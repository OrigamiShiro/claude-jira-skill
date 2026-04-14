"""Тесты jira_worklog.py."""

import re
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

from jira_worklog import (  # noqa: E402
    build_worklog_payload,
    cmd_add,
    make_adf,
    now_jira_format,
)


class NowJiraFormatTests(unittest.TestCase):
    def test_format_matches(self):
        s = now_jira_format()
        # 2026-04-14T15:00:00.000+0000
        self.assertRegex(s, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.000\+0000")


class BuildWorklogPayloadTests(unittest.TestCase):
    def test_minimal(self):
        p = build_worklog_payload("3h", None, None)
        self.assertEqual(p["timeSpent"], "3h")
        self.assertIn("started", p)
        self.assertNotIn("comment", p)

    def test_with_comment(self):
        p = build_worklog_payload("1h", "test comment", None)
        self.assertIn("comment", p)
        adf = p["comment"]
        self.assertEqual(adf["type"], "doc")
        self.assertEqual(adf["content"][0]["content"][0]["text"], "test comment")

    def test_with_started_override(self):
        p = build_worklog_payload("1h", None, "2026-04-14T10:00:00.000+0000")
        self.assertEqual(p["started"], "2026-04-14T10:00:00.000+0000")


class CmdAddTests(unittest.TestCase):
    def test_posts_correct_endpoint(self):
        client = MagicMock()
        client.post.return_value = {"id": "999"}
        args = MagicMock(key="PROJ-1", time="2h", comment="x", started=None)
        cmd_add(args, client)

        call_args, call_kwargs = client.post.call_args
        self.assertEqual(call_args[0], "/rest/api/3/issue/PROJ-1/worklog")
        self.assertEqual(call_kwargs["json"]["timeSpent"], "2h")


if __name__ == "__main__":
    unittest.main()
