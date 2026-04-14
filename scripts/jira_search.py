"""
Search issues via JQL.

By default the query is scoped to the ACTIVE profile's project
(prefixed with `project=<project_key> AND (...)`).
Use --all-projects to query the whole Jira instance.

Examples:
  python jira_search.py "assignee=currentUser()"              # active project only
  python jira_search.py "status='In Progress'" --limit 10
  python jira_search.py "key=PROJ-21" --fields key,summary,status
  python jira_search.py --all-projects "assignee=currentUser()"
  python jira_search.py "project=OTHER AND status='Done'"     # explicit project = not touched
"""

from __future__ import annotations

import argparse
import re
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


# Проверка что в JQL уже есть ограничение по проекту
# (project = "OV", project=OV, PROJECT=OV, project IN (...) и т.д.)
_PROJECT_CLAUSE_RE = re.compile(r"\bproject\s*(=|!=|\bin\b|\bnot\s+in\b)", re.IGNORECASE)


def has_project_clause(jql: str) -> bool:
    return bool(_PROJECT_CLAUSE_RE.search(jql))


def scope_jql_to_project(jql: str, project_key: str) -> str:
    """
    Prefix JQL with `project=<key> AND (...)`.
    If the JQL already mentions `project`, leave it unchanged.
    """
    jql = jql.strip()
    if not jql:
        return f'project = "{project_key}"'
    if has_project_clause(jql):
        return jql
    return f'project = "{project_key}" AND ({jql})'


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search Jira issues via JQL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("jql", help="JQL query")
    parser.add_argument(
        "--limit", type=int, default=50, help="Max results (default: 50)"
    )
    parser.add_argument(
        "--fields",
        default="summary,status,issuetype",
        help="Comma-separated fields (default: summary,status,issuetype)",
    )
    parser.add_argument(
        "--board", default=None, help="Profile name (default: active)"
    )
    parser.add_argument(
        "--all-projects",
        action="store_true",
        help="Don't scope to the active project; search the whole Jira instance",
    )
    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)

        # Авто-скоуп к активному project, если не отключено флагом
        # и если юзер не указал project в JQL явно.
        jql = args.jql
        if not args.all_projects:
            jql = scope_jql_to_project(jql, client.project_key)

        result = client.get(
            "/rest/api/3/search/jql",
            params={
                "jql": jql,
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
        print("No results.")
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
                if len(summary) > 60:
                    summary = summary[:57] + "..."
                row.append(summary)
            else:
                row.append(str(f.get(fn, "")))
        rows.append(row)

    headers = ["KEY"]
    for fn in field_list:
        if fn != "key":
            headers.append(fn.upper())

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
