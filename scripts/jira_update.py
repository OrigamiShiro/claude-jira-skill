"""
Обновление issue в Jira.

Subcommands:
  transition <key> <status>     — сменить статус (Готово, В работе, ...)
  assign <key> <account_id>     — назначить assignee
  unassign <key>                — снять assignee
  field <key> <field> <value>   — обновить произвольное поле (summary, description)

Примеры:
  python jira_update.py transition HOR-123 "Готово"
  python jira_update.py assign HOR-123 712020:abc
  python jira_update.py unassign HOR-123
  python jira_update.py field HOR-123 summary "New title"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent))

from lib.client import JiraClient, JiraError  # noqa: E402


def find_transition_id(client: JiraClient, key: str, status_name: str) -> str | None:
    """Возвращает id перехода для status_name (поиск без учёта регистра)."""
    data = client.get(f"/rest/api/3/issue/{key}/transitions")
    target = status_name.strip().lower()
    for t in data.get("transitions", []):
        if t.get("name", "").lower() == target:
            return t.get("id")
        # Также проверяем целевой статус (to.name)
        to = t.get("to", {})
        if to.get("name", "").lower() == target:
            return t.get("id")
    return None


def cmd_transition(args, client: JiraClient) -> int:
    tid = find_transition_id(client, args.key, args.status)
    if tid is None:
        print(f"❌ Переход в статус '{args.status}' недоступен для {args.key}")
        return 1
    client.post(
        f"/rest/api/3/issue/{args.key}/transitions",
        json={"transition": {"id": tid}},
    )
    print(f"✓ {args.key} → {args.status}")
    return 0


def cmd_assign(args, client: JiraClient) -> int:
    client.put(
        f"/rest/api/3/issue/{args.key}/assignee",
        json={"accountId": args.account_id},
    )
    print(f"✓ {args.key} назначен на {args.account_id}")
    return 0


def cmd_unassign(args, client: JiraClient) -> int:
    client.put(
        f"/rest/api/3/issue/{args.key}/assignee",
        json={"accountId": None},
    )
    print(f"✓ {args.key} — assignee снят")
    return 0


def cmd_field(args, client: JiraClient) -> int:
    field_value: object = args.value
    # description идёт в ADF
    if args.field == "description":
        field_value = {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": args.value}]}
            ],
        }
    client.put(
        f"/rest/api/3/issue/{args.key}",
        json={"fields": {args.field: field_value}},
    )
    print(f"✓ {args.key}.{args.field} обновлено")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Обновление Jira-задач.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--board", default=None, help="Имя профиля")
    sub = parser.add_subparsers(dest="command", required=True)

    p_t = sub.add_parser("transition", help="Сменить статус")
    p_t.add_argument("key")
    p_t.add_argument("status")

    p_a = sub.add_parser("assign", help="Назначить assignee")
    p_a.add_argument("key")
    p_a.add_argument("account_id")

    p_u = sub.add_parser("unassign", help="Снять assignee")
    p_u.add_argument("key")

    p_f = sub.add_parser("field", help="Обновить поле")
    p_f.add_argument("key")
    p_f.add_argument("field")
    p_f.add_argument("value")

    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)
        handlers = {
            "transition": cmd_transition,
            "assign": cmd_assign,
            "unassign": cmd_unassign,
            "field": cmd_field,
        }
        return handlers[args.command](args, client)
    except JiraError as e:
        print(f"❌ {e}")
        return 1
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
