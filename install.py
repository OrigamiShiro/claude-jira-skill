"""
Установщик Jira CLI Skill.

Запуск:
  python ~/.claude/skills/jira/install.py

Что делает:
  1. Проверяет наличие Python 3.9+
  2. Устанавливает зависимости (requests)
  3. Копирует slash-команды в ~/.claude/commands/
  4. Подсказывает следующий шаг (/jira-init)

Кроссплатформенный — работает на Windows, macOS, Linux.
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


def check_python() -> bool:
    if sys.version_info < (3, 9):
        print(f"❌ Требуется Python 3.9+, у тебя {sys.version.split()[0]}")
        return False
    print(f"✓ Python {sys.version.split()[0]}")
    return True


def install_requirements() -> bool:
    if not REQUIREMENTS.is_file():
        print("⚠ requirements.txt не найден, пропускаю")
        return True

    print(f"→ pip install -r {REQUIREMENTS}")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"❌ pip install failed:\n{result.stderr}")
        return False
    print("✓ Зависимости установлены")
    return True


def install_commands() -> bool:
    if not TEMPLATES_DIR.is_dir():
        print(f"❌ Не найдена директория шаблонов: {TEMPLATES_DIR}")
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
        print(f"✓ Установлено slash-команд: {len(installed)}")
        for n in installed:
            print(f"    /{n.removesuffix('.md')}")
    if skipped:
        print(f"⚠ Пропущено (уже есть): {len(skipped)}")
        for n in skipped:
            print(f"    /{n.removesuffix('.md')}")
        print("   Для переустановки удали файлы вручную и перезапусти install.py")

    return True


def print_next_steps() -> None:
    print()
    print("═" * 55)
    print("✓ Установка завершена")
    print("═" * 55)
    print()
    print("Следующие шаги:")
    print("  1. Перезапусти Claude Code (или обнови список команд).")
    print("  2. Получи Atlassian API token:")
    print("     https://id.atlassian.com/manage-profile/security/api-tokens")
    print("  3. В Claude Code запусти:  /jira-init")
    print()
    print("Список всех команд:  /jira-help")
    print()


def main() -> int:
    print(f"Jira CLI Skill — установка")
    print(f"Location: {SKILL_DIR}")
    print("─" * 55)

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
