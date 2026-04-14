"""Тесты lib/client.py."""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent.parent
sys.path.insert(0, str(SCRIPTS))

from lib.auth import BoardCredentials  # noqa: E402
from lib.client import (  # noqa: E402
    JiraAuthError,
    JiraClient,
    JiraError,
    JiraNotFoundError,
)


def _creds() -> BoardCredentials:
    return BoardCredentials(
        name="test",
        url="https://example.atlassian.net",
        project_key="TEST",
        board_id=1,
        email="u@e.com",
        token="T",
    )


def _mock_response(status_code: int, json_data=None, text: str = ""):
    response = MagicMock()
    response.status_code = status_code
    response.url = "https://example.atlassian.net/rest/api/3/fake"
    response.content = b"x" if status_code != 204 else b""
    if json_data is not None:
        response.json.return_value = json_data
        response.text = str(json_data)
    else:
        response.json.side_effect = ValueError("not json")
        response.text = text
    return response


class JiraClientInitTests(unittest.TestCase):
    def test_init_without_active_board_raises(self):
        with patch("lib.client.get_active_board", return_value=None):
            with self.assertRaises(JiraError):
                JiraClient()

    def test_init_uses_explicit_board(self):
        with patch("lib.client.load_creds", return_value=_creds()):
            client = JiraClient(board_name="test")
            self.assertEqual(client.project_key, "TEST")
            self.assertEqual(client.board_id, 1)
            self.assertEqual(client.base_url, "https://example.atlassian.net")


class JiraClientFullUrlTests(unittest.TestCase):
    def setUp(self):
        with patch("lib.client.load_creds", return_value=_creds()):
            self.client = JiraClient(board_name="test")

    def test_path_with_slash(self):
        self.assertEqual(
            self.client._full_url("/rest/api/3/myself"),
            "https://example.atlassian.net/rest/api/3/myself",
        )

    def test_path_without_slash(self):
        self.assertEqual(
            self.client._full_url("rest/api/3/myself"),
            "https://example.atlassian.net/rest/api/3/myself",
        )

    def test_full_url_passthrough(self):
        url = "https://other.com/endpoint"
        self.assertEqual(self.client._full_url(url), url)


class HandleResponseTests(unittest.TestCase):
    def setUp(self):
        with patch("lib.client.load_creds", return_value=_creds()):
            self.client = JiraClient(board_name="test")

    def test_401_raises_auth_error(self):
        resp = _mock_response(401, text="bad creds")
        with self.assertRaises(JiraAuthError):
            self.client._handle_response(resp)

    def test_403_raises_auth_error(self):
        resp = _mock_response(403, text="forbidden")
        with self.assertRaises(JiraAuthError):
            self.client._handle_response(resp)

    def test_404_raises_not_found(self):
        resp = _mock_response(404, text="not found")
        with self.assertRaises(JiraNotFoundError):
            self.client._handle_response(resp)

    def test_500_raises_generic(self):
        resp = _mock_response(500, text="server error")
        with self.assertRaises(JiraError):
            self.client._handle_response(resp)

    def test_200_returns_json(self):
        resp = _mock_response(200, json_data={"key": "PROJ-1"})
        self.assertEqual(self.client._handle_response(resp), {"key": "PROJ-1"})

    def test_204_returns_none(self):
        resp = _mock_response(204)
        resp.content = b""
        self.assertIsNone(self.client._handle_response(resp))


class HttpVerbsTests(unittest.TestCase):
    def setUp(self):
        with patch("lib.client.load_creds", return_value=_creds()):
            self.client = JiraClient(board_name="test")

    def test_get_calls_session(self):
        with patch.object(self.client._session, "get") as mock_get:
            mock_get.return_value = _mock_response(200, json_data={"ok": True})
            result = self.client.get("/rest/api/3/test", params={"a": 1})

            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            self.assertEqual(args[0], "https://example.atlassian.net/rest/api/3/test")
            self.assertEqual(kwargs["params"], {"a": 1})
            self.assertEqual(result, {"ok": True})

    def test_post_sends_json(self):
        with patch.object(self.client._session, "post") as mock_post:
            mock_post.return_value = _mock_response(201, json_data={"id": "1"})
            self.client.post("/rest/api/3/issue", json={"summary": "x"})

            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs["json"], {"summary": "x"})

    def test_delete_calls_session(self):
        with patch.object(self.client._session, "delete") as mock_delete:
            mock_delete.return_value = _mock_response(204)
            result = self.client.delete("/rest/api/3/issue/PROJ-1")
            self.assertIsNone(result)

    def test_myself_helper(self):
        with patch.object(self.client._session, "get") as mock_get:
            mock_get.return_value = _mock_response(
                200, json_data={"displayName": "me"}
            )
            result = self.client.myself()
            self.assertEqual(result["displayName"], "me")

    def test_browse_url(self):
        self.assertEqual(
            self.client.browse_url("PROJ-42"),
            "https://example.atlassian.net/browse/PROJ-42",
        )


if __name__ == "__main__":
    unittest.main()
