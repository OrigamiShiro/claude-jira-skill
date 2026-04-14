"""Тесты jira_batch.py."""

import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

from jira_batch import OP_HANDLERS, execute, load_ops, op_link  # noqa: E402


class LoadOpsTests(unittest.TestCase):
    def test_from_stdin(self):
        data = [{"op": "transition", "key": "PROJ-1", "status": "Done"}]
        with patch("sys.stdin", io.StringIO(json.dumps(data))):
            result = load_ops(None)
        self.assertEqual(result, data)

    def test_invalid_not_array(self):
        with patch("sys.stdin", io.StringIO('{"not": "array"}')):
            with self.assertRaises(ValueError):
                load_ops(None)


class ExecuteTests(unittest.TestCase):
    def test_unknown_op_counts_as_fail(self):
        client = MagicMock()
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            ok, fail = execute(client, [{"op": "ghost", "key": "X"}])
        self.assertEqual(ok, 0)
        self.assertEqual(fail, 1)
        self.assertIn("Unknown op", captured.getvalue())

    def test_continues_after_error(self):
        client = MagicMock()
        # transition требует find_transition_id → mock client.get
        client.get.return_value = {"transitions": []}
        ops = [
            {"op": "transition", "key": "PROJ-1", "status": "Ghost"},  # fail
            {"op": "assign", "key": "PROJ-2", "account_id": "abc"},  # ok
        ]
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            ok, fail = execute(client, ops)

        self.assertEqual(ok, 1)
        self.assertEqual(fail, 1)


class OpLinkTests(unittest.TestCase):
    def test_resolves_alias(self):
        client = MagicMock()
        op = {"inward": "PROJ-1", "outward": "PROJ-2", "type": "parent-child"}
        op_link(client, op)
        call_args, call_kwargs = client.post.call_args
        self.assertEqual(call_args[0], "/rest/api/3/issueLink")
        self.assertEqual(call_kwargs["json"]["type"]["id"], "10007")


class HandlersCoverageTests(unittest.TestCase):
    def test_all_expected_handlers_exist(self):
        expected = {"transition", "worklog", "link", "assign", "unassign", "delete"}
        self.assertEqual(set(OP_HANDLERS.keys()), expected)


if __name__ == "__main__":
    unittest.main()
