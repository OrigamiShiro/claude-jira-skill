"""
Управление спринтами (Agile API).

Subcommands:
  list [--state STATE] [--board-id N]    — список спринтов борды
                                            STATE: active, future, closed
  show <sprint_id>                       — детали спринта + issues в нём
  create --name NAME [--goal TEXT] [--start ISO] [--end ISO]
  move <sprint_id> <key1> [<key2> ...]   — переместить issues в спринт
  start <sprint_id>                      — запустить спринт (нужен start/end date)
  complete <sprint_id>                   — закрыть спринт

Примеры:
  python jira_sprint.py list --state future
  python jira_sprint.py show 17
  python jira_sprint.py create --name "Sprint 5" --goal "Foundation"
  python jira_sprint.py move 17 PROJ-1 PROJ-2 PROJ-3
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


def cmd_list(args, client: JiraClient) -> int:
    board_id = args.board_id or client.board_id
    params = {}
    if args.state:
        params["state"] = args.state

    data = client.get(f"/rest/agile/1.0/board/{board_id}/sprint", params=params)
    sprints = data.get("values", [])
    if not sprints:
        print(f"Board {board_id}: нет спринтов{f' ({args.state})' if args.state else ''}")
        return 0

    print(f"Board {board_id}:")
    for s in sprints:
        sid = s.get("id", "?")
        name = s.get("name", "?")
        state = s.get("state", "?")
        print(f"  [{sid}] {name} ({state})")
    return 0


def cmd_show(args, client: JiraClient) -> int:
    sprint = client.get(f"/rest/agile/1.0/sprint/{args.sprint_id}")
    print(f"Sprint {sprint.get('id')}: {sprint.get('name')}")
    print(f"  State:    {sprint.get('state')}")
    if sprint.get("goal"):
        print(f"  Goal:     {sprint.get('goal')}")
    if sprint.get("startDate"):
        print(f"  Start:    {sprint.get('startDate')}")
    if sprint.get("endDate"):
        print(f"  End:      {sprint.get('endDate')}")

    issues_data = client.get(f"/rest/agile/1.0/sprint/{args.sprint_id}/issue")
    issues = issues_data.get("issues", [])
    print(f"\n  Issues ({len(issues)}):")
    for i in issues:
        key = i.get("key", "?")
        f = i.get("fields", {})
        summary = f.get("summary", "")
        if len(summary) > 60:
            summary = summary[:57] + "..."
        status = f.get("status", {}).get("name", "?")
        print(f"    {key:<10} [{status}] {summary}")
    return 0


def cmd_create(args, client: JiraClient) -> int:
    board_id = args.board_id or client.board_id
    payload: dict = {"name": args.name, "originBoardId": board_id}
    if args.goal:
        payload["goal"] = args.goal
    if args.start:
        payload["startDate"] = args.start
    if args.end:
        payload["endDate"] = args.end

    result = client.post("/rest/agile/1.0/sprint", json=payload)
    sid = result.get("id", "?")
    print(f"✓ Спринт '{args.name}' создан (id: {sid})")
    return 0


def cmd_move(args, client: JiraClient) -> int:
    payload = {"issues": args.keys}
    client.post(f"/rest/agile/1.0/sprint/{args.sprint_id}/issue", json=payload)
    n = len(args.keys)
    print(f"✓ {n} issue(s) перемещены в спринт {args.sprint_id}")
    return 0


def cmd_start(args, client: JiraClient) -> int:
    payload = {"state": "active"}
    if args.start:
        payload["startDate"] = args.start
    if args.end:
        payload["endDate"] = args.end
    client.post(f"/rest/agile/1.0/sprint/{args.sprint_id}", json=payload)
    print(f"✓ Спринт {args.sprint_id} запущен")
    return 0


def cmd_complete(args, client: JiraClient) -> int:
    client.post(
        f"/rest/agile/1.0/sprint/{args.sprint_id}", json={"state": "closed"}
    )
    print(f"✓ Спринт {args.sprint_id} закрыт")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Управление Jira-спринтами.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--board", default=None, help="Имя профиля")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ls = sub.add_parser("list", help="Список спринтов")
    p_ls.add_argument("--state", choices=["active", "future", "closed"])
    p_ls.add_argument("--board-id", type=int, default=None)

    p_sh = sub.add_parser("show", help="Детали спринта")
    p_sh.add_argument("sprint_id", type=int)

    p_cr = sub.add_parser("create", help="Создать спринт")
    p_cr.add_argument("--name", required=True)
    p_cr.add_argument("--goal", default=None)
    p_cr.add_argument("--start", default=None, help="ISO datetime")
    p_cr.add_argument("--end", default=None, help="ISO datetime")
    p_cr.add_argument("--board-id", type=int, default=None)

    p_mv = sub.add_parser("move", help="Переместить issues в спринт")
    p_mv.add_argument("sprint_id", type=int)
    p_mv.add_argument("keys", nargs="+")

    p_st = sub.add_parser("start", help="Запустить спринт")
    p_st.add_argument("sprint_id", type=int)
    p_st.add_argument("--start", default=None)
    p_st.add_argument("--end", default=None)

    p_cm = sub.add_parser("complete", help="Закрыть спринт")
    p_cm.add_argument("sprint_id", type=int)

    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)
        handlers = {
            "list": cmd_list,
            "show": cmd_show,
            "create": cmd_create,
            "move": cmd_move,
            "start": cmd_start,
            "complete": cmd_complete,
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
