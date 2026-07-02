# Agent Skills

A collection of reusable, on-demand skills compatible with any agent that supports the **SKILL.md** format — including VS Code Copilot, Claude, Cline, and other AI coding agents.

## Skills

| Skill                                                              | Description                                                                                                                                                  |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
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

## Requirements

- VS Code with Copilot agent features enabled
- Python 3.8+ (for `pdf-workspace-manager` scripts)
- Dependencies are listed in each skill's prerequisites section
