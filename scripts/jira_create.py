"""
Создание issue в Jira.

По умолчанию assignee = текущий пользователь (whoami).
Используй --no-assignee чтобы не назначать, или -a <accountId> для другого.

Примеры:
  python jira_create.py "Test task"                      # assignee = me
  python jira_create.py "Bug report" -t Баг -d "Detailed description"
  python jira_create.py "Story" -t История -a 712020:abc...
  python jira_create.py "No assignee task" --no-assignee
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


def make_adf(text: str) -> dict:
    """Atlassian Document Format — обёртка вокруг plain-text."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
        ],
    }


def build_payload(
    project_key: str,
    summary: str,
    issue_type: str,
    description: str | None = None,
    assignee: str | None = None,
) -> dict:
    fields = {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }
    if description:
        fields["description"] = make_adf(description)
    if assignee:
        fields["assignee"] = {"accountId": assignee}
    return {"fields": fields}


def main() -> int:
    parser = argparse.ArgumentParser(description="Создание Jira-задачи.")
    parser.add_argument("summary", help="Заголовок задачи")
    parser.add_argument("-d", "--description", default=None, help="Описание")
    parser.add_argument(
        "-t",
        "--type",
        default="Задача",
        help="Тип issue (Задача, Баг, История, Эпик)",
    )
    parser.add_argument(
        "-a",
        "--assignee",
        default=None,
        help="accountId исполнителя (по умолчанию — текущий пользователь)",
    )
    parser.add_argument(
        "--no-assignee",
        action="store_true",
        help="Не назначать assignee (по умолчанию назначается текущий юзер)",
    )
    parser.add_argument(
        "--board", default=None, help="Имя профиля (по умолчанию активный)"
    )
    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)

        # Определение assignee:
        # --no-assignee       → не назначать
        # -a <id>             → явный accountId
        # (ничего не указано) → активный пользователь (myself)
        if args.no_assignee:
            assignee = None
        elif args.assignee:
            assignee = args.assignee
        else:
            me = client.myself()
            assignee = me.get("accountId")

        payload = build_payload(
            project_key=client.project_key,
            summary=args.summary,
            issue_type=args.type,
            description=args.description,
            assignee=assignee,
        )
        result = client.post("/rest/api/3/issue", json=payload)
    except JiraError as e:
        print(f"❌ {e}")
        return 1
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1

    key = result.get("key", "?")
    print(f"✓ Задача создана: {key} | {client.browse_url(key)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
