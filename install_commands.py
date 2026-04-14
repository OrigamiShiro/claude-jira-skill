"""
Установить slash-команды скилла в ~/.claude/commands/.

Копирует файлы из commands-templates/ в ~/.claude/commands/,
чтобы команды /jira-init, /jira-switch-board, /jira-help и т.д.
появились в автокомплите Claude Code.

Запускать один раз после клонирования скилла:
  python ~/.claude/skills/jira/install_commands.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

THIS = Path(__file__).resolve()
TEMPLATES_DIR = THIS.parent / "commands-templates"
USER_COMMANDS = Path.home() / ".claude" / "commands"


def main() -> int:
    if not TEMPLATES_DIR.is_dir():
        print(f"❌ Не найдена директория шаблонов: {TEMPLATES_DIR}")
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

    print(f"Установка в {USER_COMMANDS}:")
    if installed:
        print(f"\n✓ Установлено ({len(installed)}):")
        for n in installed:
            print(f"  /{n.removesuffix('.md')}")
    if skipped:
        print(f"\n⚠ Уже существуют (пропущено, {len(skipped)}):")
        for n in skipped:
            print(f"  /{n.removesuffix('.md')}")
        print("\n  Для обновления — удали файлы вручную и перезапусти.")

    if not installed and not skipped:
        print("Шаблоны не найдены.")
        return 1

    print("\nПерезапусти Claude Code или набери / чтобы увидеть новые команды.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
