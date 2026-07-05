#!/usr/bin/env python3
"""
Check for critical safety flags (sleep debt, dehydration, extreme fatigue).
"""

import argparse
import json
import sys
from pathlib import Path


def check_critical_flags(metrics: dict) -> dict:
    """
    Detect safety violations.
    
    Returns:
        dict with flags: critical_issues (list), warnings (list), clearance (bool)
    """
    
    flags = {
        "critical_issues": [],
        "warnings": [],
        "clearance": True,
    }
    
    # Check sleep debt
    sleep_hours = metrics["sleep"]["hours"]
    if sleep_hours < 5.5:
        flags["critical_issues"].append(
            f"⛔ SLEEP DEBT CRITICAL: {sleep_hours}h detected. Overtraining risk HIGH."
        )
        flags["clearance"] = False
    elif sleep_hours < 6.5:
        flags["warnings"].append(
            f"⚠️  Sleep Low: {sleep_hours}h (target: 7–8h). Monitor fatigue."
        )
    
    # Check dehydration
    hydration = metrics["hydration"]
    if hydration < 1.0:
        flags["critical_issues"].append(
            f"⛔ SEVERE DEHYDRATION: {hydration}L detected. Cancel training session."
        )
        flags["clearance"] = False
    elif hydration < 1.5:
        flags["critical_issues"].append(
            f"⛔ DEHYDRATION WARNING: {hydration}L on training day. Risk of cramping and tendon injury."
        )
        flags["clearance"] = False
    elif hydration < 2.0:
        flags["warnings"].append(
            f"⚠️  Hydration Below Optimal: {hydration}L. Aim for 2.5L+ today."
        )
    
    # Check extreme fatigue
    fatigue = metrics["perceived_fatigue_level"]
    if fatigue >= 9:
        flags["critical_issues"].append(
            f"⛔ EXTREME FATIGUE: {fatigue}/10 reported. Overtraining imminent."
        )
        flags["clearance"] = False
    elif fatigue >= 8:
        flags["critical_issues"].append(
            f"⛔ HIGH FATIGUE: {fatigue}/10. Reduce training intensity significantly."
        )
        flags["clearance"] = False
    elif fatigue >= 7:
        flags["warnings"].append(
            f"⚠️  Elevated Fatigue: {fatigue}/10. Consider lighter workout."
        )
    
    # Check nutrition + fatigue combo
    nutrition_status = metrics.get("nutrition", {}).get("normalized", "untracked")
    if fatigue >= 7 and ("deficit" in nutrition_status or "sgarrata" in nutrition_status):
        flags["warnings"].append(
            "⚠️  Combo Risk: High fatigue + poor nutrition. Risk of hormonal dysregulation."
        )
    
    return flags


def main():
    parser = argparse.ArgumentParser(
        description="Check critical safety flags"
    )
    parser.add_argument("--input", type=str, default="metrics.json", help="Input metrics JSON")
    parser.add_argument("--output", type=str, default="critical_flags.json", help="Output JSON")
    
    args = parser.parse_args()
    
    try:
        # Load metrics
        input_path = Path(args.input)
        with open(input_path, "r") as f:
            metrics = json.load(f)
        
        # Check flags
        flags = check_critical_flags(metrics)
        
        # Save flags
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(flags, f, indent=2)
        
        # Print to console
        if flags["critical_issues"]:
            print("🚨 CRITICAL ISSUES DETECTED:")
            for issue in flags["critical_issues"]:
                print(f"  {issue}")
        
        if flags["warnings"]:
            print("\n⚠️  WARNINGS:")
            for warning in flags["warnings"]:
                print(f"  {warning}")
        
        if not flags["critical_issues"] and not flags["warnings"]:
            print("✅ No critical issues detected. Training clearance granted.")
        
        clearance_status = "🟢 CLEARED" if flags["clearance"] else "🔴 DO NOT TRAIN"
        print(f"\n{clearance_status}")
        print(f"📁 Flags saved to: {output_path}")
        
        sys.exit(0 if flags["clearance"] else 1)
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
