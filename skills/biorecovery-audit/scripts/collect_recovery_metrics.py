#!/usr/bin/env python3
"""
Collect recovery metrics from user input.
Parses sleep, hydration, nutrition, and fatigue data into validated JSON.
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


def validate_nutrition(nutrition_status: str) -> str:
    """Validate nutrition status."""
    valid = ["surplus", "deficit", "maintenance", "untracked"]
    if nutrition_status not in valid:
        raise ValueError(f"Nutrition status must be one of {valid}. Got: {nutrition_status}")
    return nutrition_status


def validate_fatigue(fatigue_level: int) -> int:
    """Validate fatigue perception level."""
    if fatigue_level < 1 or fatigue_level > 10:
        raise ValueError(f"Fatigue level must be 1-10. Got: {fatigue_level}")
    return fatigue_level


def collect_metrics(sleep: float, hydration: float, nutrition: str, fatigue: int) -> dict:
    """Collect and validate all recovery metrics."""
    metrics = {
        "sleep": validate_sleep(sleep),
        "hydration": validate_hydration(hydration),
        "nutrition_status": validate_nutrition(nutrition),
        "perceived_fatigue_level": validate_fatigue(fatigue),
    }
    return metrics


def main():
    parser = argparse.ArgumentParser(
        description="Collect recovery metrics for biorecovery audit"
    )
    parser.add_argument("--sleep", type=float, default=7.0, help="Sleep hours (0-24)")
    parser.add_argument("--hydration", type=float, default=2.0, help="Hydration in liters (0-20)")
    parser.add_argument(
        "--nutrition",
        type=str,
        default="maintenance",
        choices=["surplus", "deficit", "maintenance", "untracked"],
        help="Nutrition status"
    )
    parser.add_argument("--fatigue", type=int, default=5, help="Fatigue level (1-10)")
    parser.add_argument("--output", type=str, default="metrics.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    try:
        metrics = collect_metrics(args.sleep, args.hydration, args.nutrition, args.fatigue)
        
        # Write to JSON
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(metrics, f, indent=2)
        
        # Print summary
        print("✅ Recovery metrics collected:")
        print(f"  • Sleep: {metrics['sleep']['hours']} hours ({metrics['sleep']['quality']})")
        print(f"  • Hydration: {metrics['hydration']} liters")
        print(f"  • Nutrition Status: {metrics['nutrition_status']}")
        print(f"  • Perceived Fatigue: {metrics['perceived_fatigue_level']}/10")
        print(f"\n📁 Saved to: {output_path}")
        
    except (ValueError, IOError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
