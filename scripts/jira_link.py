"""
Управление связями между issues.

Subcommands:
  add <inward> <outward> --type TYPE   — создать link
  remove <link_id>                     — удалить link
  list <key>                           — все связи issue
  types                                — доступные типы связей

Типы связей (--type):
  parent-child  (id 10007) — inward "is child of", outward "is parent of"
  blocks        (id 10000) — inward "is blocked by", outward "blocks"
  relates       (id 10003) — relates to ↔ relates to
  duplicate     (id 10002) — is duplicated by ↔ duplicates
  cloners       (id 10001) — is cloned by ↔ clones

Можно использовать ID типа напрямую: --type 10007

Примеры:
  python jira_link.py add HOR-1 HOR-2 --type parent-child
  python jira_link.py list HOR-1
  python jira_link.py types
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


# Шорткаты для типов связей (id из стандартного Jira)
LINK_TYPE_ALIASES = {
    "parent-child": "10007",
    "parent": "10007",
    "child": "10007",
    "blocks": "10000",
    "block": "10000",
    "relates": "10003",
    "duplicate": "10002",
    "cloners": "10001",
    "clone": "10001",
}


def resolve_type_id(type_arg: str) -> str:
    """Преобразует alias или прямой id в id типа связи."""
    return LINK_TYPE_ALIASES.get(type_arg.lower(), type_arg)


def cmd_add(args, client: JiraClient) -> int:
    type_id = resolve_type_id(args.type)
    client.post(
        "/rest/api/3/issueLink",
        json={
            "type": {"id": type_id},
            "inwardIssue": {"key": args.inward},
            "outwardIssue": {"key": args.outward},
        },
    )
    print(f"✓ {args.inward} ← {args.outward} (type id {type_id})")
    return 0


def cmd_remove(args, client: JiraClient) -> int:
    client.delete(f"/rest/api/3/issueLink/{args.link_id}")
    print(f"✓ Link {args.link_id} удалён")
    return 0


def cmd_list(args, client: JiraClient) -> int:
    issue = client.get(
        f"/rest/api/3/issue/{args.key}", params={"fields": "issuelinks"}
    )
    links = issue.get("fields", {}).get("issuelinks", [])
    if not links:
        print(f"{args.key}: нет связей")
        return 0

    print(f"{args.key}:")
    for link in links:
        link_id = link.get("id", "?")
        link_type = link.get("type", {})
        # Логика: API возвращает другую сторону link.
        # Если other=inwardIssue → значит focal issue (args.key) — outwardIssue,
        #                          и она имеет outward-verb к other.
        # Если other=outwardIssue → focal — inwardIssue,
        #                           и она имеет inward-verb к other.
        if "inwardIssue" in link:
            other = link["inwardIssue"]["key"]
            verb = link_type.get("outward", "?")
        else:
            other = link["outwardIssue"]["key"]
            verb = link_type.get("inward", "?")
        print(f"  [{link_id}] {verb} {other}")
    print(f"\nTotal: {len(links)}")
    return 0


def cmd_types(_args, client: JiraClient) -> int:
    data = client.get("/rest/api/3/issueLinkType")
    types = data.get("issueLinkTypes", [])
    print(f"{'ID':<8} {'NAME':<20} {'INWARD':<25} OUTWARD")
    print("-" * 80)
    for t in types:
        print(
            f"{t.get('id', '?'):<8} {t.get('name', '?'):<20} "
            f"{t.get('inward', '?'):<25} {t.get('outward', '?')}"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Управление связями между Jira issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--board", default=None, help="Имя профиля")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Создать link")
    p_add.add_argument("inward", help="Inward issue (child / blocked / etc.)")
    p_add.add_argument("outward", help="Outward issue (parent / blocker / etc.)")
    p_add.add_argument("--type", required=True, help="Тип связи (alias или id)")

    p_rm = sub.add_parser("remove", help="Удалить link")
    p_rm.add_argument("link_id", help="ID связи (из 'list')")

    p_ls = sub.add_parser("list", help="Список связей issue")
    p_ls.add_argument("key", help="Issue key")

    sub.add_parser("types", help="Доступные типы связей")

    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)
        handlers = {
            "add": cmd_add,
            "remove": cmd_remove,
            "list": cmd_list,
            "types": cmd_types,
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
