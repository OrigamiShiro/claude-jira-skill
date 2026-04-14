"""Тесты jira_ping.py."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
sys.path.insert(0, str(SCRIPTS))

PING_PY = SCRIPTS / "jira_ping.py"
INIT_PY = SCRIPTS / "jira_init.py"


class PingNoConfigTests(unittest.TestCase):
    """Тест без активной борды → ошибка."""

    def test_no_config(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["JIRA_SKILL_GLOBAL_CONFIG"] = str(Path(tmp) / "_no_global_.json")
            env["JIRA_SKILL_NO_UPWARD_SEARCH"] = "1"
            result = subprocess.run(
                [sys.executable, str(PING_PY)],
                cwd=tmp,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
            )
            self.assertNotEqual(result.returncode, 0)


class PingMockTests(unittest.TestCase):
    """Тест ping с mock JiraClient — изолированно от сети."""

    def test_success_logic(self):
        """Импортируем модуль и проверяем что myself вызывается."""
        sys.path.insert(0, str(SCRIPTS))
        import importlib
        import lib.client as client_mod

        with patch.object(client_mod, "load_creds") as mock_load:
            mock_load.return_value = MagicMock(
                base_url="https://x", project_key="P", board_id=1,
                email="e@e", token="T",
            )
            with patch("lib.client.requests.Session") as mock_session_cls:
                fake_resp = MagicMock()
                fake_resp.status_code = 200
                fake_resp.content = b"x"
                fake_resp.json.return_value = {
                    "displayName": "Test User",
                    "emailAddress": "e@e",
                }
                fake_resp.url = "https://x/rest/api/3/myself"
                mock_session = MagicMock()
                mock_session.get.return_value = fake_resp
                mock_session_cls.return_value = mock_session

                # importlib.reload — не нужен, оба patch активны
                from lib.client import JiraClient

                c = JiraClient(board_name="x")
                me = c.myself()
                self.assertEqual(me["displayName"], "Test User")


if __name__ == "__main__":
    unittest.main()
