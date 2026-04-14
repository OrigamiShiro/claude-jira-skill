"""
Загрузка креденшиалов для борды.

Структура:
  <skill-dir>/boards/<name>.json  — {url, project_key, board_id, creds_file}
  <skill-dir>/creds/<name>.json   — {email, token}
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import config_dir, find_config

log = logging.getLogger("jira-skill.auth")


@dataclass
class BoardCredentials:
    """Полный набор данных для работы с бордой."""

    name: str
    url: str
    project_key: str
    board_id: int
    email: str
    token: str

    @property
    def base_url(self) -> str:
        """Базовый URL без хвостовых слешей."""
        return self.url.rstrip("/")

    def auth_tuple(self) -> tuple[str, str]:
        """Для requests.auth=HTTPBasicAuth(...) или auth=(email, token)."""
        return (self.email, self.token)


def mask_token(token: str) -> str:
    """Маскирует API токен для безопасного вывода."""
    if not token:
        return ""
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


def load_board_info(name: str, skill_dir: Optional[Path] = None) -> dict:
    """Читает boards/<name>.json."""
    if skill_dir is None:
        cfg = find_config()
        if cfg is None:
            raise FileNotFoundError(
                "config.json не найден. Запусти jira_init.py."
            )
        skill_dir = config_dir(cfg)

    board_file = skill_dir / "boards" / f"{name}.json"
    if not board_file.is_file():
        raise FileNotFoundError(f"Профиль борды не найден: {board_file}")

    try:
        with board_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Повреждённый файл борды: {board_file} ({e})") from e


def load_creds_file(name: str, skill_dir: Optional[Path] = None) -> dict:
    """Читает creds/<name>.json."""
    if skill_dir is None:
        cfg = find_config()
        if cfg is None:
            raise FileNotFoundError(
                "config.json не найден. Запусти jira_init.py."
            )
        skill_dir = config_dir(cfg)

    creds_file = skill_dir / "creds" / f"{name}.json"
    if not creds_file.is_file():
        raise FileNotFoundError(f"Креды для борды не найдены: {creds_file}")

    try:
        with creds_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Повреждённый creds файл: {creds_file} ({e})") from e


def load_creds(
    board_name: str, skill_dir: Optional[Path] = None
) -> BoardCredentials:
    """
    Возвращает полные креденшиалы для борды.

    board_name: имя профиля (ключ файла boards/<name>.json)
    skill_dir:  путь к директории скилла (где лежат boards/ и creds/);
                если None — определяется через find_config()
    """
    board = load_board_info(board_name, skill_dir)
    creds_file_name = board.get("creds_file", board_name)
    creds = load_creds_file(creds_file_name, skill_dir)

    required_board = ("url", "project_key", "board_id")
    missing_board = [k for k in required_board if k not in board]
    if missing_board:
        raise ValueError(
            f"В файле борды '{board_name}' не хватает полей: {missing_board}"
        )

    required_creds = ("email", "token")
    missing_creds = [k for k in required_creds if k not in creds]
    if missing_creds:
        raise ValueError(
            f"В creds файле '{creds_file_name}' не хватает полей: {missing_creds}"
        )

    return BoardCredentials(
        name=board_name,
        url=board["url"],
        project_key=board["project_key"],
        board_id=int(board["board_id"]),
        email=creds["email"],
        token=creds["token"],
    )


def list_boards(skill_dir: Optional[Path] = None) -> list[str]:
    """Возвращает список имён профилей (по файлам boards/*.json)."""
    if skill_dir is None:
        cfg = find_config()
        if cfg is None:
            return []
        skill_dir = config_dir(cfg)

    boards_dir = skill_dir / "boards"
    if not boards_dir.is_dir():
        return []

    return sorted(
        p.stem for p in boards_dir.glob("*.json") if p.is_file()
    )
