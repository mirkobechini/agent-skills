# Agent Skills

A collection of reusable, on-demand skills compatible with any agent that supports the **SKILL.md** format — including VS Code Copilot, Claude, Cline, and other AI coding agents.

## Skills

| Skill                                                              | Description                                                                                                                                                  |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`biorecovery-audit`](./skills/biorecovery-audit/SKILL.md)         | Recovery audit system for preventing overtraining: tracks sleep, hydration, nutrition, and fatigue to compute recovery multipliers (0.7x–1.2x) for training. |
| [`pdf-workspace-manager`](./skills/pdf-workspace-manager/SKILL.md) | Full PDF management: browser preview, merge, split, reorder, remove pages, text editing, and metadata editing. Powered by PyMuPDF and pypdf.                 |
| [`pr-summary-handoff`](./skills/pr-summary-handoff/SKILL.md)       | Guides the developer through creating a Pull Request on GitHub after completing a feature or hotfix branch, generating the PR link and a summary of changes. |

## Usage

Skills are loaded automatically by the agent when the conversation matches their `description`. You can also invoke them manually by typing `/` in chat and selecting the skill name.

## Structure

Each skill lives in its own folder under `skills/`:

```
skills/<skill-name>/
├── SKILL.md           # Required — skill definition and procedures
├── scripts/           # Executable scripts
├── references/        # Documentation loaded on demand
└── assets/            # Templates, boilerplate, config files
```

## Creating a New Skill

Use the template in `TEMPLATE/` to create professional skills quickly:

```bash
# 1. Copy the template skeleton
cd skills/
cp -r ../TEMPLATE/template-skill/ my-new-skill/
cd my-new-skill/

# 2. Edit SKILL.md with your skill's content
# 3. Add code to scripts/ folder
# 4. Test everything locally
```

**Complete guide**: See `TEMPLATE/HOW-TO-CREATE-A-SKILL.md` for step-by-step instructions on:

- Filling in the YAML frontmatter
- Writing each section (When to Use, Output, Prerequisites, Procedure, Examples, etc.)
- Testing and verification checklist
- Common mistakes to avoid

## Requirements

- VS Code with Copilot agent features enabled
- Python 3.8+ (for `pdf-workspace-manager` scripts)
- Dependencies are listed in each skill's prerequisites section
