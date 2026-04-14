"""
Проверка подключения к Jira (whoami).

Примеры:
  python jira_ping.py                    # активный профиль
  python jira_ping.py --board myboard # конкретный профиль
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
    parser = argparse.ArgumentParser(description="Проверка подключения к Jira.")
    parser.add_argument(
        "--board",
        help="Имя профиля (по умолчанию активный)",
    )
    args = parser.parse_args()

    try:
        client = JiraClient(board_name=args.board)
        me = client.myself()
    except JiraError as e:
        print(f"❌ {e}")
        return 1
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    name = me.get("displayName", "?")
    email = me.get("emailAddress", "?")
    print(f"✓ Подключено как: {name} ({email})")
    print(f"  URL:     {client.base_url}")
    print(f"  Project: {client.project_key}")
    print(f"  Board:   {client.board_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
