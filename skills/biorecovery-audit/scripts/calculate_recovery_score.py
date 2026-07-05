#!/usr/bin/env python3
"""
Calculate recovery score based on collected metrics.
Produces 0.7x–1.2x multiplier to gate training intensity.
"""

import argparse
import json
import sys
from pathlib import Path


def calculate_recovery_score(metrics: dict) -> dict:
    """
    Compute recovery multiplier (0.7x–1.2x) from metrics.
    
    Formula:
    - Base: 1.0x
    - Sleep adjustment: ±0.15x (restful +0.15, interrupted 0, poor -0.15)
    - Hydration adjustment: ±0.1x (optimal 0, low -0.1)
    - Fatigue adjustment: -0.01x per fatigue point above 5
    - Nutrition boost: +0.05x if surplus, -0.1x if deficit
    - Clamp: 0.7x–1.2x
    """
    
    score = 1.0
    
    # Sleep contribution
    sleep_quality = metrics["sleep"]["quality"]
    if sleep_quality == "restful":
        score += 0.15
    elif sleep_quality == "interrupted":
        score += 0
    elif sleep_quality == "poor":
        score -= 0.15
    
    # Hydration contribution
    hydration_liters = metrics["hydration"]
    if hydration_liters >= 2.0:
        score += 0.05  # Optimal
    elif hydration_liters >= 1.5:
        score += 0  # Adequate
    else:
        score -= 0.1  # Low (dehydration risk)
    
    # Fatigue contribution
    fatigue = metrics["perceived_fatigue_level"]
    if fatigue > 5:
        score -= (fatigue - 5) * 0.02
    elif fatigue <= 3:
        score += 0.05
    
    # Nutrition contribution
    nutrition = metrics["nutrition_status"]
    if nutrition == "surplus":
        score += 0.05
    elif nutrition == "deficit":
        score -= 0.1
    elif nutrition == "untracked":
        score -= 0.02  # Conservative penalty
    
    # Clamp to 0.7x–1.2x range
    score = max(0.7, min(1.2, score))
    
    # Determine RPE ceiling
    rpe_ceiling = int(10 * score)
    rpe_ceiling = max(5, min(10, rpe_ceiling))
    
    # Calculate volume reduction percentage
    volume_reduction = max(0, int((1.0 - score) * 100))
    
    return {
        "recovery_score": round(score, 2),
        "rpe_ceiling": rpe_ceiling,
        "volume_reduction_percent": volume_reduction,
        "sleep_quality": sleep_quality,
        "hydration_liters": hydration_liters,
        "fatigue_level": fatigue,
        "nutrition_status": nutrition,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate recovery score from collected metrics"
    )
    parser.add_argument("--input", type=str, default="metrics.json", help="Input metrics JSON")
    parser.add_argument("--output", type=str, default="recovery_score.json", help="Output JSON")
    
    args = parser.parse_args()
    
    try:
        # Load metrics
        input_path = Path(args.input)
        with open(input_path, "r") as f:
            metrics = json.load(f)
        
        # Calculate score
        result = calculate_recovery_score(metrics)
        
        # Save result
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        
        # Print summary
        print("📊 Recovery Index Calculated:")
        print(f"  • Base Sleep Multiplier: {result['recovery_score']}x ({metrics['sleep']['quality']} quality)")
        print(f"  • Hydration Multiplier: {'1.0x' if result['hydration_liters'] >= 2.0 else '0.9x'} ({result['hydration_liters']}L)")
        print(f"  • Fatigue Adjustment: {'-0.02' if result['fatigue_level'] > 5 else '+0.05'} ({result['fatigue_level']}/10)")
        print(f"  {'━' * 40}")
        print(f"  RECOVERY SCORE: {result['recovery_score']}x")
        print(f"\n  ⚠️  Training Recommendation:")
        print(f"    → RPE Ceiling: {result['rpe_ceiling']}/10")
        print(f"    → Volume Reduction: {result['volume_reduction_percent']}% below target")
        print(f"\n📁 Saved to: {output_path}")
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
