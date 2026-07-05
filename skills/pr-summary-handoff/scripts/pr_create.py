#!/usr/bin/env python3
"""
PR Summary Handoff: Automated GitHub Pull Request creation and notification.

Orchestrates the workflow for creating pull requests on GitHub with proper
branch detection, validation, and Telegram notifications.

Usage:
  python pr_create.py [--branch BRANCH] [--target TARGET] [--title TITLE] [--telegram]
  python pr_create.py --help
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import quote


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class GitContext:
    """Represents the current Git repository context."""

    current_branch: str
    target_branch: str
    commits: list[str]
    changed_files: list[str]

    @staticmethod
    def detect() -> "GitContext":
        """Detect current branch, target, and commits."""
        try:
            current = subprocess.check_output(
                ["git", "branch", "--show-current"], text=True
            ).strip()
            if not current:
                raise ValueError("Not on any branch")

            # Determine target branch from naming convention
            target = "main" if any(
                current.startswith(p) for p in ["hotfix/", "bugfix/"]
            ) else "dev"

            # Get commits
            log_output = subprocess.check_output(
                ["git", "log", f"{target}..HEAD", "--oneline", "--no-decorate"],
                text=True,
            ).strip()
            commits = [line for line in log_output.split("\n") if line]

            # Get changed files
            diff_output = subprocess.check_output(
                ["git", "diff", f"{target}...HEAD", "--name-status"],
                text=True,
            ).strip()
            changed_files = [line.split("\t")[1] if "\t" in line else line
                           for line in diff_output.split("\n") if line]

            return GitContext(
                current_branch=current,
                target_branch=target,
                commits=commits,
                changed_files=changed_files,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e}")
            sys.exit(1)


@dataclass
class PullRequestDetails:
    """Details of created pull request."""

    url: str
    title: str
    number: int


def validate_environment() -> bool:
    """Validate that required tools are available and configured."""
    logger.info("Validating environment...")

    # Check git
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ git not found. Please install Git.")
        return False

    # Check gh
    try:
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error(
            "❌ GitHub CLI (gh) not found. Install from: https://cli.github.com"
        )
        return False

    # Check gh authentication
    try:
        subprocess.run(["gh", "auth", "status"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.error("❌ GitHub CLI not authenticated. Run: gh auth login")
        return False

    logger.info("✅ Environment validation passed")
    return True


def sync_with_target(target_branch: str) -> bool:
    """Sync current branch with target branch."""
    logger.info(f"Syncing with {target_branch}...")

    try:
        subprocess.run(["git", "fetch", "origin", target_branch], check=True)
        subprocess.run(["git", "merge", f"origin/{target_branch}"], check=True)
        logger.info(f"✅ Synced with {target_branch}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Sync failed: {e}")
        return False


def push_branch(branch: str) -> bool:
    """Push branch to remote."""
    logger.info(f"Pushing {branch} to remote...")

    try:
        subprocess.run(["git", "push", "origin", "HEAD"], check=True)
        logger.info("✅ Branch pushed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Push failed: {e}")
        return False


def create_pull_request(
    branch: str, target: str, title: str = None, body: str = None
) -> Optional[PullRequestDetails]:
    """Create a pull request using GitHub CLI."""
    logger.info(f"Creating PR from {branch} to {target}...")

    try:
        cmd = ["gh", "pr", "create", "--base", target]

        if title:
            cmd.extend(["--title", title])
        if body:
            cmd.extend(["--body", body])
        else:
            cmd.append("--fill")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pr_url = result.stdout.strip()

        # Parse URL to extract number
        pr_number = int(pr_url.rstrip("/").split("/")[-1])

        logger.info(f"✅ PR created: {pr_url}")
        return PullRequestDetails(url=pr_url, title=title or "(auto-filled)", number=pr_number)

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ PR creation failed: {e.stderr}")
        return None


def send_telegram_notification(
    bot_token: str, chat_id: str, pr_details: PullRequestDetails,
    context: GitContext
) -> bool:
    """Send PR notification via Telegram."""
    logger.info("Sending Telegram notification...")

    try:
        message_parts = [
            "✅ <b>Pull Request creato!</b>",
            f"📌 <b>Titolo:</b> {pr_details.title}",
            f"🔗 <b>Link:</b> {pr_details.url}",
            f"🌿 <b>Branch:</b> {context.current_branch} → {context.target_branch}",
            "",
            f"📝 <b>Commits:</b> {len(context.commits)}",
            f"📄 <b>File modificati:</b> {len(context.changed_files)}",
        ]

        message = "\n".join(message_parts)
        encoded_message = quote(message)

        subprocess.run(
            [
                "curl",
                "-s",
                "-X", "POST",
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                "-d", f"chat_id={chat_id}",
                "-d", "parse_mode=HTML",
                "-d", f"text={encoded_message}",
            ],
            check=True,
            capture_output=True,
        )

        logger.info("✅ Telegram notification sent")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Telegram notification failed: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ curl not found. Telegram notification skipped.")
        return False


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated GitHub PR creation with Telegram notification"
    )
    parser.add_argument(
        "--branch", help="Branch to create PR from (auto-detected if omitted)"
    )
    parser.add_argument(
        "--target", help="Target branch (auto-detected from branch name if omitted)"
    )
    parser.add_argument("--title", help="PR title (auto-filled from commits if omitted)")
    parser.add_argument("--body", help="PR description body")
    parser.add_argument(
        "--telegram", action="store_true", help="Send Telegram notification"
    )
    parser.add_argument(
        "--bot-token", help="Telegram bot token (required with --telegram)"
    )
    parser.add_argument(
        "--chat-id", help="Telegram chat ID (required with --telegram)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate environment
    if not validate_environment():
        return 1

    # Detect Git context
    context = GitContext.detect()
    logger.info(
        f"Current branch: {context.current_branch}, target: {context.target_branch}"
    )
    logger.info(f"Found {len(context.commits)} commits, {len(context.changed_files)} changed files")

    # Sync with target
    if not sync_with_target(context.target_branch):
        return 1

    # Push branch
    if not push_branch(context.current_branch):
        return 1

    # Create PR
    pr = create_pull_request(
        context.current_branch,
        context.target_branch,
        title=args.title,
        body=args.body,
    )

    if not pr:
        return 1

    # Show summary
    print("\n" + "=" * 60)
    print("✅ Pull Request created successfully!")
    print("=" * 60)
    print(f"📌 Title:   {pr.title}")
    print(f"🔗 Link:    {pr.url}")
    print(f"🌿 Branch:  {context.current_branch} → {context.target_branch}")
    print(f"📝 Summary: {len(context.commits)} commits, {len(context.changed_files)} files changed")
    print("=" * 60 + "\n")

    # Send Telegram notification if requested
    if args.telegram:
        if not args.bot_token or not args.chat_id:
            logger.error("❌ --telegram requires --bot-token and --chat-id")
            return 1

        if not send_telegram_notification(
            args.bot_token, args.chat_id, pr, context
        ):
            logger.warning("⚠️ Telegram notification failed, but PR was created")

    return 0


if __name__ == "__main__":
    sys.exit(main())
