"""Tests for jira_search.py — JQL scoping and payload formation."""

import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

from jira_search import has_project_clause, scope_jql_to_project  # noqa: E402


class HasProjectClauseTests(unittest.TestCase):
    def test_detects_project_equals(self):
        self.assertTrue(has_project_clause("project=OV"))
        self.assertTrue(has_project_clause("project = OV"))
        self.assertTrue(has_project_clause('project="OV"'))
        self.assertTrue(has_project_clause("PROJECT=OV"))

    def test_detects_project_in(self):
        self.assertTrue(has_project_clause("project IN (OV, SN)"))
        self.assertTrue(has_project_clause("project in (OV)"))
        self.assertTrue(has_project_clause("project NOT IN (OV)"))

    def test_detects_project_not_equals(self):
        self.assertTrue(has_project_clause("project != OV"))

    def test_no_clause(self):
        self.assertFalse(has_project_clause("assignee=currentUser()"))
        self.assertFalse(has_project_clause("status='In Progress'"))
        self.assertFalse(has_project_clause(""))

    def test_not_confused_by_substring(self):
        # "projectlead" or fields containing "project" should not match
        self.assertFalse(has_project_clause("summary ~ 'project'"))


class ScopeJqlTests(unittest.TestCase):
    def test_wraps_plain_jql(self):
        self.assertEqual(
            scope_jql_to_project("assignee=currentUser()", "OV"),
            'project = "OV" AND (assignee=currentUser())',
        )

    def test_keeps_explicit_project(self):
        result = scope_jql_to_project("project=SN AND status=Done", "OV")
        self.assertEqual(result, "project=SN AND status=Done")

    def test_empty_jql_becomes_project_only(self):
        self.assertEqual(scope_jql_to_project("", "OV"), 'project = "OV"')
        self.assertEqual(scope_jql_to_project("   ", "OV"), 'project = "OV"')


def _run_with_capture(argv: list[str], project_key: str = "OV"):
    """Helper: run jira_search.main() with mocks and capture the JQL sent to API."""
    from lib.auth import BoardCredentials
    import jira_search

    creds = BoardCredentials(
        name="t", url="https://x", project_key=project_key, board_id=1,
        email="e", token="T",
    )
    with patch("lib.client.load_creds", return_value=creds):
        with patch("lib.client.requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            fake_resp = MagicMock(status_code=200, content=b'{"issues":[]}')
            fake_resp.json.return_value = {"issues": []}
            fake_resp.url = "https://x/search/jql"
            mock_session.get.return_value = fake_resp
            mock_session_cls.return_value = mock_session

            with patch.object(sys, "argv", argv):
                captured = StringIO()
                with patch.object(sys, "stdout", captured):
                    rc = jira_search.main()

            _, kwargs = mock_session.get.call_args
            return rc, kwargs


class SearchScriptTests(unittest.TestCase):
    def test_default_scopes_to_active_project(self):
        rc, kwargs = _run_with_capture(
            ["jira_search.py", "assignee=currentUser()"], project_key="OV"
        )
        self.assertEqual(rc, 0)
        self.assertEqual(
            kwargs["params"]["jql"],
            'project = "OV" AND (assignee=currentUser())',
        )

    def test_all_projects_flag_disables_scoping(self):
        rc, kwargs = _run_with_capture(
            ["jira_search.py", "--all-projects", "assignee=currentUser()"],
            project_key="OV",
        )
        self.assertEqual(rc, 0)
        self.assertEqual(kwargs["params"]["jql"], "assignee=currentUser()")

    def test_explicit_project_left_untouched(self):
        rc, kwargs = _run_with_capture(
            ["jira_search.py", "project=SN AND status=Done"], project_key="OV"
        )
        self.assertEqual(rc, 0)
        self.assertEqual(kwargs["params"]["jql"], "project=SN AND status=Done")


if __name__ == "__main__":
    unittest.main()
