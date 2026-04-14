"""
Массовые операции через JSON.

Принимает JSON-массив команд из файла или stdin. Каждая команда:
  {"op": "transition", "key": "PROJ-1", "status": "Готово"}
  {"op": "worklog", "key": "PROJ-1", "time": "2h", "comment": "..."}
  {"op": "link", "inward": "PROJ-1", "outward": "PROJ-2", "type": "parent-child"}
  {"op": "assign", "key": "PROJ-1", "account_id": "712020:abc"}

Примеры:
  python jira_batch.py --file ops.json
  cat ops.json | python jira_batch.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Также stdin — для чтения JSON с кириллицей через pipe
if sys.stdin.encoding and sys.stdin.encoding.lower() != "utf-8":
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent))

from jira_link import resolve_type_id  # noqa: E402
from jira_update import find_transition_id  # noqa: E402
from jira_worklog import build_worklog_payload  # noqa: E402
from lib.client import JiraClient, JiraError  # noqa: E402


def op_transition(client: JiraClient, op: dict) -> str:
    key = op["key"]
    status = op["status"]
    tid = find_transition_id(client, key, status)
    if tid is None:
        return f"✗ {key} → {status}: переход недоступен"
    client.post(
        f"/rest/api/3/issue/{key}/transitions",
        json={"transition": {"id": tid}},
    )
    return f"✓ {key} → {status}"


def op_worklog(client: JiraClient, op: dict) -> str:
    key = op["key"]
    payload = build_worklog_payload(
        time_spent=op["time"],
        comment=op.get("comment"),
        started=op.get("started"),
    )
    client.post(f"/rest/api/3/issue/{key}/worklog", json=payload)
    return f"✓ {key} worklog {op['time']}"


def op_link(client: JiraClient, op: dict) -> str:
    type_id = resolve_type_id(op["type"])
    client.post(
        "/rest/api/3/issueLink",
        json={
            "type": {"id": type_id},
            "inwardIssue": {"key": op["inward"]},
            "outwardIssue": {"key": op["outward"]},
        },
    )
    return f"✓ {op['inward']} ← {op['outward']} (link {type_id})"


def op_assign(client: JiraClient, op: dict) -> str:
    key = op["key"]
    client.put(
        f"/rest/api/3/issue/{key}/assignee",
        json={"accountId": op["account_id"]},
    )
    return f"✓ {key} assignee → {op['account_id']}"


def op_unassign(client: JiraClient, op: dict) -> str:
    key = op["key"]
    client.put(
        f"/rest/api/3/issue/{key}/assignee", json={"accountId": None}
    )
    return f"✓ {key} unassigned"


def op_delete(client: JiraClient, op: dict) -> str:
    key = op["key"]
    path = f"/rest/api/3/issue/{key}"
    if op.get("delete_subtasks"):
        path += "?deleteSubtasks=true"
    client.delete(path)
    return f"✓ {key} удалена"


OP_HANDLERS = {
    "transition": op_transition,
    "worklog": op_worklog,
    "link": op_link,
    "assign": op_assign,
    "unassign": op_unassign,
    "delete": op_delete,
}


def execute(client: JiraClient, ops: list[dict]) -> tuple[int, int]:
    """Возвращает (успехов, ошибок)."""
    ok = 0
    fail = 0
    for op in ops:
        op_name = op.get("op")
        handler = OP_HANDLERS.get(op_name)
        if handler is None:
            print(f"✗ Unknown op: {op_name}")
            fail += 1
            continue
        try:
            line = handler(client, op)
            print(line)
            if line.startswith("✓"):
                ok += 1
            else:
                fail += 1
        except (JiraError, KeyError, ValueError) as e:
            print(f"✗ {op_name} {op.get('key', '?')}: {e}")
            fail += 1
    return ok, fail


def load_ops(file_path: str | None) -> list[dict]:
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    if not isinstance(data, list):
        raise ValueError("Ожидался JSON-массив команд")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Массовые операции с Jira.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--file", "-f", default=None, help="JSON-файл (иначе stdin)"
    )
    parser.add_argument("--board", default=None, help="Имя профиля")
    args = parser.parse_args()

    try:
        ops = load_ops(args.file)
    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        print(f"❌ Ошибка чтения JSON: {e}")
        return 1

    try:
        client = JiraClient(board_name=args.board)
    except (JiraError, FileNotFoundError) as e:
        print(f"❌ {e}")
        return 1

    ok, fail = execute(client, ops)
    print(f"\n✓ {ok} успехов | ✗ {fail} ошибок")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
