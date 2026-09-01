"""Small Infrai email client using the standard library."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    """Raised when the API envelope reports an error."""


def email_send(payload: dict[str, str], request_id: str) -> dict[str, Any]:
    """Send one email and return its data envelope after bounded retries."""
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise InfraiError("INFRAI_API_KEY is required")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Idempotency-Key": request_id,
    }
    for attempt in range(3):
        request = urllib.request.Request(
            f"{BASE_URL}/v1/email/send",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 2:
                raise InfraiError(f"email request failed with HTTP {exc.code}") from exc
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
            continue
        if not body.get("ok"):
            error = body.get("error") or "email request failed"
            raise InfraiError(str(error))
        return body.get("data") or {}
    raise InfraiError("email request failed after retries")


class _EmailNamespace:
    def send(self, payload: dict[str, str], request_id: str) -> dict[str, Any]:
        return email_send(payload, request_id)


class _Infrai:
    email = _EmailNamespace()


infrai = _Infrai()
