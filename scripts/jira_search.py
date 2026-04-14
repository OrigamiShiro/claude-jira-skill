"""
Поиск issue по JQL.

Примеры:
  python jira_search.py "project=HOR AND status='В работе'"
  python jira_search.py "assignee=currentUser()" --limit 10
  python jira_search.py "key=PROJ-21" --fields key,summary,status
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Поиск Jira issues по JQL.")
    parser.add_argument("jql", help="JQL запрос")
    parser.add_argument(
        "--limit", type=int, default=50, help="Максимум результатов (default: 50)"
    )
    parser.add_argument(
        "--fields",
        default="summary,status,issuetype",
        help="Поля через запятую (default: summary,status,issuetype)",
    )
    parser.add_argument(
        "--board", default=None, help="Имя профиля (по умолчанию активный)"
    )
    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)
        result = client.get(
            "/rest/api/3/search/jql",
            params={
                "jql": args.jql,
                "maxResults": args.limit,
                "fields": args.fields,
            },
        )
    except JiraError as e:
        print(f"❌ {e}")
        return 1
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1

    issues = result.get("issues", [])
    if not issues:
        print("Ничего не найдено.")
        return 0

    field_list = [f.strip() for f in args.fields.split(",") if f.strip()]

    rows = []
    for i in issues:
        f = i.get("fields", {})
        row = [i.get("key", "?")]
        for fn in field_list:
            if fn == "key":
                continue
            if fn == "status":
                row.append(f.get("status", {}).get("name", "?"))
            elif fn == "issuetype":
                row.append(f.get("issuetype", {}).get("name", "?"))
            elif fn == "assignee":
                a = f.get("assignee")
                row.append(a.get("displayName") if a else "<unassigned>")
            elif fn == "summary":
                summary = f.get("summary", "")
                # Обрезаем длинные summary
                if len(summary) > 60:
                    summary = summary[:57] + "..."
                row.append(summary)
            else:
                # Произвольное поле — тупо к str
                row.append(str(f.get(fn, "")))
        rows.append(row)

    # Заголовок
    headers = ["KEY"]
    for fn in field_list:
        if fn != "key":
            headers.append(fn.upper())

    # Ширина колонок
    widths = [
        max(len(headers[i]), max(len(str(r[i])) for r in rows))
        for i in range(len(headers))
    ]

    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(fmt.format(*r))
    print(f"\nFound: {len(issues)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
