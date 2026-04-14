"""
Показать все доступные команды скилла с кратким описанием.

Использование:
  python jira_help.py                # все команды
  python jira_help.py --commands     # только slash-команды
  python jira_help.py --scripts      # только CLI-скрипты
"""

from __future__ import annotations

import argparse
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


SLASH_COMMANDS = [
    ("/jira-init",               "Первичная настройка новой борды (location, name, url, project, board-id, email, token)"),
    ("/jira-add-board",          "Добавить ещё одну борду (не трогая существующие)"),
    ("/jira-switch-board",       "Переключить активную борду — интерактивный выбор из списка"),
    ("/jira-show [name]",        "Показать детали профиля (без имени — активный)"),
    ("/jira-remove-board <name>","Удалить профиль (boards/ + creds/ файлы)"),
    ("/jira-ping",               "Проверить подключение к Jira (whoami)"),
    ("/jira-help",               "Показать этот список"),
]

SCRIPTS = [
    ("jira_init.py",     "Первичная настройка борды (--location, --name, --url, --project, --board-id, --email, --token)"),
    ("jira_config.py",   "Управление профилями: list | current | show [name] | switch <name> | remove <name>"),
    ("jira_ping.py",     "Проверка подключения: /rest/api/3/myself"),
    ("jira_create.py",   "Создать issue: <summary> [-d TEXT] [-t Задача|Баг|История|Эпик] [-a account_id] [--no-assignee]"),
    ("jira_update.py",   "Обновить issue: transition <key> <status> | assign <key> <id> | unassign <key> | field <key> <field> <value>"),
    ("jira_delete.py",   "Удалить issue: <key1> [<key2> ...] [--delete-subtasks]"),
    ("jira_search.py",   "JQL поиск: '<JQL>' [--limit N] [--fields f1,f2]"),
    ("jira_link.py",     "Связи: add <in> <out> --type TYPE | remove <link_id> | list <key> | types"),
    ("jira_worklog.py",  "Worklog: add <key> <time> [--comment TEXT] [--started ISO] | list <key> | remove <key> <worklog_id>"),
    ("jira_sprint.py",   "Спринты: list [--state] | show <id> | create --name NAME | move <id> <key1>... | start <id> | complete <id>"),
    ("jira_batch.py",    "Массовые операции: JSON-массив через --file или stdin (op: transition/worklog/link/assign/unassign/delete)"),
    ("jira_help.py",     "Этот список"),
]


def print_slash_commands():
    print("═══ Slash-команды (в Claude Code) ═══")
    print()
    max_cmd = max(len(c) for c, _ in SLASH_COMMANDS)
    for cmd, desc in SLASH_COMMANDS:
        print(f"  {cmd:<{max_cmd}}  {desc}")
    print()


def print_scripts():
    print("═══ CLI-скрипты (прямой вызов) ═══")
    print()
    max_name = max(len(n) for n, _ in SCRIPTS)
    for name, desc in SCRIPTS:
        print(f"  {name:<{max_name}}  {desc}")
    print()
    print("  Путь: ~/.claude/skills/jira/scripts/<script>")
    print("  Флаг --board <name> доступен в любом скрипте для разового override профиля.")
    print()


def print_examples():
    print("═══ Быстрые примеры ═══")
    print()
    print("  # Создать задачу")
    print('  python jira_create.py "New feature" -t История')
    print()
    print("  # Закрыть и залогировать время")
    print("  python jira_update.py transition PROJ-1 \"Готово\"")
    print('  python jira_worklog.py add PROJ-1 "2h 30m" --comment "done"')
    print()
    print("  # Batch")
    print('  echo \'[{"op":"transition","key":"PROJ-1","status":"Готово"}]\' | python jira_batch.py')
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Справка по Jira CLI skill.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--commands", action="store_true", help="Только slash-команды")
    parser.add_argument("--scripts", action="store_true", help="Только CLI-скрипты")
    args = parser.parse_args()

    print()
    print("Jira CLI Skill — справка")
    print("─" * 60)
    print()

    # По умолчанию показываем всё. Флаги сужают.
    show_all = not (args.commands or args.scripts)

    if args.commands or show_all:
        print_slash_commands()
    if args.scripts or show_all:
        print_scripts()
    if show_all:
        print_examples()

    print("Подробнее: ~/.claude/skills/jira/SKILL.md и README.md")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
