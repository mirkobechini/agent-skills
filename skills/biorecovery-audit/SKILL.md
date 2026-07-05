---
name: biorecovery-audit
version: 1.0.0
author: Mirko Bechini
description: "Audit sleep, hydration, and nutrition metrics to generate a recovery score that gates training intensity and prevents overtraining. Use when assessing if an athlete is sufficiently recovered to train at planned intensity, or to adjust workouts based on current recovery state."
argument-hint: "[recovery_audit] [--sleep HOURS] [--hydration LITERS] [--fatigue 1-10] [--nutrition STATUS]"
user-invocable: true
applyTo: "**"
---

# Biorecovery Audit

## When to Use

Activate this skill when the user:

- Needs to audit recovery metrics before scheduling an intensive training session
- Wants to assess whether current sleep, hydration, and nutrition support planned workout intensity
- Reports extreme fatigue, poor sleep, or dehydration and needs workout adjustments
- Requires a data-driven recovery score to determine safe RPE (Rate of Perceived Exertion) ceiling
- Has tracked sleep hours, hydration, and nutrition and wants actionable optimization advice

## Output

This skill produces:

1. **Recovery Score (0.7x–1.2x multiplier)** — A dynamic recovery multiplier that adjusts training volume recommendations. Stored in `session.persistent_storage.recovery_score` for integration with workout scheduler.
2. **Training Adjustment Report** — Text-based guidance indicating safe RPE ceiling, volume reduction percentage, and actionable optimization steps for sleep, hydration, and nutrition.
3. **Critical Safety Flags** (optional) — Warnings for extreme conditions: severe dehydration (<1.5L on training days), critical sleep debt (<5.5 hours), or fatigue ≥8/10 that may prevent training entirely.

## Prerequisites

### Required

- **Python** 3.8+ — Language runtime for executing recovery calculation scripts
- **pandas** 1.3+ — Data manipulation and numeric calculations
- **numpy** 1.19+ — Numerical computations for recovery index formulas
- **pytest** 6.0+ — Testing framework (optional but recommended)

### Installation

**macOS**:

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and dependencies
brew install python3
pip3 install pandas numpy pytest
```

**Ubuntu/Debian**:

```bash
sudo apt update
sudo apt install python3 python3-pip
pip3 install pandas numpy pytest
```

**Windows** (via Python.org):

```bash
# Download and install Python from https://www.python.org/downloads/
# Then in CMD or PowerShell:
pip install pandas numpy pytest
```

### Verify

```bash
python --version  # Should show Python 3.8 or higher
python -c "import pandas; import numpy; print('✅ pandas and numpy installed')"
```

Expected output:

```
Python 3.8.x (or higher)
✅ pandas and numpy installed
```

## Procedure

### Step 1: Gather Recovery Input Data

Collect the user's current sleep, hydration, nutrition, and fatigue metrics. These four data points form the basis of the recovery audit.

```bash
python scripts/collect_recovery_metrics.py --sleep 6.5 --hydration 2.1 --nutrition maintenance --fatigue 5
```

**Output**:

```
✅ Recovery metrics collected:
  • Sleep: 6.5 hours (quality: restful)
  • Hydration: 2.1 liters
  • Nutrition Status: maintenance
  • Perceived Fatigue: 5/10
```

### Step 2: Calculate Recovery Score

Compute the recovery multiplier (0.7x–1.2x) based on sleep quality, hours, hydration level, and fatigue. Cross-reference with nutritional status to adjust.

```bash
python scripts/calculate_recovery_score.py --input metrics.json
```

**Output**:

```
📊 Recovery Index Calculated:
  • Base Sleep Multiplier: 0.95x (6.5h, restful quality)
  • Hydration Multiplier: 1.0x (2.1L ✓ optimal)
  • Fatigue Adjustment: -0.05 (5/10 slight fatigue)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RECOVERY SCORE: 0.90x

  ⚠️  Training Recommendation:
    → RPE Ceiling: 7/10 (moderate intensity)
    → Volume Reduction: 10% below target
```

### Step 3: Generate Training Adjustment Report

Produce actionable guidance for workout modification and recovery optimization. Includes safety flags if critical thresholds are breached.

```bash
python scripts/generate_adjustment_report.py --recovery-score 0.90 --output report.txt
```

**Output**:

```
📋 Training Adjustment Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recovery Status: MODERATE (0.90x multiplier)

Today's Training Adjustments:
  • Reduce total working sets by 10%
  • Max RPE: 7/10 (avoid near-max efforts)
  • Extend warm-up to 15 min (neural prep)
  • Add extra mobility work: 5–10 min

Recovery Optimization:
  ✓ Sleep: On track. Maintain 7–8 hour target.
  ⚠ Hydration: Adequate (2.1L). Aim for 2.5L+ on training days.
  ✓ Nutrition: Maintenance calories maintained.

Next Check: Tomorrow morning (sleep tracking)
```

## Reference

| Command                         | Purpose                                                             | Input                                                                                                 | Output                                                            |
| ------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `collect_recovery_metrics.py`   | Parse user input (sleep, hydration, nutrition, fatigue)             | `--sleep HOURS --hydration LITERS --nutrition [surplus/deficit/maintenance/untracked] --fatigue 1-10` | JSON file with validated metrics                                  |
| `calculate_recovery_score.py`   | Compute recovery multiplier (0.7x–1.2x) based on metrics            | `--input metrics.json`                                                                                | Recovery score, multiplier, RPE ceiling                           |
| `generate_adjustment_report.py` | Create training adjustment + optimization guidance                  | `--recovery-score VALUE --output report.txt`                                                          | Human-readable adjustment report                                  |
| `check_critical_flags.py`       | Detect safety violations (sleep debt, dehydration, extreme fatigue) | `--input metrics.json`                                                                                | Safety warnings (if any)                                          |
| `persistent_storage_write.py`   | Store recovery score in session state for workout scheduler         | `--recovery-score VALUE --session-id ID`                                                              | Write confirmation to `session.persistent_storage.recovery_score` |

## Examples

### Example 1: Athlete Checks Recovery Before Morning Workout

**User Request**: "I slept 7 hours, drank 2.2 liters today, feeling energized. Should I do my planned intense leg day?"

```bash
python scripts/collect_recovery_metrics.py --sleep 7 --hydration 2.2 --nutrition surplus --fatigue 2 && \
python scripts/calculate_recovery_score.py --input metrics.json
```

**Result**:

- Recovery Score: **1.1x** (excellent recovery)
- RPE Ceiling: **9/10** (intense training approved)
- Training Adjustment: **No reduction needed** — full volume ahead
- Recommendation: All-clear for planned leg day; consider adding accessory work

---

### Example 2: Athlete is Fatigued with Poor Sleep; Workout Scheduler Must Adapt

**User Request**: "I only slept 4.5 hours (poor quality), drank 1.2L (training day), feeling very tired at 8/10 fatigue. I have a scheduled high-intensity session. Can I do it?"

```bash
python scripts/collect_recovery_metrics.py --sleep 4.5 --hydration 1.2 --nutrition deficit --fatigue 8 && \
python scripts/calculate_recovery_score.py --input metrics.json && \
python scripts/check_critical_flags.py --input metrics.json
```

**Result**:

- Recovery Score: **0.65x** (CRITICAL DEFICIT)
- RPE Ceiling: **5/10** (low intensity only)
- Training Adjustment: **Reduce volume by 35%** — cut working sets from 30 to ~20
- Safety Flags:
  - ⛔ **Sleep Debt Critical**: <5.5 hours detected. Overtraining risk HIGH.
  - ⛔ **Dehydration Warning**: 1.2L on training day. Risk of cramping and tendon injury.
- Recommendation: Reschedule high-intensity. Do active recovery or rest day instead. Retest after sleep improvement.

## Notes & Tips

- **Performance**: Recovery calculations complete in <50ms, even with 5+ years of training history logged.
- **Best practice**: Run audit checks every morning before training to prevent overtraining injuries and maintain long-term adaptations.
- **Common mistake**: Users ignore yellow-flag hydration warnings (1.5–2L range). Dehydration compounds fatigue and increases injury risk exponentially.
- **Workaround**: If sleep data is unavailable, use fatigue perception + hydration as proxy. Recovery score will be conservative (safer).

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pandas'"

**Cause**: Required Python dependencies are not installed in your environment.

**Solution**:

```bash
# Verify Python version
python --version  # Must be 3.8+

# Install dependencies
pip install -r scripts/requirements.txt

# Verify installation
python -c "import pandas; import numpy; print('✅ Packages installed successfully')"
```

### Issue: "ValueError: Invalid nutrition status. Expected: surplus/deficit/maintenance/untracked"

**Cause**: The `--nutrition` flag received an unrecognized value.

**Solution**:

```bash
# Valid nutrition statuses are:
# - surplus (eating above maintenance for gains)
# - deficit (eating below maintenance for fat loss)
# - maintenance (maintenance calories)
# - untracked (nutrition not tracked today)

# Correct usage:
python scripts/collect_recovery_metrics.py --sleep 7 --hydration 2.0 --nutrition maintenance --fatigue 4
```

### Issue: "JSON file not found: metrics.json"

**Cause**: The metrics collection script hasn't been run yet, or the file path is incorrect.

**Solution**:

```bash
# Always run collection BEFORE calculation
python scripts/collect_recovery_metrics.py --sleep 7 --hydration 2.0 --nutrition maintenance --fatigue 4

# Verify the file was created
ls -la metrics.json  # macOS/Linux
dir metrics.json     # Windows

# Then run calculation
python scripts/calculate_recovery_score.py --input metrics.json
```

## FAQ

**Q: What does a 0.7x recovery score mean for my workout?**  
A: A 0.7x score means your body is at ~70% capacity to handle training stress. If your planned workout is 30 sets, cut it to ~21 sets. Prioritize recovery over training intensity that day.

**Q: Can I override the recovery score and train hard anyway?**  
A: Technically yes, but not recommended. Ignoring critical recovery flags (sleep <5.5h, fatigue ≥8/10) significantly increases overtraining injuries. The score is a data-driven guardian, not a suggestion.

**Q: How often should I run recovery audits?**  
A: Ideally every morning before training. At minimum, run it before high-intensity sessions. Some athletes check it weekly. More frequent checks give better prevention of accumulated fatigue.

**Q: What if I don't track sleep/hydration exactly?**  
A: Use estimates. The algorithm uses ranges (e.g., "about 6.5 hours," "drank roughly 2L"). Even rough estimates are better than missing data; the score will be conservative to prevent overtraining.

**Q: Does the recovery score account for previous day's workout stress?**  
A: The current version uses only today's sleep, hydration, nutrition, and fatigue. Future versions will integrate workout volume history and cumulative fatigue over 7–14 days.

---

## File Structure

```
skill-name/
├── SKILL.md                    # This documentation file
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration (for tests)
├── .gitignore                  # Git ignore rules
├── scripts/
│   ├── __init__.py             # Makes scripts/ importable as a package
│   ├── main_script.py          # Primary script
│   ├── helper_script.py        # Supporting script
│   └── ...
├── tests/
│   ├── __init__.py             # Makes tests/ importable as a package
│   ├── test_main.py            # Unit tests for main script
│   ├── test_helpers.py         # Unit tests for helpers
│   └── ...
├── assets/                     # Static resources, templates, data files
│   └── ...
└── references/                 # External documentation links
    └── ...
```

---

**Last Updated**: 2026-07-05  
**Status**: Active  
**Maintainer**: Mirko Bechini
