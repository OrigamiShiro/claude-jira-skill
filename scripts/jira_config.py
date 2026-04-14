"""
Управление профилями: list / show / switch / remove / current.

Примеры:
  python jira_config.py list                    # все профили
  python jira_config.py current                 # активный профиль
  python jira_config.py show hornyvilla         # детали профиля
  python jira_config.py switch other-board      # сменить активный
  python jira_config.py remove old-board        # удалить профиль
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

from lib.auth import (  # noqa: E402
    list_boards,
    load_board_info,
    load_creds_file,
    mask_token,
)
from lib.config import (  # noqa: E402
    config_dir,
    find_config,
    get_active_board,
    set_active_board,
)


def _skill_dir() -> Path | None:
    cfg = find_config()
    if cfg is None:
        return None
    return config_dir(cfg)


def cmd_list(_args) -> int:
    skill = _skill_dir()
    if skill is None:
        print("❌ config.json не найден. Запусти jira_init.py.")
        return 1

    boards = list_boards(skill_dir=skill)
    if not boards:
        print("Нет доступных профилей. Запусти jira_init.py.")
        return 0

    active = get_active_board()
    for name in boards:
        marker = " *" if name == active else "  "
        print(f"{marker}{name}")
    return 0


def cmd_current(_args) -> int:
    active = get_active_board()
    if active is None:
        print("❌ Активный профиль не выбран.")
        return 1
    print(active)
    return 0


def cmd_show(args) -> int:
    skill = _skill_dir()
    if skill is None:
        print("❌ config.json не найден.")
        return 1

    name = args.name or get_active_board()
    if name is None:
        print("❌ Имя профиля не указано и активного нет.")
        return 1

    try:
        board = load_board_info(name, skill_dir=skill)
        creds_file_name = board.get("creds_file", name)
        creds = load_creds_file(creds_file_name, skill_dir=skill)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    active = get_active_board()
    is_active = " (active)" if name == active else ""
    print(f"Profile: {name}{is_active}")
    print(f"  URL:     {board.get('url')}")
    print(f"  Project: {board.get('project_key')}")
    print(f"  Board:   {board.get('board_id')}")
    print(f"  Email:   {creds.get('email')}")
    print(f"  Token:   {mask_token(creds.get('token', ''))}")
    return 0


def cmd_switch(args) -> int:
    skill = _skill_dir()
    if skill is None:
        print("❌ config.json не найден.")
        return 1

    boards = list_boards(skill_dir=skill)
    if args.name not in boards:
        print(f"❌ Профиль '{args.name}' не найден. Доступны: {', '.join(boards) or '<none>'}")
        return 1

    set_active_board(args.name)
    print(f"✓ Активный профиль: {args.name}")
    return 0


def cmd_remove(args) -> int:
    skill = _skill_dir()
    if skill is None:
        print("❌ config.json не найден.")
        return 1

    boards = list_boards(skill_dir=skill)
    if args.name not in boards:
        print(f"❌ Профиль '{args.name}' не найден.")
        return 1

    board_file = skill / "boards" / f"{args.name}.json"
    creds_file = skill / "creds" / f"{args.name}.json"

    removed = []
    if board_file.exists():
        board_file.unlink()
        removed.append(str(board_file.relative_to(skill)))
    if creds_file.exists():
        creds_file.unlink()
        removed.append(str(creds_file.relative_to(skill)))

    # Если удаляли активный — снять метку
    active = get_active_board()
    if active == args.name:
        set_active_board("")
        print(f"✓ Профиль '{args.name}' удалён (был активным — теперь без активного)")
    else:
        print(f"✓ Профиль '{args.name}' удалён")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Управление Jira-профилями.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="Список профилей")
    sub.add_parser("current", help="Активный профиль")

    p_show = sub.add_parser("show", help="Детали профиля")
    p_show.add_argument("name", nargs="?", help="Имя профиля (по умолчанию активный)")

    p_switch = sub.add_parser("switch", help="Сменить активный профиль")
    p_switch.add_argument("name", help="Имя профиля")

    p_remove = sub.add_parser("remove", help="Удалить профиль")
    p_remove.add_argument("name", help="Имя профиля")

    args = parser.parse_args()

    handlers = {
        "list": cmd_list,
        "current": cmd_current,
        "show": cmd_show,
        "switch": cmd_switch,
        "remove": cmd_remove,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
