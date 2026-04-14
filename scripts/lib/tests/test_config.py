"""Тесты lib/config.py."""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Добавляем родительскую директорию scripts/ в path
THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent.parent  # ../../../
sys.path.insert(0, str(SCRIPTS))

from lib.config import (  # noqa: E402
    find_config,
    get_active_board,
    load_config,
    resolve_location,
    save_config,
    set_active_board,
)


def _write_config(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class _IsolateGlobalConfig:
    """Контекст: отключает upward search и редиректит global на nonexistent path."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self._old_env = {}

    def __enter__(self):
        self._old_env["JIRA_SKILL_NO_UPWARD_SEARCH"] = os.environ.get(
            "JIRA_SKILL_NO_UPWARD_SEARCH"
        )
        self._old_env["JIRA_SKILL_GLOBAL_CONFIG"] = os.environ.get(
            "JIRA_SKILL_GLOBAL_CONFIG"
        )
        os.environ["JIRA_SKILL_NO_UPWARD_SEARCH"] = "1"
        os.environ["JIRA_SKILL_GLOBAL_CONFIG"] = str(self.tmp / "_no_global_.json")
        return self

    def __exit__(self, *args):
        for k, v in self._old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class FindConfigTests(unittest.TestCase):
    def test_finds_local_config_in_cwd(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            local = root / ".claude" / "skills" / "jira" / "config.json"
            _write_config(local, {"active_board": "hornyvilla"})

            with _IsolateGlobalConfig(root):
                found = find_config(start=root)
                self.assertEqual(found, local)

    def test_finds_local_config_in_parent(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sub = root / "src" / "nested" / "deep"
            sub.mkdir(parents=True)
            local = root / ".claude" / "skills" / "jira" / "config.json"
            _write_config(local, {"active_board": "other"})

            # Здесь нужен upward search, но изолируем глобальный
            old_env = os.environ.get("JIRA_SKILL_GLOBAL_CONFIG")
            os.environ["JIRA_SKILL_GLOBAL_CONFIG"] = str(root / "_no_global_.json")
            try:
                # Тоже отключаем upward за пределы tmpdir — иначе найдёт реальный global
                # Способ: убедиться что путь до tmp короткий и в нём только local
                # Но проще — патчим _global_config_path
                found = find_config(start=sub)
                self.assertEqual(found, local)
            finally:
                if old_env is None:
                    os.environ.pop("JIRA_SKILL_GLOBAL_CONFIG", None)
                else:
                    os.environ["JIRA_SKILL_GLOBAL_CONFIG"] = old_env

    def test_falls_back_to_global(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_global = root / "fake_global_config.json"
            _write_config(fake_global, {"active_board": "global"})

            old_env = {
                "JIRA_SKILL_NO_UPWARD_SEARCH": os.environ.get("JIRA_SKILL_NO_UPWARD_SEARCH"),
                "JIRA_SKILL_GLOBAL_CONFIG": os.environ.get("JIRA_SKILL_GLOBAL_CONFIG"),
            }
            os.environ["JIRA_SKILL_NO_UPWARD_SEARCH"] = "1"
            os.environ["JIRA_SKILL_GLOBAL_CONFIG"] = str(fake_global)
            try:
                found = find_config(start=root)
                self.assertEqual(found, fake_global)
            finally:
                for k, v in old_env.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v

    def test_returns_none_when_nothing_exists(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with _IsolateGlobalConfig(root):
                found = find_config(start=root)
                self.assertIsNone(found)


class LoadConfigTests(unittest.TestCase):
    def test_loads_valid_json(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            _write_config(path, {"active_board": "test"})

            data = load_config(path)
            self.assertEqual(data, {"active_board": "test"})

    def test_raises_on_missing_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nonexistent.json"
            with _IsolateGlobalConfig(Path(tmp)):
                with self.assertRaises(FileNotFoundError):
                    load_config(path)

    def test_raises_on_invalid_json(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text("not a json {", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_config(path)


class SaveConfigTests(unittest.TestCase):
    def test_saves_and_creates_parent_dirs(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sub" / "dir" / "config.json"
            result = save_config({"active_board": "x"}, path)

            self.assertEqual(result, path)
            self.assertTrue(path.is_file())
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"active_board": "x"},
            )


class ActiveBoardTests(unittest.TestCase):
    def test_get_returns_name(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            _write_config(path, {"active_board": "hornyvilla"})

            self.assertEqual(get_active_board(path), "hornyvilla")

    def test_get_returns_none_when_missing(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nonexistent.json"
            with _IsolateGlobalConfig(Path(tmp)):
                self.assertIsNone(get_active_board(path))

    def test_set_preserves_other_fields(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            _write_config(path, {"active_board": "old", "other": "preserved"})

            set_active_board("new", path)

            data = load_config(path)
            self.assertEqual(data["active_board"], "new")
            self.assertEqual(data["other"], "preserved")


class ResolveLocationTests(unittest.TestCase):
    def test_global_location(self):
        path = resolve_location("global")
        self.assertEqual(path.name, "jira")
        self.assertIn("skills", str(path))

    def test_local_location_is_in_cwd(self):
        path = resolve_location("local")
        self.assertTrue(str(path).startswith(str(Path.cwd())))
        self.assertIn(".claude", str(path))

    def test_invalid_location_raises(self):
        with self.assertRaises(ValueError):
            resolve_location("invalid")


if __name__ == "__main__":
    unittest.main()
