from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import time

import requests


@dataclass
class ClobClient:
    base_url: str
    timeout_seconds: int = 30
    max_retries: int = 5
    user_agent: str = "pmre/0.1 raw-books"

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url.rstrip("/") + path

    def post_json(self, path: str, payload: Any) -> Any:
        url = self._url(path)
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "User-Agent": self.user_agent,
                        "Connection": "close",
                    },
                    timeout=(10, self.timeout_seconds),
                )
                resp.raise_for_status()
                return resp.json()
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt == self.max_retries:
                    break
                time.sleep(min(8.0, 1.0 * (2 ** (attempt - 1))))

        raise RuntimeError(f"CLOB request failed for {url}: {last_error}") from last_error

    def get_books(self, token_ids: list[str]) -> list[dict[str, Any]]:
        payload = [{"token_id": token_id} for token_id in token_ids]
        data = self.post_json("/books", payload)

        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("books"), list):
            return data["books"]

        raise ValueError(f"Unexpected /books payload shape: {type(data).__name__}")
