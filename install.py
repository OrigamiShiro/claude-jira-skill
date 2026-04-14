"""
Jira CLI Skill installer.

Usage:
  python ~/.claude/skills/jira/install.py

What it does:
  1. Verifies the skill is in ~/.claude/skills/jira/ (Claude Code default path)
  2. Checks Python 3.9+
  3. Installs pip dependencies (requests)
  4. Copies slash commands to ~/.claude/commands/
  5. Prints next steps (/jira-init)

IMPORTANT: this installer does NOT copy the skill anywhere.
The skill must already be at ~/.claude/skills/jira/ for Claude Code to detect it.
If you cloned the repo elsewhere, either move it or create a symlink/junction
to ~/.claude/skills/jira/.

Cross-platform — works on Windows, macOS, Linux.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SKILL_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SKILL_DIR / "commands-templates"
USER_COMMANDS = Path.home() / ".claude" / "commands"
REQUIREMENTS = SKILL_DIR / "requirements.txt"
EXPECTED_SKILL_PATH = (Path.home() / ".claude" / "skills" / "jira").resolve()


def check_location() -> bool:
    """Warn if skill is not at the expected path ~/.claude/skills/jira/."""
    if SKILL_DIR == EXPECTED_SKILL_PATH:
        print(f"✓ Location: {SKILL_DIR}")
        return True

    print(f"⚠ Skill is NOT at the expected location!")
    print(f"  Current:  {SKILL_DIR}")
    print(f"  Expected: {EXPECTED_SKILL_PATH}")
    print()
    print("  Claude Code auto-detects skills from ~/.claude/skills/<name>/.")
    print("  If you leave the skill where it is, Claude won't see it.")
    print()
    print("  Options:")
    print(f"    1. Move:     mv \"{SKILL_DIR}\" \"{EXPECTED_SKILL_PATH}\"")
    print(f"    2. Clone again into the correct path:")
    print(f"       git clone <repo> \"{EXPECTED_SKILL_PATH}\"")
    print(f"    3. Symlink (macOS/Linux):")
    print(f"       ln -s \"{SKILL_DIR}\" \"{EXPECTED_SKILL_PATH}\"")
    print(f"    4. Junction (Windows, cmd as admin):")
    print(f"       mklink /J \"{EXPECTED_SKILL_PATH}\" \"{SKILL_DIR}\"")
    print()

    try:
        answer = input("Continue installation anyway? [y/N] ").strip().lower()
    except EOFError:
        answer = "n"
    if answer != "y":
        print("Aborted.")
        return False

    print("⚠ Continuing — but Claude Code may not see this skill.")
    return True


def check_python() -> bool:
    if sys.version_info < (3, 9):
        print(f"❌ Python 3.9+ required, you have {sys.version.split()[0]}")
        return False
    print(f"✓ Python {sys.version.split()[0]}")
    return True


def install_requirements() -> bool:
    if not REQUIREMENTS.is_file():
        print("⚠ requirements.txt not found, skipping")
        return True

    print(f"→ pip install -r {REQUIREMENTS}")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"❌ pip install failed:\n{result.stderr}")
        return False
    print("✓ Dependencies installed")
    return True


def install_commands() -> bool:
    if not TEMPLATES_DIR.is_dir():
        print(f"❌ Templates directory not found: {TEMPLATES_DIR}")
        return False

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

    if installed:
        print(f"✓ Installed slash commands: {len(installed)}")
        for n in installed:
            print(f"    /{n.removesuffix('.md')}")
    if skipped:
        print(f"⚠ Skipped (already exist): {len(skipped)}")
        for n in skipped:
            print(f"    /{n.removesuffix('.md')}")
        print("   To reinstall — delete those files and re-run install.py")

    return True


def print_next_steps() -> None:
    print()
    print("═" * 55)
    print("✓ Installation complete")
    print("═" * 55)
    print()
    print("Next steps:")
    print("  1. Restart Claude Code (or refresh command list).")
    print("  2. Get an Atlassian API token:")
    print("     https://id.atlassian.com/manage-profile/security/api-tokens")
    print("  3. In Claude Code run:  /jira-init")
    print()
    print("See all commands:  /jira-help")
    print()


def main() -> int:
    print("Jira CLI Skill — installation")
    print("─" * 55)

    if not check_location():
        return 1
    if not check_python():
        return 1
    if not install_requirements():
        return 1
    if not install_commands():
        return 1

    print_next_steps()
    return 0


if __name__ == "__main__":
    sys.exit(main())
