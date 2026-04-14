"""Тесты jira_init.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

from jira_init import write_board_files  # noqa: E402


class WriteBoardFilesTests(unittest.TestCase):
    def test_creates_board_and_creds(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            write_board_files(
                skill_dir=skill,
                name="hornyvilla",
                url="https://x.atlassian.net/",
                project_key="HOR",
                board_id=153,
                email="me@e.com",
                token="T",
            )
            board = json.loads(
                (skill / "boards" / "hornyvilla.json").read_text(encoding="utf-8")
            )
            creds = json.loads(
                (skill / "creds" / "hornyvilla.json").read_text(encoding="utf-8")
            )
            self.assertEqual(board["url"], "https://x.atlassian.net")  # trailing / стрипнут
            self.assertEqual(board["project_key"], "HOR")
            self.assertEqual(board["board_id"], 153)
            self.assertEqual(creds["email"], "me@e.com")
            self.assertEqual(creds["token"], "T")

    def test_refuses_overwrite_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            write_board_files(
                skill_dir=skill,
                name="x",
                url="https://x",
                project_key="P",
                board_id=1,
                email="e",
                token="t",
            )
            with self.assertRaises(FileExistsError):
                write_board_files(
                    skill_dir=skill,
                    name="x",
                    url="https://y",
                    project_key="P",
                    board_id=2,
                    email="e",
                    token="t",
                )

    def test_overwrite_replaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            write_board_files(
                skill_dir=skill,
                name="x",
                url="https://x",
                project_key="P",
                board_id=1,
                email="e",
                token="t",
            )
            write_board_files(
                skill_dir=skill,
                name="x",
                url="https://y",
                project_key="Q",
                board_id=2,
                email="e2",
                token="t2",
                overwrite=True,
            )
            board = json.loads(
                (skill / "boards" / "x.json").read_text(encoding="utf-8")
            )
            self.assertEqual(board["url"], "https://y")
            self.assertEqual(board["project_key"], "Q")
            self.assertEqual(board["board_id"], 2)


if __name__ == "__main__":
    unittest.main()
