"""
Удаление issue в Jira.

ВНИМАНИЕ: необратимая операция.

Примеры:
  python jira_delete.py PROJ-258
  python jira_delete.py PROJ-1 PROJ-2 PROJ-3        # batch
  python jira_delete.py PROJ-1 --delete-subtasks  # удалить вместе с подзадачами
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

from lib.client import JiraClient, JiraError, JiraNotFoundError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Удаление Jira issues.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("keys", nargs="+", help="Ключи issue для удаления (PROJ-1 PROJ-2 ...)")
    parser.add_argument(
        "--delete-subtasks",
        action="store_true",
        help="Удалять вместе с подзадачами (иначе API вернёт ошибку если есть subtasks)",
    )
    parser.add_argument("--board", default=None, help="Имя профиля")
    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)
    except (JiraError, FileNotFoundError) as e:
        print(f"❌ {e}")
        return 1

    ok = 0
    fail = 0
    for key in args.keys:
        path = f"/rest/api/3/issue/{key}"
        if args.delete_subtasks:
            path += "?deleteSubtasks=true"
        try:
            client.delete(path)
            print(f"✓ {key} удалена")
            ok += 1
        except JiraNotFoundError:
            print(f"✗ {key}: не найдена")
            fail += 1
        except JiraError as e:
            print(f"✗ {key}: {e}")
            fail += 1

    if len(args.keys) > 1:
        print(f"\n✓ {ok} удалено | ✗ {fail} ошибок")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
