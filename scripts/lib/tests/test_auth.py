"""Тесты lib/auth.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent.parent
sys.path.insert(0, str(SCRIPTS))

from lib.auth import (  # noqa: E402
    BoardCredentials,
    list_boards,
    load_board_info,
    load_creds,
    load_creds_file,
    mask_token,
)


def _make_skill_dir(tmp: Path, board_name: str, board_data: dict, creds_data: dict) -> Path:
    skill = tmp / "skill"
    (skill / "boards").mkdir(parents=True)
    (skill / "creds").mkdir(parents=True)
    (skill / "boards" / f"{board_name}.json").write_text(
        json.dumps(board_data), encoding="utf-8"
    )
    (skill / "creds" / f"{board_name}.json").write_text(
        json.dumps(creds_data), encoding="utf-8"
    )
    return skill


class MaskTokenTests(unittest.TestCase):
    def test_short_token(self):
        self.assertEqual(mask_token("abc"), "***")
        self.assertEqual(mask_token("12345678"), "***")

    def test_long_token(self):
        self.assertEqual(mask_token("ATATT3xFfG0pSM"), "ATAT...0pSM")

    def test_empty(self):
        self.assertEqual(mask_token(""), "")


class LoadBoardInfoTests(unittest.TestCase):
    def test_loads_existing_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = _make_skill_dir(
                Path(tmp),
                "myboard",
                {"url": "https://x.atlassian.net", "project_key": "HOR", "board_id": 153},
                {"email": "u@e.com", "token": "t"},
            )
            data = load_board_info("myboard", skill_dir=skill)
            self.assertEqual(data["project_key"], "HOR")

    def test_raises_on_missing_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "boards").mkdir(parents=True)
            with self.assertRaises(FileNotFoundError):
                load_board_info("ghost", skill_dir=skill)

    def test_raises_on_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "boards").mkdir(parents=True)
            (skill / "boards" / "bad.json").write_text("not json{", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_board_info("bad", skill_dir=skill)


class LoadCredsFileTests(unittest.TestCase):
    def test_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "creds").mkdir(parents=True)
            (skill / "creds" / "x.json").write_text(
                json.dumps({"email": "a@b", "token": "T"}), encoding="utf-8"
            )
            data = load_creds_file("x", skill_dir=skill)
            self.assertEqual(data["email"], "a@b")

    def test_missing_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "creds").mkdir(parents=True)
            with self.assertRaises(FileNotFoundError):
                load_creds_file("ghost", skill_dir=skill)


class LoadCredsTests(unittest.TestCase):
    def test_returns_board_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = _make_skill_dir(
                Path(tmp),
                "myboard",
                {"url": "https://x.atlassian.net/", "project_key": "HOR", "board_id": 153},
                {"email": "u@e.com", "token": "T"},
            )
            creds = load_creds("myboard", skill_dir=skill)
            self.assertIsInstance(creds, BoardCredentials)
            self.assertEqual(creds.base_url, "https://x.atlassian.net")
            self.assertEqual(creds.project_key, "HOR")
            self.assertEqual(creds.board_id, 153)
            self.assertEqual(creds.auth_tuple(), ("u@e.com", "T"))

    def test_missing_required_board_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = _make_skill_dir(
                Path(tmp),
                "bad",
                {"url": "https://x"},  # нет project_key, board_id
                {"email": "e", "token": "t"},
            )
            with self.assertRaises(ValueError):
                load_creds("bad", skill_dir=skill)

    def test_missing_required_creds_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = _make_skill_dir(
                Path(tmp),
                "x",
                {"url": "https://x", "project_key": "P", "board_id": 1},
                {"email": "e"},  # нет token
            )
            with self.assertRaises(ValueError):
                load_creds("x", skill_dir=skill)

    def test_uses_creds_file_override(self):
        """Если в boards указан creds_file — берём оттуда."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "boards").mkdir(parents=True)
            (skill / "creds").mkdir(parents=True)
            (skill / "boards" / "alpha.json").write_text(
                json.dumps(
                    {
                        "url": "https://x",
                        "project_key": "P",
                        "board_id": 1,
                        "creds_file": "shared",
                    }
                ),
                encoding="utf-8",
            )
            (skill / "creds" / "shared.json").write_text(
                json.dumps({"email": "e", "token": "t"}), encoding="utf-8"
            )
            creds = load_creds("alpha", skill_dir=skill)
            self.assertEqual(creds.email, "e")


class ListBoardsTests(unittest.TestCase):
    def test_lists_all_boards(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "boards").mkdir(parents=True)
            (skill / "boards" / "alpha.json").write_text("{}")
            (skill / "boards" / "beta.json").write_text("{}")
            (skill / "boards" / "notes.txt").write_text("skip me")

            result = list_boards(skill_dir=skill)
            self.assertEqual(result, ["alpha", "beta"])

    def test_returns_empty_when_no_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            self.assertEqual(list_boards(skill_dir=skill), [])


if __name__ == "__main__":
    unittest.main()
