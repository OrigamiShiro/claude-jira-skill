"""Интеграционные тесты jira_config.py через subprocess."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
SCRIPTS = THIS.parent.parent
INIT_PY = SCRIPTS / "jira_init.py"
CONFIG_PY = SCRIPTS / "jira_config.py"


def _run(script: Path, args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    # Изолируем от существующего глобального config:
    # 1) указываем GLOBAL на nonexistent path
    # 2) отключаем upward search (иначе tmpdir под HOME подхватит глобальный)
    env = os.environ.copy()
    env["JIRA_SKILL_GLOBAL_CONFIG"] = str(cwd / "_no_global_.json")
    env["JIRA_SKILL_NO_UPWARD_SEARCH"] = "1"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def _make_board(cwd: Path, name: str) -> None:
    """Создаёт борду через jira_init.py с --no-ping."""
    result = _run(
        INIT_PY,
        [
            "--location", "local",
            "--name", name,
            "--url", "https://example.atlassian.net",
            "--project", "TEST",
            "--board-id", "1",
            "--email", "u@e.com",
            "--token", "T",
            "--no-ping",
        ],
        cwd=cwd,
    )
    assert result.returncode == 0, result.stderr


class JiraConfigTests(unittest.TestCase):
    def test_list_empty_no_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            result = _run(CONFIG_PY, ["list"], cwd=cwd)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("config.json не найден", result.stdout)

    def test_list_with_boards(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _make_board(cwd, "alpha")
            _make_board(cwd, "beta")

            result = _run(CONFIG_PY, ["list"], cwd=cwd)
            self.assertEqual(result.returncode, 0)
            self.assertIn("alpha", result.stdout)
            self.assertIn("beta", result.stdout)
            # second board остался активным (init выставляет active каждый раз)
            self.assertIn("*beta", result.stdout)

    def test_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _make_board(cwd, "alpha")
            result = _run(CONFIG_PY, ["current"], cwd=cwd)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "alpha")

    def test_show(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _make_board(cwd, "alpha")
            result = _run(CONFIG_PY, ["show", "alpha"], cwd=cwd)
            self.assertEqual(result.returncode, 0)
            self.assertIn("Profile: alpha", result.stdout)
            self.assertIn("https://example.atlassian.net", result.stdout)
            self.assertIn("TEST", result.stdout)
            # Token замаскирован — не должен фигурировать как "Token:   T\n"
            self.assertNotIn("Token:   T\n", result.stdout)
            self.assertIn("***", result.stdout)

    def test_switch(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _make_board(cwd, "alpha")
            _make_board(cwd, "beta")

            result = _run(CONFIG_PY, ["switch", "alpha"], cwd=cwd)
            self.assertEqual(result.returncode, 0)
            self.assertIn("alpha", result.stdout)

            cur = _run(CONFIG_PY, ["current"], cwd=cwd)
            self.assertEqual(cur.stdout.strip(), "alpha")

    def test_switch_to_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _make_board(cwd, "alpha")
            result = _run(CONFIG_PY, ["switch", "ghost"], cwd=cwd)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("не найден", result.stdout)

    def test_remove(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _make_board(cwd, "alpha")
            _make_board(cwd, "beta")

            result = _run(CONFIG_PY, ["remove", "alpha"], cwd=cwd)
            self.assertEqual(result.returncode, 0)

            # Файлы реально удалены
            board_file = cwd / ".claude" / "skills" / "jira" / "boards" / "alpha.json"
            creds_file = cwd / ".claude" / "skills" / "jira" / "creds" / "alpha.json"
            self.assertFalse(board_file.exists())
            self.assertFalse(creds_file.exists())

            # В list нет alpha
            lst = _run(CONFIG_PY, ["list"], cwd=cwd)
            self.assertNotIn("alpha", lst.stdout)

    def test_remove_active_clears_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _make_board(cwd, "alpha")
            # alpha теперь активный (последний init)
            result = _run(CONFIG_PY, ["remove", "alpha"], cwd=cwd)
            self.assertEqual(result.returncode, 0)

            cfg_path = cwd / ".claude" / "skills" / "jira" / "config.json"
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertEqual(cfg.get("active_board"), "")


if __name__ == "__main__":
    unittest.main()
