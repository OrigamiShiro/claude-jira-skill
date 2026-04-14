"""Тесты jira_link.py."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

from jira_link import LINK_TYPE_ALIASES, cmd_add, cmd_list, resolve_type_id  # noqa: E402


class ResolveTypeIdTests(unittest.TestCase):
    def test_alias(self):
        self.assertEqual(resolve_type_id("parent-child"), "10007")
        self.assertEqual(resolve_type_id("blocks"), "10000")
        self.assertEqual(resolve_type_id("relates"), "10003")

    def test_case_insensitive(self):
        self.assertEqual(resolve_type_id("PARENT-CHILD"), "10007")

    def test_passthrough_id(self):
        self.assertEqual(resolve_type_id("99999"), "99999")

    def test_aliases_complete(self):
        for alias in ["parent-child", "blocks", "relates", "duplicate", "cloners"]:
            self.assertIn(alias, LINK_TYPE_ALIASES)


class CmdAddTests(unittest.TestCase):
    def test_posts_correct_payload(self):
        client = MagicMock()
        args = MagicMock(inward="PROJ-1", outward="PROJ-2", type="parent-child")
        cmd_add(args, client)

        client.post.assert_called_once()
        call_args, call_kwargs = client.post.call_args
        self.assertEqual(call_args[0], "/rest/api/3/issueLink")
        payload = call_kwargs["json"]
        self.assertEqual(payload["type"]["id"], "10007")
        self.assertEqual(payload["inwardIssue"]["key"], "PROJ-1")
        self.assertEqual(payload["outwardIssue"]["key"], "PROJ-2")


class CmdListTests(unittest.TestCase):
    def test_displays_correct_verbs(self):
        """При просмотре inwardIssue=focal: показывает outward verb для other."""
        client = MagicMock()
        client.get.return_value = {
            "fields": {
                "issuelinks": [
                    {
                        "id": "100",
                        "type": {"inward": "is child of", "outward": "is parent of"},
                        "outwardIssue": {"key": "PROJ-PARENT"},
                    },
                    {
                        "id": "200",
                        "type": {"inward": "is blocked by", "outward": "blocks"},
                        "inwardIssue": {"key": "PROJ-BLOCKED"},
                    },
                ]
            }
        }
        args = MagicMock(key="PROJ-FOCAL")

        # Перехватываем print через io
        from io import StringIO
        from unittest.mock import patch

        captured = StringIO()
        with patch("sys.stdout", captured):
            cmd_list(args, client)

        output = captured.getvalue()
        # focal — outwardIssue в первом link → она inwardIssue, имеет inward verb к other
        self.assertIn("is child of PROJ-PARENT", output)
        # focal — inwardIssue во втором link → она outwardIssue, имеет outward verb к other
        self.assertIn("blocks PROJ-BLOCKED", output)


if __name__ == "__main__":
    unittest.main()
