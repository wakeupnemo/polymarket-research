from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import time

import requests


@dataclass
class GammaClient:
    base_url: str
    timeout_seconds: int = 60
    max_retries: int = 5
    user_agent: str = "pmre/0.1 metadata-refresh"

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url.rstrip("/") + path

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = self._url(path)
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(
                    url,
                    params=params,
                    headers={
                        "Accept": "application/json",
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

        raise RuntimeError(f"Gamma request failed for {url} params={params}: {last_error}") from last_error

    def list_markets(
        self,
        *,
        active: bool = True,
        closed: bool = False,
        limit: int = 25,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        payload = self.get_json(
            "/markets",
            {
                "active": str(active).lower(),
                "closed": str(closed).lower(),
                "limit": limit,
                "offset": offset,
            },
        )
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("markets"), list):
            return payload["markets"]
        raise ValueError(f"Unexpected /markets payload shape: {type(payload).__name__}")
