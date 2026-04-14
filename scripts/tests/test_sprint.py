"""Тесты jira_sprint.py."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

from jira_sprint import (  # noqa: E402
    cmd_complete,
    cmd_create,
    cmd_list,
    cmd_move,
    cmd_start,
)


def _make_client(board_id: int = 153):
    client = MagicMock()
    client.board_id = board_id
    return client


class CmdListTests(unittest.TestCase):
    def test_uses_client_board_id(self):
        client = _make_client(99)
        client.get.return_value = {"values": []}
        args = MagicMock(state=None, board_id=None)
        cmd_list(args, client)

        call_args, _ = client.get.call_args
        self.assertEqual(call_args[0], "/rest/agile/1.0/board/99/sprint")

    def test_uses_arg_board_id(self):
        client = _make_client(99)
        client.get.return_value = {"values": []}
        args = MagicMock(state="active", board_id=42)
        cmd_list(args, client)

        call_args, call_kwargs = client.get.call_args
        self.assertEqual(call_args[0], "/rest/agile/1.0/board/42/sprint")
        self.assertEqual(call_kwargs["params"], {"state": "active"})


class CmdCreateTests(unittest.TestCase):
    def test_minimal(self):
        client = _make_client(153)
        client.post.return_value = {"id": 100}
        # MagicMock.name — особый атрибут; задаём явно
        args = MagicMock(goal=None, start=None, end=None, board_id=None)
        args.name = "Sprint X"
        cmd_create(args, client)

        call_args, call_kwargs = client.post.call_args
        self.assertEqual(call_args[0], "/rest/agile/1.0/sprint")
        self.assertEqual(
            call_kwargs["json"], {"name": "Sprint X", "originBoardId": 153}
        )

    def test_with_optional(self):
        client = _make_client(153)
        client.post.return_value = {"id": 100}
        args = MagicMock(
            goal="goal", start="2026-04-14", end="2026-04-28",
            board_id=None,
        )
        args.name = "X"
        cmd_create(args, client)
        payload = client.post.call_args[1]["json"]
        self.assertEqual(payload["goal"], "goal")
        self.assertEqual(payload["startDate"], "2026-04-14")
        self.assertEqual(payload["endDate"], "2026-04-28")


class CmdMoveTests(unittest.TestCase):
    def test_posts_issues_array(self):
        client = _make_client()
        args = MagicMock(sprint_id=17, keys=["PROJ-1", "PROJ-2"])
        cmd_move(args, client)

        call_args, call_kwargs = client.post.call_args
        self.assertEqual(call_args[0], "/rest/agile/1.0/sprint/17/issue")
        self.assertEqual(call_kwargs["json"], {"issues": ["PROJ-1", "PROJ-2"]})


class CmdStartCompleteTests(unittest.TestCase):
    def test_start_active(self):
        client = _make_client()
        args = MagicMock(sprint_id=17, start=None, end=None)
        cmd_start(args, client)
        payload = client.post.call_args[1]["json"]
        self.assertEqual(payload["state"], "active")

    def test_complete_closed(self):
        client = _make_client()
        args = MagicMock(sprint_id=17)
        cmd_complete(args, client)
        payload = client.post.call_args[1]["json"]
        self.assertEqual(payload["state"], "closed")


if __name__ == "__main__":
    unittest.main()
