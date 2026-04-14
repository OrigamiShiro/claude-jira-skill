"""
JiraClient — тонкая обёртка над requests для Jira Cloud REST API.

Использование:
    client = JiraClient()                   # активная борда из config.json
    client = JiraClient(board_name="other") # конкретная борда

    client.get("/rest/api/3/myself")
    client.post("/rest/api/3/issue", json={...})
"""

from __future__ import annotations

import json as json_lib
import logging
from typing import Any, Optional

import requests
from requests.auth import HTTPBasicAuth

from .auth import BoardCredentials, load_creds
from .config import get_active_board

log = logging.getLogger("jira-skill.client")


DEFAULT_TIMEOUT = 30  # секунд


class JiraError(Exception):
    """Базовая ошибка Jira API."""


class JiraAuthError(JiraError):
    """401 — некорректные credentials."""


class JiraNotFoundError(JiraError):
    """404 — ресурс не найден."""


class JiraClient:
    """Тонкая обёртка над requests для Jira Cloud REST API."""

    def __init__(self, board_name: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        if board_name is None:
            board_name = get_active_board()
            if board_name is None:
                raise JiraError(
                    "Активная борда не выбрана. Запусти jira_init.py или jira_config.py switch."
                )

        self.creds: BoardCredentials = load_creds(board_name)
        self.timeout = timeout
        self._session = requests.Session()
        self._session.auth = HTTPBasicAuth(self.creds.email, self.creds.token)
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def base_url(self) -> str:
        return self.creds.base_url

    @property
    def project_key(self) -> str:
        return self.creds.project_key

    @property
    def board_id(self) -> int:
        return self.creds.board_id

    def _full_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def _handle_response(self, response: requests.Response) -> Any:
        # Auth errors
        if response.status_code == 401:
            log.error("Jira auth failed (401) for %s", response.url)
            raise JiraAuthError(
                "Unauthorized (401). Проверь email и API token."
            )
        if response.status_code == 403:
            log.error("Jira forbidden (403) for %s", response.url)
            raise JiraAuthError(
                "Forbidden (403). Нет прав на операцию."
            )
        if response.status_code == 404:
            log.error("Jira not found (404) for %s", response.url)
            raise JiraNotFoundError(
                f"Resource not found (404): {response.url}"
            )
        if response.status_code >= 400:
            text = response.text[:500]
            log.error(
                "Jira API error %d for %s: %s",
                response.status_code,
                response.url,
                text,
            )
            raise JiraError(
                f"Jira API error {response.status_code}: {text}"
            )

        # Success — try JSON, fallback to None for 204 No Content
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except json_lib.JSONDecodeError:
            return response.text

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------

    def get(
        self,
        path: str,
        params: Optional[dict] = None,
        **kwargs,
    ) -> Any:
        url = self._full_url(path)
        response = self._session.get(
            url, params=params, timeout=self.timeout, **kwargs
        )
        return self._handle_response(response)

    def post(
        self,
        path: str,
        json: Optional[dict] = None,
        **kwargs,
    ) -> Any:
        url = self._full_url(path)
        response = self._session.post(
            url, json=json, timeout=self.timeout, **kwargs
        )
        return self._handle_response(response)

    def put(
        self,
        path: str,
        json: Optional[dict] = None,
        **kwargs,
    ) -> Any:
        url = self._full_url(path)
        response = self._session.put(
            url, json=json, timeout=self.timeout, **kwargs
        )
        return self._handle_response(response)

    def delete(self, path: str, **kwargs) -> Any:
        url = self._full_url(path)
        response = self._session.delete(url, timeout=self.timeout, **kwargs)
        return self._handle_response(response)

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def myself(self) -> dict:
        """GET /rest/api/3/myself — проверка авторизации."""
        return self.get("/rest/api/3/myself")

    def browse_url(self, issue_key: str) -> str:
        return f"{self.base_url}/browse/{issue_key}"
