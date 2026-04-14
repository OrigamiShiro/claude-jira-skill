"""
Управление worklog (журнал работы).

Subcommands:
  add <key> <time> [--comment TEXT] [--started ISO_DATETIME]
      time:   Jira-формат: "3h 15m", "1d 2h", "30m", "1w"
      started: ISO datetime (например 2026-04-14T10:00:00.000+0000),
               по умолчанию — текущее время

  list <key>
  remove <key> <worklog_id>

Примеры:
  python jira_worklog.py add PROJ-1 "3h 15m" --comment "История 1.1 done"
  python jira_worklog.py list PROJ-1
  python jira_worklog.py remove PROJ-1 12345
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
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


def make_adf(text: str) -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
        ],
    }


def now_jira_format() -> str:
    """ISO datetime в формате который Jira принимает: 2026-04-14T15:00:00.000+0000."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.000+0000")


def build_worklog_payload(time_spent: str, comment: str | None, started: str | None) -> dict:
    payload: dict = {
        "timeSpent": time_spent,
        "started": started or now_jira_format(),
    }
    if comment:
        payload["comment"] = make_adf(comment)
    return payload


def cmd_add(args, client: JiraClient) -> int:
    payload = build_worklog_payload(args.time, args.comment, args.started)
    result = client.post(f"/rest/api/3/issue/{args.key}/worklog", json=payload)
    wid = result.get("id", "?") if isinstance(result, dict) else "?"
    print(f"✓ Worklog добавлен: {args.key} {args.time} (id {wid})")
    return 0


def cmd_list(args, client: JiraClient) -> int:
    data = client.get(f"/rest/api/3/issue/{args.key}/worklog")
    worklogs = data.get("worklogs", [])
    if not worklogs:
        print(f"{args.key}: worklog'ов нет")
        return 0

    print(f"{args.key}:")
    for w in worklogs:
        wid = w.get("id", "?")
        time_spent = w.get("timeSpent", "?")
        author = w.get("author", {}).get("displayName", "?")
        started = w.get("started", "?")
        print(f"  [{wid}] {time_spent} — {author} @ {started}")
    print(f"\nTotal: {len(worklogs)}")
    return 0


def cmd_remove(args, client: JiraClient) -> int:
    client.delete(f"/rest/api/3/issue/{args.key}/worklog/{args.worklog_id}")
    print(f"✓ Worklog {args.worklog_id} удалён из {args.key}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Управление Jira worklog.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--board", default=None, help="Имя профиля")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Добавить worklog")
    p_add.add_argument("key")
    p_add.add_argument("time", help='Например "3h 15m", "1d", "30m"')
    p_add.add_argument("--comment", default=None)
    p_add.add_argument("--started", default=None, help="ISO datetime")

    p_ls = sub.add_parser("list", help="Список worklog'ов")
    p_ls.add_argument("key")

    p_rm = sub.add_parser("remove", help="Удалить worklog")
    p_rm.add_argument("key")
    p_rm.add_argument("worklog_id")

    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)
        handlers = {"add": cmd_add, "list": cmd_list, "remove": cmd_remove}
        return handlers[args.command](args, client)
    except JiraError as e:
        print(f"❌ {e}")
        return 1
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
