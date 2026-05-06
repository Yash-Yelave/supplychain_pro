from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass

import httpx

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str
    base_url: str
    model: str
    timeout_s: float = 20.0
    max_retries: int = 2


class DeepSeekChatClient:
    def __init__(self, config: DeepSeekConfig | None = None) -> None:
        if config is None:
            if load_dotenv is not None:
                load_dotenv(override=False)
            api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("Missing DEEPSEEK_API_KEY env var")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip().rstrip("/")
            model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
            timeout_s = float(os.getenv("DEEPSEEK_TIMEOUT_S", "20"))
            max_retries = int(os.getenv("DEEPSEEK_MAX_RETRIES", "2"))
            config = DeepSeekConfig(
                api_key=api_key,
                base_url=base_url,
                model=model,
                timeout_s=timeout_s,
                max_retries=max_retries,
            )
        self._config = config
        self._client = httpx.Client(
            base_url=self._config.base_url,
            timeout=httpx.Timeout(self._config.timeout_s),
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
        )

    def close(self) -> None:
        self._client.close()

    def chat_json(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
    ) -> dict:
        payload = {
            "model": self._config.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        last_exc: Exception | None = None
        for attempt in range(self._config.max_retries + 1):
            try:
                resp = self._client.post("/chat/completions", json=payload)
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise httpx.HTTPStatusError("retryable", request=resp.request, response=resp)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return _load_json_strict(content)
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError, KeyError, ValueError) as exc:
                last_exc = exc
                if attempt >= self._config.max_retries:
                    break
                backoff = (0.4 * (2**attempt)) + random.random() * 0.2
                time.sleep(backoff)

        raise RuntimeError(f"DeepSeek request failed after retries: {last_exc}")


def _load_json_strict(s: str) -> dict:
    s = s.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            s = "\n".join(lines[1:-1]).strip()
        else:
            s = s.strip("`").strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        obj = _extract_first_json_object(s)
        return json.loads(obj)


def _extract_first_json_object(s: str) -> str:
    start = s.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")

    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == "\"":
                in_str = False
            continue
        else:
            if ch == "\"":
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start : i + 1].strip()

    raise ValueError("Unterminated JSON object in response")
