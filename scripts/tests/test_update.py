"""Тесты jira_update.py — find_transition_id и cmd_field."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

from jira_update import cmd_field, find_transition_id  # noqa: E402


class FindTransitionTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.get.return_value = {
            "transitions": [
                {"id": "10", "name": "В работу", "to": {"name": "В работе"}},
                {"id": "20", "name": "Завершить", "to": {"name": "Готово"}},
            ]
        }

    def test_match_by_transition_name(self):
        self.assertEqual(find_transition_id(self.client, "HOR-1", "В работу"), "10")

    def test_match_by_target_status(self):
        self.assertEqual(find_transition_id(self.client, "HOR-1", "Готово"), "20")

    def test_case_insensitive(self):
        self.assertEqual(find_transition_id(self.client, "HOR-1", "ГОТОВО"), "20")

    def test_returns_none_when_missing(self):
        self.assertIsNone(find_transition_id(self.client, "HOR-1", "Несуществует"))


class CmdFieldTests(unittest.TestCase):
    def test_summary_field_passes_string(self):
        client = MagicMock()
        args = MagicMock()
        args.key = "HOR-1"
        args.field = "summary"
        args.value = "New title"

        cmd_field(args, client)

        client.put.assert_called_once()
        call_args, call_kwargs = client.put.call_args
        self.assertEqual(call_args[0], "/rest/api/3/issue/HOR-1")
        self.assertEqual(
            call_kwargs["json"], {"fields": {"summary": "New title"}}
        )

    def test_description_wraps_in_adf(self):
        client = MagicMock()
        args = MagicMock()
        args.key = "HOR-1"
        args.field = "description"
        args.value = "new desc"

        cmd_field(args, client)

        call_args, call_kwargs = client.put.call_args
        desc = call_kwargs["json"]["fields"]["description"]
        self.assertEqual(desc["type"], "doc")
        self.assertEqual(desc["content"][0]["content"][0]["text"], "new desc")


if __name__ == "__main__":
    unittest.main()
