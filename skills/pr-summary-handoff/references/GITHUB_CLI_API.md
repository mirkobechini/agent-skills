# GitHub CLI Reference

## Purpose

GitHub CLI (`gh`) is a command-line tool for GitHub that allows you to work with GitHub directly from your terminal without having to use a web browser.

## Installation

### Windows

```bash
winget install --id GitHub.cli
# or with Chocolatey:
choco install gh
```

### macOS

```bash
brew install gh
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
sudo apt-add-repository https://cli.github.com/packages
sudo apt update
sudo apt install gh
```

## Authentication

Before using `gh`, authenticate with GitHub:

```bash
gh auth login
# Follow the prompts to choose protocol (HTTPS/SSH) and authenticate
gh auth status  # Verify authentication
```

## Common Commands for PR Management

### Create a Pull Request

```bash
# Auto-fill PR with commit messages
gh pr create --base <TARGET_BRANCH> --fill

# Create with custom title and body
gh pr create --base <TARGET_BRANCH> --title "PR Title" --body "PR Description"

# Create as draft
gh pr create --base <TARGET_BRANCH> --draft --fill

# Create and assign
gh pr create --base <TARGET_BRANCH> --assignee @me --fill

# Create with reviewers
gh pr create --base <TARGET_BRANCH> --reviewer user1,user2 --fill

# Add labels
gh pr create --base <TARGET_BRANCH> --label "bug,frontend" --fill
```

### List Pull Requests

```bash
# List PRs in the repo
gh pr list

# List PRs for a specific base branch
gh pr list --base main

# List PRs assigned to you
gh pr list --assignee @me
```

### View Pull Request Details

```bash
# View specific PR
gh pr view <PR_NUMBER>

# View PR with detailed info
gh pr view <PR_NUMBER> --json title,body,state
```

### Merge Pull Request

```bash
# Merge PR
gh pr merge <PR_NUMBER>

# Merge and delete branch
gh pr merge <PR_NUMBER> --delete-branch

# Merge with strategy (squash, rebase, merge)
gh pr merge <PR_NUMBER> --squash
gh pr merge <PR_NUMBER> --rebase
```

## Useful Flags

| Flag                | Description                            |
| ------------------- | -------------------------------------- |
| `--base <BRANCH>`   | Target branch (where PR will merge)    |
| `--title <TEXT>`    | PR title                               |
| `--body <TEXT>`     | PR description (supports markdown)     |
| `--draft`           | Create as draft (not ready for review) |
| `--assignee <USER>` | Assign to user(s)                      |
| `--reviewer <USER>` | Request review from user(s)            |
| `--label <LABELS>`  | Add labels (comma-separated)           |
| `--project <NAME>`  | Link to project board                  |
| `--fill`            | Auto-populate title/body from commits  |
| `--web`             | Open PR in web browser                 |
| `--delete-branch`   | Delete branch after merge              |

## Exit Codes

| Code | Meaning               |
| ---- | --------------------- |
| 0    | Success               |
| 1    | General error         |
| 4    | Authentication failed |

## Environment Variables

```bash
# GitHub token (alternative to `gh auth login`)
export GH_TOKEN=<your_token>

# Repository (if not in git repo directory)
export GH_REPO=owner/repo

# GitHub host (for GitHub Enterprise)
export GH_HOST=github.example.com
```

## Troubleshooting

### Authentication Issues

```bash
# Re-authenticate
gh auth logout
gh auth login

# Check authentication status
gh auth status
```

### Permission Denied

```bash
# Check if you have push access to the repository
gh repo view --json owner,name
```

### PR Creation Failed

```bash
# Try manual creation with explicit title
gh pr create --base main --title "My PR" --body "Description"

# If still fails, check your Git commits have proper messages
git log --oneline -5
```

## Reference Links

- [Official GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub CLI GitHub Repository](https://github.com/cli/cli)
- [GitHub CLI Releases](https://github.com/cli/cli/releases)
