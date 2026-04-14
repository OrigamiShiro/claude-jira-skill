"""
Install slash commands of the skill into ~/.claude/commands/.

Copies files from commands-templates/ into ~/.claude/commands/,
so that /jira-init, /jira-switch-board, /jira-help, etc. appear
in Claude Code autocomplete.

Run once after cloning the skill:
  python ~/.claude/skills/jira/install_commands.py

For a full setup (pip + commands) use install.py instead.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

THIS = Path(__file__).resolve()
TEMPLATES_DIR = THIS.parent / "commands-templates"
USER_COMMANDS = Path.home() / ".claude" / "commands"


def main() -> int:
    if not TEMPLATES_DIR.is_dir():
        print(f"❌ Templates directory not found: {TEMPLATES_DIR}")
        return 1

    USER_COMMANDS.mkdir(parents=True, exist_ok=True)

    installed = []
    skipped = []
    for src in sorted(TEMPLATES_DIR.glob("*.md")):
        dst = USER_COMMANDS / src.name
        if dst.exists():
            skipped.append(dst.name)
            continue
        shutil.copy2(src, dst)
        installed.append(dst.name)

    print(f"Install to {USER_COMMANDS}:")
    if installed:
        print(f"\n✓ Installed ({len(installed)}):")
        for n in installed:
            print(f"  /{n.removesuffix('.md')}")
    if skipped:
        print(f"\n⚠ Already exist, skipped ({len(skipped)}):")
        for n in skipped:
            print(f"  /{n.removesuffix('.md')}")
        print("\n  To update — delete files manually and re-run.")

    if not installed and not skipped:
        print("Templates not found.")
        return 1

    print("\nRestart Claude Code or type / to see new commands.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
