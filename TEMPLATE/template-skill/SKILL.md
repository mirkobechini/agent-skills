---
name: template-skill
version: 1.0.0
author: [Your Name]
description: "[2-3 sentence description of what this skill does and the main problem it solves]"
argument-hint: "[brief command syntax hint, if applicable]"
user-invocable: true
applyTo: "**"
---

# Example Skill

## When to Use

Activate this skill when the user:

- [Specific user action 1]
- [Specific user action 2]
- [Specific user action 3]
- [Specific user action 4]

## Output

This skill produces:

1. **[Output type 1]** — [Concrete description: what is created, format, location]
2. **[Output type 2]** — [Concrete description]
3. **[Output type 3]** (optional) — [Concrete description]

## Prerequisites

### Required

- **[Tool/Language 1]** version [X.Y]+ — [Purpose]
- **[Tool/Language 2]** — [Purpose]
- **[Credential/API key]** — [Where to obtain]

### Installation

**macOS**:

```bash
[installation command]
```

**Ubuntu/Debian**:

```bash
[installation command]
```

**Windows**:

```bash
[installation command]
```

### Verify

```bash
[verification command]
```

Expected output:

```
[what success looks like]
```

## Procedure

### Step 1: [Descriptive Title]

[What happens in this step. 1-2 sentences explaining the goal.]

```bash
[Real, testable command]
```

**Output**:

```
[Exact expected output or result]
```

### Step 2: [Descriptive Title]

[What happens in this step. 1-2 sentences.]

```bash
[Real, testable command with options]
```

**Options**:

- `--flag` — [What this flag does]
- `--other-flag` — [What this flag does]

**Output**:

```
[Exact expected output or result]
```

### Step 3: [Descriptive Title]

[Continue with additional steps as needed]

## Reference

| Command | Purpose        | Input          | Output          |
| ------- | -------------- | -------------- | --------------- |
| `[cmd]` | [What it does] | [Input format] | [Output format] |
| `[cmd]` | [What it does] | [Input format] | [Output format] |

## Examples

### Example 1: [Common/Basic Use Case]

**User Request**: "[What the user asks for]"

```bash
[Real, executable command]
```

**Result**:

- [Concrete outcome 1]
- [Concrete outcome 2]
- [Concrete outcome 3]

---

### Example 2: [Advanced/Complex Use Case]

**User Request**: "[What the user asks for]"

```bash
[Real, executable command with multiple options]
```

**Result**:

- [Concrete outcome 1]
- [Concrete outcome 2]

## Notes & Tips

- **Performance**: [Relevant performance considerations]
- **Best practice**: [Recommended approach or pattern]
- **Common mistake**: [What users often do wrong and how to avoid it]
- **Workaround**: [Alternative approach when main method doesn't work]

## Troubleshooting

### Issue: [Specific, Common Error]

**Cause**: [Why this happens]

**Solution**:

```bash
[Step 1 command]
[Step 2 command]
```

### Issue: [Another Specific Error]

**Cause**: [Why this happens]

**Solution**: [Step-by-step fix]

### Issue: [Third Common Error]

**Cause**: [Why this happens]

**Solution**: [How to resolve]

## FAQ

**Q: [Common question 1]**  
A: [Concrete answer]

**Q: [Common question 2]**  
A: [Concrete answer]

**Q: [Common question 3]**  
A: [Concrete answer]

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

**Last Updated**: YYYY-MM-DD  
**Status**: [Active | In Development | Deprecated]  
**Maintainer**: [Your name]
