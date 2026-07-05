#!/usr/bin/env python3
"""
Generate human-readable training adjustment report from recovery score.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def generate_report(recovery_score: float, metrics: dict) -> str:
    """Generate text report with training adjustments."""
    
    # Determine recovery status
    if recovery_score >= 1.1:
        status = "EXCELLENT"
        emoji = "🟢"
    elif recovery_score >= 0.9:
        status = "GOOD"
        emoji = "🟡"
    elif recovery_score >= 0.8:
        status = "MODERATE"
        emoji = "🟠"
    else:
        status = "CRITICAL"
        emoji = "🔴"
    
    # Build report
    report = f"""📋 Training Adjustment Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Recovery Status: {emoji} {status} ({recovery_score}x multiplier)

Today's Training Adjustments:
"""
    
    # Volume adjustment
    volume_reduction = max(0, int((1.0 - recovery_score) * 100))
    if volume_reduction == 0:
        report += "  • No reduction needed — full volume ahead\n"
    else:
        report += f"  • Reduce total working sets by {volume_reduction}%\n"
    
    # RPE ceiling
    rpe_ceiling = int(10 * recovery_score)
    rpe_ceiling = max(5, min(10, rpe_ceiling))
    report += f"  • Max RPE: {rpe_ceiling}/10 (avoid near-max efforts)\n"
    
    if recovery_score < 0.9:
        report += "  • Extend warm-up to 15 min (neural prep)\n"
        report += "  • Add extra mobility work: 5–10 min\n"
    
    # Recovery optimization
    report += "\nRecovery Optimization:\n"
    
    sleep_quality = metrics["sleep"]["quality"]
    if sleep_quality == "restful":
        report += f"  ✓ Sleep: On track. Maintain 7–8 hour target.\n"
    elif sleep_quality == "interrupted":
        report += f"  ⚠ Sleep: Interrupted (4–6h). Prioritize sleep tonight.\n"
    else:
        report += f"  ❌ Sleep: Critical debt (<5.5h). REDUCE TRAINING VOLUME.\n"
    
    hydration = metrics["hydration"]
    if hydration >= 2.5:
        report += f"  ✓ Hydration: Excellent ({hydration}L). Maintain.\n"
    elif hydration >= 1.5:
        report += f"  ⚠ Hydration: Adequate ({hydration}L). Aim for 2.5L+ on training days.\n"
    else:
        report += f"  ❌ Hydration: LOW ({hydration}L). Risk of cramping and tendon injury.\n"
    
    nutrition = metrics["nutrition_status"]
    nutrition_text = {
        "surplus": "Positive energy balance — supports hypertrophy",
        "deficit": "Energy deficit — monitor fatigue closely",
        "maintenance": "Maintenance calories maintained",
        "untracked": "Nutrition not tracked — estimate conservatively"
    }
    report += f"  {nutrition_text.get(nutrition, 'Unknown status')}\n"
    
    report += f"\nNext Check: Tomorrow morning (sleep tracking)\n"
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate training adjustment report"
    )
    parser.add_argument("--recovery-score", type=float, required=True, help="Recovery score (0.7–1.2)")
    parser.add_argument("--input", type=str, default="metrics.json", help="Input metrics JSON")
    parser.add_argument("--output", type=str, default="adjustment_report.txt", help="Output report file")
    
    args = parser.parse_args()
    
    try:
        # Load metrics
        input_path = Path(args.input)
        with open(input_path, "r") as f:
            metrics = json.load(f)
        
        # Generate report
        report = generate_report(args.recovery_score, metrics)
        
        # Save report
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            f.write(report)
        
        # Print to console
        print(report)
        print(f"\n📁 Report saved to: {output_path}")
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
