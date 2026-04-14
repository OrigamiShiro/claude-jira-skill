"""
Первичная настройка борды.

Создаёт:
  <skill-dir>/boards/<name>.json   {url, project_key, board_id}
  <skill-dir>/creds/<name>.json    {email, token}
  <skill-dir>/config.json          {active_board, location}

skill-dir выбирается через --location:
  global → ~/.claude/skills/jira/      (по умолчанию)
  local  → ./.claude/skills/jira/      (в текущей директории)

Пример:
  python jira_init.py --location global --name myboard \\
      --url https://your-company.atlassian.net --project HOR --board-id 153 \\
      --email me@example.com --token ATATT3xFfG...
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Force UTF-8 stdout on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent))

from lib.config import resolve_location, save_config  # noqa: E402

log = logging.getLogger("jira-skill.init")


def normalize_url(url: str) -> str:
    """
    Извлекает корневой URL Jira-инстанса из любого URL.

    https://x.atlassian.net/jira/software/projects/OV/boards/2  → https://x.atlassian.net
    https://x.atlassian.net/                                     → https://x.atlassian.net
    https://x.atlassian.net                                      → https://x.atlassian.net
    """
    from urllib.parse import urlparse

    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Некорректный URL: {url!r}")
    return f"{parsed.scheme}://{parsed.netloc}"


def write_board_files(
    skill_dir: Path,
    name: str,
    url: str,
    project_key: str,
    board_id: int,
    email: str,
    token: str,
    overwrite: bool = False,
) -> None:
    """Записывает boards/<name>.json и creds/<name>.json."""
    boards_dir = skill_dir / "boards"
    creds_dir = skill_dir / "creds"
    boards_dir.mkdir(parents=True, exist_ok=True)
    creds_dir.mkdir(parents=True, exist_ok=True)

    board_path = boards_dir / f"{name}.json"
    creds_path = creds_dir / f"{name}.json"

    if board_path.exists() and not overwrite:
        raise FileExistsError(
            f"Профиль уже существует: {board_path}. "
            f"Используй --overwrite или другое имя."
        )

    board_data = {
        "url": normalize_url(url),
        "project_key": project_key,
        "board_id": int(board_id),
    }
    creds_data = {"email": email, "token": token}

    board_path.write_text(
        json.dumps(board_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    creds_path.write_text(
        json.dumps(creds_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Первичная настройка Jira борды.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--location",
        choices=["local", "global"],
        default="global",
        help="Где хранить config: local (.claude/skills/jira/ в CWD) или global (~/...)",
    )
    parser.add_argument("--name", required=True, help="Имя профиля (slug)")
    parser.add_argument("--url", required=True, help="Jira URL")
    parser.add_argument("--project", required=True, help="Project key (например HOR)")
    parser.add_argument("--board-id", type=int, required=True, help="Board ID")
    parser.add_argument("--email", required=True, help="Email Atlassian аккаунта")
    parser.add_argument("--token", required=True, help="API token")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Перезаписать существующий профиль",
    )
    parser.add_argument(
        "--no-ping",
        action="store_true",
        help="Не проверять подключение после init",
    )

    args = parser.parse_args()

    skill_dir = resolve_location(args.location)
    skill_dir.mkdir(parents=True, exist_ok=True)

    try:
        write_board_files(
            skill_dir=skill_dir,
            name=args.name,
            url=args.url,
            project_key=args.project,
            board_id=args.board_id,
            email=args.email,
            token=args.token,
            overwrite=args.overwrite,
        )
    except FileExistsError as e:
        print(f"❌ {e}")
        return 1

    config_path = skill_dir / "config.json"
    save_config(
        {"active_board": args.name, "location": args.location},
        config_path,
    )

    print(f"✓ Профиль '{args.name}' создан")
    print(f"  Location: {args.location} ({skill_dir})")

    if args.no_ping:
        return 0

    # Ping
    try:
        from lib.client import JiraClient

        client = JiraClient(board_name=args.name)
        me = client.myself()
        display_name = me.get("displayName", "?")
        print(f"✓ Подключено как: {display_name} ({me.get('emailAddress', '?')})")
        return 0
    except Exception as e:
        print(f"⚠ Профиль создан, но ping не удался: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
