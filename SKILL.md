---
name: pr-summary-handoff
description: "Guides the developer through creating a Pull Request on GitHub after completing a feature or hotfix branch, generating the PR link and a summary of changes. Activate when a working branch is completed and needs to be merged into dev or main."
user-invocable: true
applyTo: "**"
---

# PR Summary Handoff

## When to Use

- A feature branch or hotfix branch has been completed and tested
- The branch needs to be merged into `dev` (features) or `main` (hotfixes)
- A Pull Request must be created on GitHub
- The developer needs a summary message with a link to the PR

## What This Skill Produces

1. **Detect** the target branch (`dev` for features, `main` for hotfixes)
2. **Sync** the branch with the target (fetch + merge)
3. **Push** the branch to the remote
4. **GitHub CLI command** to create the PR from the current branch to the target
5. **Direct link** and a **summary message** in Italian with what was fixed and how
6. **Telegram notification** with the PR summary
7. _(Optional, hotfix only)_ **Merge and cleanup** with automatic sync back to `dev`

## Prerequisites

- `gh` (GitHub CLI) installed and authenticated (`gh auth status`)
- `curl` available in the terminal (required for Telegram notification)
- A Telegram bot token (get one from [@BotFather](https://t.me/BotFather) with `/newbot`)
- Your Telegram Chat ID (message your bot and visit `https://api.telegram.org/bot<TOKEN>/getUpdates` to find it)

## Procedure

### 1. Identify the context

- Determine the current branch name (`git branch --show-current`)
- Verify it's not already `dev` or `main`
- Verify the working directory is clean (`git status --porcelain`); if not, ask the developer to commit or stash before proceeding
- **Pre-flight check**: verify `gh` is available and authenticated:
  ```bash
  if ! command -v gh &> /dev/null; then
    echo "❌ gh (GitHub CLI) non trovato. Installalo da: https://cli.github.com/"
    echo "   Su Windows: winget install --id GitHub.cli"
    echo "   Su macOS: brew install gh"
    echo "   Su Linux: sudo apt install gh  (o equivalente)"
    exit 1
  fi
  gh auth status || {
    echo "❌ gh non autenticato. Esegui 'gh auth login' per configurare."
    exit 1
  }
  ```
- Determine the target branch:
  ```bash
  BRANCH=$(git branch --show-current)
  case "$BRANCH" in
    hotfix/*|bugfix/*)
      TARGET_BRANCH="main"
      echo "Hotfix rilevato — target: main"
      ;;
    *)
      TARGET_BRANCH="dev"
      echo "Feature rilevata — target: dev"
      ;;
  esac
  ```
- Update local target branch:
  ```bash
  git fetch origin "$TARGET_BRANCH"
  ```
- Collect commits made in the branch compared to the target:
  ```
  git log "$TARGET_BRANCH"..HEAD --oneline --no-decorate
  ```
- Collect a list of changed files:
  ```
  git diff "$TARGET_BRANCH"...HEAD --name-status
  ```

### 2. Sync with target branch (recommended)

Before creating the PR, align the branch with the target to reduce conflicts:

```bash
git fetch origin "$TARGET_BRANCH"
git merge "origin/$TARGET_BRANCH"
```

If there are conflicts, stop and ask the developer to resolve them manually, then retry.

> **Note**: `git merge` is safer for shared branches. If the branch is used only by you and you confirm it's safe, you can use `git rebase origin/$TARGET_BRANCH` instead.

### 3. Push the branch to remote

The branch must be on GitHub before creating the PR:

```bash
git push origin HEAD
```

### 4. Create the Pull Request on GitHub

Check if the repository has a PR template:

```bash
TEMPLATE=$(git show HEAD:.github/PULL_REQUEST_TEMPLATE.md 2>/dev/null)
```

If a template exists, use `--fill` to auto-populate title and body from commits (the template is applied server-side):

```bash
PR_URL=$(gh pr create --base "$TARGET_BRANCH" --fill 2>&1)
```

If `--fill` fails (e.g. commits are not descriptive enough), capture the error and fall back to a manual prompt. If no template exists, create the PR directly with a custom body:

```bash
PR_URL=$(gh pr create \
  --base "$TARGET_BRANCH" \
  --title "<descriptive title>" \
  --body "<PR body>" 2>&1)
```

In both cases, save the PR URL for later use in the summary and Telegram notification:

```bash
# Extract the PR URL from the output
PR_URL=$(echo "$PR_URL" | grep -oE 'https://github\.com/[^ ]+/pull/[0-9]+')
echo "✅ PR creato: $PR_URL"
```

> 💡 If the PR creation fails with `--fill`, ask the developer for a title and body manually and retry without `--fill`.

**Optional flags** (add as needed):

| Flag                      | Description                                                          |
| ------------------------- | -------------------------------------------------------------------- |
| `--draft`                 | Create the PR as a draft (not ready for review)                      |
| `--label "<name>"`        | Add labels (repeat for multiple: `--label "bug" --label "frontend"`) |
| `--assignee "<username>"` | Assign the PR to a user (use `@me` for yourself)                     |
| `--reviewer "<username>"` | Request reviewers (repeat for multiple)                              |
| `--project "<name>"`      | Link the PR to a GitHub project board                                |
| `--fill`                  | Auto-fill title and body from commit messages                        |

If the repository has a PR template (`.github/PULL_REQUEST_TEMPLATE.md`), `gh` applies it server-side when using `--fill` or when no `--body` is provided.

- **Title**: Clear and descriptive, in Italian (e.g. "Fix: risolto bug calcolo totale carrello", "Feat: aggiunta autenticazione OAuth")
- **Body**: Structure in Italian:

  ```markdown
  ## Cosa è stato fatto

  [Description of the changes made]

  ## Perché

  [Reason for the changes]

  ## Come è stato risolto

  [Technical approach used]

  ## Test effettuati

  - [List of tests performed]
  ```

> 💡 **Tip**: If the changes relate to an issue or ticket, reference it in the title or body (e.g. `Fix #123`, `Closes #42`, `PROJ-456`). This automatically links the PR to the issue.

### 5. Communicate the result to the developer

Show a clear message in the terminal:

```
✅ Pull Request created successfully!

📌 **Title**: <PR title>
🔗 **Link**: <PR url>
🌿 **Branch**: <branch-name> → $TARGET_BRANCH

📝 **Summary**:
<brief summary in Italian of what was fixed and how>

```

Then proceed to send the Telegram notification (see Step 6).

### 6. Send Telegram notification

Ask the developer for the required information:

1. **Bot Token** — Ask the developer to provide their Telegram bot token (create one via [@BotFather](https://t.me/BotFather) with `/newbot`)
2. **Chat ID** — Ask the developer to provide their Chat ID (they can get it by messaging the bot and visiting `https://api.telegram.org/bot<TOKEN>/getUpdates`)

Once both are provided, check that `curl` is available:

```bash
if ! command -v curl &> /dev/null; then
  echo "❌ curl non trovato. La notifica Telegram richiede curl. Installalo e riprova."
  exit 1
fi
```

Then prepare the message in a variable and send it via `curl`:

```bash
MESSAGE="✅ <b>Pull Request creato con successo!</b>%0A%0A📌 <b>Titolo:</b> <PR title>%0A🔗 <b>Link:</b> <PR url>%0A🌿 <b>Branch:</b> <branch-name> → $TARGET_BRANCH%0A%0A📝 <b>Summary:</b>%0A<summary in Italian>"

curl -s -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>" \
  -d "parse_mode=HTML" \
  -d "text=$MESSAGE"
```

> 💡 Using URL-encoded newlines (`%0A`) avoids multiline issues on Windows terminals.

> ⚠️ The bot token and chat ID are used only once for this notification and are **not stored** anywhere.

### 7. Post-PR: merge and cleanup (optional, only for hotfixes)

> ⚠️ **Important**: In a standard workflow, the PR should be reviewed and approved before merging.
> This step is intended only for **hotfixes or urgent changes** with explicit developer confirmation.

After showing the summary, **ask the developer for confirmation** before proceeding:

```
Do you want me to proceed with merging the PR and deleting the branch?
This should only be done for hotfixes or if the PR has already been approved.
[Reply with "yes" to proceed, "no" to leave everything as is]
```

- If **yes**: execute the merge via GitHub CLI, then update the local repo:

  ```bash
  gh pr merge --merge --delete-branch
  git checkout "$TARGET_BRANCH"
  git pull
  ```

  If the target was `main` (hotfix), also sync the fix back into `dev`:

  ```bash
  git checkout dev
  git merge main
  git push origin dev
  ```

  For local branch deletion, try the safe command first:

  ```bash
  git branch -d <branch-name>
  ```

  If it fails because the branch hasn't been fully merged, ask the developer for confirmation before forcing:

  ```bash
  git branch -D <branch-name>
  ```

- If **no**: leave the PR open and the local branch intact

## Example Output

**Feature branch → dev:**

```
✅ Pull Request created successfully!

📌 **Title**: Feat: aggiunta autenticazione OAuth
🔗 **Link**: https://github.com/nome-org/repository/pull/42
🌿 **Branch**: feat/oauth-login → dev

📝 **Summary**:
Aggiunta autenticazione tramite OAuth 2.0 con provider Google e GitHub.
Implementato flusso di login, refresh token e gestione sessione lato frontend.
```

**Hotfix → main (con merge-back su dev):**

```
✅ Pull Request created successfully!

📌 **Title**: Fix: risolto errore nel calcolo dello sconto
🔗 **Link**: https://github.com/nome-org/repository/pull/43
🌿 **Branch**: hotfix/calcolo-sconto → main

📝 **Summary**:
Risolto un bug nel calcolo dello sconto che causava prezzi negativi
quando venivano applicati coupon promozionali. Il problema era causato
da un overflow nella funzione `applyDiscount()`. Aggiunto un controllo
per garantire che lo sconto non superi il 100% del totale.
```

## Error Handling

| Scenario                                 | What to do                                                                                                                                                  |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gh` not installed                       | Show install instructions and stop: `winget install --id GitHub.cli` / `brew install gh` / `apt install gh`                                                 |
| `gh` not authenticated                   | Show error and suggest `gh auth login`                                                                                                                      |
| Target branch not found locally          | Run `git fetch origin $TARGET_BRANCH` first, then retry                                                                                                     |
| Working directory not clean              | Ask the developer to commit or stash pending changes before proceeding                                                                                      |
| Merge has conflicts                      | Stop and ask the developer to resolve conflicts manually, then retry                                                                                        |
| Push rejected (branch protection)        | Inform the developer. Suggest `--force-with-lease` only if they confirm a force push is safe                                                                |
| `gh pr create --fill` fails              | Show the error and ask the developer for a title and body manually, then retry without `--fill`                                                             |
| `gh pr merge` fails (checks not passing) | Leave the PR open and inform the developer that required checks must pass first                                                                             |
| Telegram notification fails              | Inform the developer and stop — the PR was created but the notification must be retried later                                                               |
| `curl` not available (for Telegram)      | Inform the developer that `curl` is required and stop. Suggest installing it (`winget install curl` / `brew install curl` / `apt install curl`), then retry |

## Notes

- `gh` (GitHub CLI) is **required** — the skill stops at Step 1 if it's not installed or authenticated
- `curl` is **required** for Telegram notification — the skill stops if `curl` is not available
- Telegram bot token and Chat ID are **required** — the skill asks for them at Step 6 and stops if not provided
- If you prefer to create the PR manually, you can build the direct link from the remote URL:
  ```bash
  REMOTE_URL=$(git remote get-url origin)
  ```
  Then extract `<owner>/<repo>` from the URL (supports both SSH `git@github.com:owner/repo.git` and HTTPS `https://github.com/owner/repo.git` formats) and construct:
  ```
  https://github.com/<owner>/<repo>/pull/new/<branch>?base=$TARGET_BRANCH
  ```
