"""
Управление config.json скилла.

Поиск config:
  1. Локальный: .claude/skills/jira/config.json вверх по дереву от CWD
  2. Глобальный: ~/.claude/skills/jira/config.json

Структура config.json:
{
  "active_board": "hornyvilla",
  "location": "global" | "local"
}
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

log = logging.getLogger("jira-skill.config")

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


LOCAL_CONFIG_SUBPATH = Path(".claude") / "skills" / "jira" / "config.json"
GLOBAL_CONFIG_DIR = Path.home() / ".claude" / "skills" / "jira"
GLOBAL_CONFIG_PATH = GLOBAL_CONFIG_DIR / "config.json"


def _global_config_path() -> Path:
    """Глобальный config — учитывает env override JIRA_SKILL_GLOBAL_CONFIG (для тестов/изоляции)."""
    override = os.environ.get("JIRA_SKILL_GLOBAL_CONFIG")
    if override:
        return Path(override)
    return GLOBAL_CONFIG_PATH


def find_config(start: Optional[Path] = None) -> Optional[Path]:
    """
    Ищет config.json.

    Сначала проверяет локальные: .claude/skills/jira/config.json
    от start (или CWD) вверх по дереву до корня.
    Затем — глобальный: ~/.claude/skills/jira/config.json.

    Env-флаг JIRA_SKILL_NO_UPWARD_SEARCH=1 отключает upward search
    (нужно для тестовой изоляции — иначе тесты подхватывают глобальный
    config через дерево, если tmpdir внутри HOME).

    Возвращает Path к найденному файлу или None.
    """
    no_upward = os.environ.get("JIRA_SKILL_NO_UPWARD_SEARCH") == "1"
    current = (start or Path.cwd()).resolve()
    while True:
        candidate = current / LOCAL_CONFIG_SUBPATH
        if candidate.is_file():
            return candidate
        if no_upward or current.parent == current:
            break
        current = current.parent

    global_path = _global_config_path()
    if global_path.is_file():
        return global_path

    return None


def config_dir(config_path: Path) -> Path:
    """Директория, в которой лежит config.json (с подпапками boards/, creds/)."""
    return config_path.parent


def load_config(config_path: Optional[Path] = None) -> dict:
    """
    Загружает config.json. Если путь не передан — ищет через find_config.
    Возвращает dict. Если файл отсутствует или повреждён — возбуждает исключение.
    """
    path = config_path or find_config()
    if path is None:
        raise FileNotFoundError(
            "config.json не найден. Запусти jira_init.py для первичной настройки."
        )
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log.error("Повреждённый config.json: %s", path)
        raise ValueError(f"Повреждённый config.json: {path} ({e})") from e
    return data


def save_config(data: dict, config_path: Optional[Path] = None) -> Path:
    """
    Сохраняет config.json. Если путь не передан — ищет существующий,
    либо пишет в глобальный.
    """
    path = config_path or find_config() or _global_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def get_active_board(config_path: Optional[Path] = None) -> Optional[str]:
    """Возвращает имя активной борды из config.json или None."""
    try:
        data = load_config(config_path)
    except FileNotFoundError:
        return None
    return data.get("active_board")


def set_active_board(name: str, config_path: Optional[Path] = None) -> Path:
    """Устанавливает active_board в config.json. Остальные поля сохраняет."""
    path = config_path or find_config() or _global_config_path()
    data: dict = {}
    if path.is_file():
        try:
            data = load_config(path)
        except (FileNotFoundError, ValueError):
            data = {}
    data["active_board"] = name
    return save_config(data, path)


def resolve_location(location: str) -> Path:
    """
    Преобразует location ('local'/'global') в путь к директории skill-конфига.

    local  → CWD / .claude / skills / jira
    global → ~/.claude/skills/jira
    """
    location = location.lower()
    if location == "local":
        return Path.cwd() / ".claude" / "skills" / "jira"
    if location == "global":
        return GLOBAL_CONFIG_DIR
    raise ValueError(f"Unknown location: {location!r} (expected 'local' or 'global')")
