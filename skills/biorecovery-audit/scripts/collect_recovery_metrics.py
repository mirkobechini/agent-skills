#!/usr/bin/env python3
"""
Collect recovery metrics from user input.
Parses sleep, hydration, nutrition, and fatigue data into validated JSON.
Supports flexible nutrition input: descriptive ("seguita-bene") or numeric (calories).
"""

import argparse
import json
import sys
from pathlib import Path


def validate_sleep(sleep_hours: float) -> dict:
    """Validate sleep input and infer quality."""
    if sleep_hours < 0 or sleep_hours > 24:
        raise ValueError(f"Sleep hours must be 0-24. Got: {sleep_hours}")
    
    if sleep_hours < 5.5:
        quality = "poor"
    elif sleep_hours < 7:
        quality = "interrupted"
    else:
        quality = "restful"
    
    return {"hours": sleep_hours, "quality": quality}


def validate_hydration(hydration_liters: float) -> float:
    """Validate hydration input."""
    if hydration_liters < 0 or hydration_liters > 20:
        raise ValueError(f"Hydration must be 0-20 liters. Got: {hydration_liters}")
    return hydration_liters


def validate_nutrition(
    nutrition_status: str = None,
    nutrition_target: int = None,
    nutrition_consumed: int = None
) -> dict:
    """
    Validate nutrition input. Supports two modes:
    1. Descriptive: "seguita-bene", "sgarrata-leggera", "sgarrata-forte", "on-target"
    2. Numeric: target and consumed calories
    """
    valid_descriptive = ["seguita-bene", "sgarrata-leggera", "sgarrata-forte", "on-target"]
    
    nutrition = {}
    
    # Mode 1: Descriptive
    if nutrition_status:
        if nutrition_status not in valid_descriptive:
            raise ValueError(
                f"Nutrition status must be one of {valid_descriptive}. Got: {nutrition_status}"
            )
        nutrition["status"] = nutrition_status
        
        # Map descriptive to numeric impact
        status_map = {
            "seguita-bene": "adherence:95",
            "on-target": "adherence:90",
            "sgarrata-leggera": "adherence:70",
            "sgarrata-forte": "adherence:40",
        }
        nutrition["normalized"] = status_map.get(nutrition_status, nutrition_status)
    
    # Mode 2: Numeric (calories)
    if nutrition_target is not None and nutrition_consumed is not None:
        if nutrition_target <= 0 or nutrition_consumed < 0:
            raise ValueError(f"Calories must be positive. Target: {nutrition_target}, Consumed: {nutrition_consumed}")
        
        delta = nutrition_consumed - nutrition_target
        adherence_pct = (nutrition_consumed / nutrition_target * 100) if nutrition_target > 0 else 0
        
        nutrition["numeric"] = {
            "target": nutrition_target,
            "consumed": nutrition_consumed,
            "delta": delta,
            "adherence_percent": round(adherence_pct, 1)
        }
        
        # Normalize to status string
        if abs(delta) <= 100:
            nutrition["normalized"] = "adherence:90"
        elif delta > 100 and delta <= 300:
            nutrition["normalized"] = "surplus"
        elif delta < -100 and delta >= -300:
            nutrition["normalized"] = "deficit"
        elif abs(delta) > 300:
            nutrition["normalized"] = "sgarrata-forte" if delta < 0 else "surplus:strong"
    
    # Default if nothing provided
    if not nutrition:
        nutrition["normalized"] = "untracked"
    
    return nutrition


def validate_fatigue(fatigue_level: int) -> int:
    """Validate fatigue perception level."""
    if fatigue_level < 1 or fatigue_level > 10:
        raise ValueError(f"Fatigue level must be 1-10. Got: {fatigue_level}")
    return fatigue_level


def collect_metrics(
    sleep: float,
    hydration: float,
    fatigue: int,
    nutrition_status: str = None,
    nutrition_target: int = None,
    nutrition_consumed: int = None
) -> dict:
    """Collect and validate all recovery metrics."""
    
    nutrition = validate_nutrition(nutrition_status, nutrition_target, nutrition_consumed)
    
    metrics = {
        "sleep": validate_sleep(sleep),
        "hydration": validate_hydration(hydration),
        "nutrition": nutrition,
        "perceived_fatigue_level": validate_fatigue(fatigue),
    }
    return metrics


def main():
    parser = argparse.ArgumentParser(
        description="Collect recovery metrics for biorecovery audit"
    )
    parser.add_argument("--sleep", type=float, default=7.0, help="Sleep hours (0-24)")
    parser.add_argument(
        "--hydration",
        type=float,
        default=2.0,
        help="Water drunk so far today in liters (0-20)"
    )
    parser.add_argument("--fatigue", type=int, default=5, help="Fatigue level (1-10)")
    
    # Nutrition: descriptive mode
    parser.add_argument(
        "--nutrition-status",
        type=str,
        choices=["seguita-bene", "sgarrata-leggera", "sgarrata-forte", "on-target"],
        help="Nutrition adherence (descriptive mode)"
    )
    
    # Nutrition: numeric mode
    parser.add_argument(
        "--nutrition-target",
        type=int,
        help="Target calories for today (numeric mode)"
    )
    parser.add_argument(
        "--nutrition-consumed",
        type=int,
        help="Calories consumed so far today (numeric mode)"
    )
    
    parser.add_argument("--output", type=str, default="metrics.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    try:
        metrics = collect_metrics(
            sleep=args.sleep,
            hydration=args.hydration,
            fatigue=args.fatigue,
            nutrition_status=args.nutrition_status,
            nutrition_target=args.nutrition_target,
            nutrition_consumed=args.nutrition_consumed,
        )
        
        # Write to JSON
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(metrics, f, indent=2)
        
        # Print summary
        print("✅ Recovery metrics collected:")
        print(f"  • Sleep: {metrics['sleep']['hours']}h ({metrics['sleep']['quality']})")
        print(f"  • Hydration (so far today): {metrics['hydration']}L")
        print(f"  • Fatigue: {metrics['perceived_fatigue_level']}/10")
        
        # Nutrition summary
        nutrition = metrics["nutrition"]
        if "numeric" in nutrition:
            num = nutrition["numeric"]
            print(f"  • Nutrition: {num['consumed']}/{num['target']} cal ({num['adherence_percent']}%, delta: {num['delta']:+d})")
        else:
            print(f"  • Nutrition: {nutrition.get('status', 'untracked')}")
        
        print(f"\n📁 Saved to: {output_path}")
        
    except (ValueError, IOError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
