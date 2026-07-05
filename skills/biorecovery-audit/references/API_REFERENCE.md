# Biorecovery Audit API Reference

## Input Parameters

### `collect_recovery_metrics.py`

**Arguments:**

- `--sleep HOURS` (float, 0–24): Sleep hours. Infers quality automatically (restful: 7+h, interrupted: 5.5–7h, poor: <5.5h)
- `--hydration LITERS` (float, 0–20): Water drunk **so far today** in liters
- `--nutrition-status {seguita-bene|sgarrata-leggera|sgarrata-forte|on-target}` (optional): Descriptive diet adherence
- `--nutrition-target CALORIES` (optional): Target calories for today
- `--nutrition-consumed CALORIES` (optional): Calories consumed so far today
- `--fatigue LEVEL` (int, 1–10): Perceived fatigue (1=fresh, 10=exhausted)
- `--output FILE` (str): Output JSON filename (default: `metrics.json`)

**Nutrition Modes:**

- **Descriptive**: Use `--nutrition-status "seguita-bene"` (diet followed well) or similar
- **Numeric**: Use `--nutrition-target 2500 --nutrition-consumed 2100` (calorie tracking)
- **Mixed**: Can use both simultaneously

**Output Format (JSON) — Descriptive Mode:**

```json
{
  "sleep": {
    "hours": 6.5,
    "quality": "interrupted"
  },
  "hydration": 2.1,
  "nutrition": {
    "status": "seguita-bene",
    "normalized": "adherence:95"
  },
  "perceived_fatigue_level": 5
}
```

**Output Format (JSON) — Numeric Mode:**

```json
{
  "sleep": {
    "hours": 7.5,
    "quality": "restful"
  },
  "hydration": 2.3,
  "nutrition": {
    "numeric": {
      "target": 2500,
      "consumed": 2100,
      "delta": -400,
      "adherence_percent": 84.0
    },
    "normalized": "adherence:85"
  },
  "perceived_fatigue_level": 3
}
```

---

## Recovery Score Calculation

### `calculate_recovery_score.py`

**Input:** `metrics.json` (from collect_recovery_metrics)

**Algorithm:**

- Base: 1.0x
- Sleep: +0.15x (restful), +0x (interrupted), -0.15x (poor)
- Hydration: +0.05x (≥2.0L), +0x (1.5–2.0L), -0.1x (<1.5L)
- Fatigue: -0.02x per level above 5 (e.g., fatigue 8 → -0.06x)
- **Nutrition (Descriptive)**: +0.05x (seguita-bene), 0x (on-target), -0.05x (sgarrata-leggera), -0.1x (sgarrata-forte)
- **Nutrition (Numeric)**: +0.05x (≥95% adherence), 0x (85–95%), -0.05x (70–85%), -0.1x (<70%)
- **Clamp:** 0.7x–1.2x range

**Output Format (JSON):**

```json
{
  "recovery_score": 0.9,
  "rpe_ceiling": 7,
  "volume_reduction_percent": 10,
  "sleep_quality": "restful",
  "hydration_liters": 2.1,
  "fatigue_level": 5,
  "nutrition_status": "maintenance"
}
```

---

## Critical Flags

### `check_critical_flags.py`

**Critical Thresholds:**

- Sleep < 5.5h → **SLEEP DEBT CRITICAL**
- Hydration < 1.5L (training day) → **DEHYDRATION WARNING**
- Hydration < 1.0L → **SEVERE DEHYDRATION** (cancel training)
- Fatigue ≥ 9 → **EXTREME FATIGUE**
- Fatigue 8–9 → **HIGH FATIGUE**
- Fatigue ≥ 7 + nutrition deficit → **COMBO RISK**

**Output Format (JSON):**

```json
{
  "critical_issues": [
    "⛔ DEHYDRATION WARNING: 1.2L on training day. Risk of cramping and tendon injury."
  ],
  "warnings": ["⚠️  Elevated Fatigue: 7/10. Consider lighter workout."],
  "clearance": false
}
```

---

## Training Adjustments

### `generate_adjustment_report.py`

**Output:** Human-readable text report with:

- Recovery status (EXCELLENT | GOOD | MODERATE | CRITICAL)
- Volume reduction percentage
- RPE ceiling recommendation
- Sleep, hydration, nutrition guidance
- Next check time

---

## Integration Layer

### `persistent_storage_write.py`

Writes recovery score to `session.persistent_storage.recovery_score` for integration with workout scheduler.

**Output Format (JSON):**

```json
{
  "timestamp": "2026-07-05T14:30:00",
  "recovery_score": 0.9,
  "session_id": "default",
  "storage_location": "session.persistent_storage.recovery_score"
}
```

---

## Typical Workflow

```
1. collect_recovery_metrics.py (user input)
   ↓ outputs: metrics.json
2. calculate_recovery_score.py (metric processing)
   ↓ outputs: recovery_score.json
3. check_critical_flags.py (safety checks)
   ↓ outputs: critical_flags.json
4. generate_adjustment_report.py (user guidance)
   ↓ outputs: adjustment_report.txt
5. persistent_storage_write.py (scheduler integration)
   ↓ outputs: session_storage.json
```

---

## Error Handling

### Exit Codes

- `0`: Success (or success with warnings)
- `1`: Failure (critical issue detected OR file error)

### Common Errors

- `ValueError: Invalid nutrition status` → Use valid choices: surplus/deficit/maintenance/untracked
- `ValueError: Fatigue level must be 1-10` → Clamp to 1–10 range
- `FileNotFoundError: metrics.json` → Run collection step first
