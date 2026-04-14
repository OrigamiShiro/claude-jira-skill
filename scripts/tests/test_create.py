"""Тесты jira_create.py — формирование payload."""

import sys
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

from jira_create import build_payload, make_adf  # noqa: E402


class MakeADFTests(unittest.TestCase):
    def test_wraps_text(self):
        adf = make_adf("hello")
        self.assertEqual(adf["type"], "doc")
        self.assertEqual(adf["version"], 1)
        self.assertEqual(
            adf["content"][0]["content"][0]["text"], "hello"
        )


class BuildPayloadTests(unittest.TestCase):
    def test_minimal(self):
        p = build_payload("HOR", "Test", "Задача")
        self.assertEqual(p["fields"]["project"], {"key": "HOR"})
        self.assertEqual(p["fields"]["summary"], "Test")
        self.assertEqual(p["fields"]["issuetype"], {"name": "Задача"})
        self.assertNotIn("description", p["fields"])
        self.assertNotIn("assignee", p["fields"])

    def test_with_description(self):
        p = build_payload("HOR", "T", "Задача", description="desc text")
        self.assertIn("description", p["fields"])
        self.assertEqual(
            p["fields"]["description"]["content"][0]["content"][0]["text"],
            "desc text",
        )

    def test_with_assignee(self):
        p = build_payload("HOR", "T", "Задача", assignee="712020:abc")
        self.assertEqual(p["fields"]["assignee"], {"accountId": "712020:abc"})

    def test_full(self):
        p = build_payload(
            "HOR", "T", "Баг", description="why", assignee="712020:x"
        )
        self.assertEqual(p["fields"]["issuetype"], {"name": "Баг"})
        self.assertIn("description", p["fields"])
        self.assertIn("assignee", p["fields"])


if __name__ == "__main__":
    unittest.main()
