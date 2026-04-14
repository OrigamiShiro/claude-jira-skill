"""Тесты jira_search.py — формирование запроса (mock)."""

import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))


class SearchScriptTests(unittest.TestCase):
    def test_calls_jql_endpoint(self):
        # Запускаем main() с mock JiraClient
        from lib.auth import BoardCredentials
        import jira_search

        creds = BoardCredentials(
            name="t", url="https://x", project_key="P", board_id=1,
            email="e", token="T",
        )
        with patch("lib.client.load_creds", return_value=creds):
            with patch("lib.client.requests.Session") as mock_session_cls:
                mock_session = MagicMock()
                fake_resp = MagicMock(
                    status_code=200,
                    content=b'{"issues":[]}',
                )
                fake_resp.json.return_value = {"issues": []}
                fake_resp.url = "https://x/search/jql"
                mock_session.get.return_value = fake_resp
                mock_session_cls.return_value = mock_session

                with patch.object(
                    sys, "argv", ["jira_search.py", "project=HOR"]
                ):
                    captured = StringIO()
                    with patch.object(sys, "stdout", captured):
                        rc = jira_search.main()

                self.assertEqual(rc, 0)
                # Проверяем: GET был в /rest/api/3/search/jql с jql параметром
                _, kwargs = mock_session.get.call_args
                self.assertIn("/rest/api/3/search/jql", mock_session.get.call_args[0][0])
                self.assertEqual(kwargs["params"]["jql"], "project=HOR")
                self.assertEqual(kwargs["params"]["maxResults"], 50)


if __name__ == "__main__":
    unittest.main()
