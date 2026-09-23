"""open-webui HTTP client and the gateway connection sync."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

from .constants import GATEWAY_CONNECTION_MATCH, GATEWAY_SESSION_HEADER


def http(method, base, path, token=None, body=None, timeout=60):
    """Return (status, parsed_body_or_text). Never raises on HTTP errors."""
    url = base.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = raw
        return exc.code, parsed
    except urllib.error.URLError as exc:
        return 0, str(exc)


def authenticate(base, args):
    key = args.api_key or os.environ.get("OPENWEBUI_API_KEY")
    if key:
        return key
    email = args.email or os.environ.get("WEBUI_ADMIN_EMAIL")
    password = args.password or os.environ.get("WEBUI_ADMIN_PASSWORD")
    if email and password:
        status, body = http(
            "POST", base, "/api/v1/auths/signin", None, {"email": email, "password": password}
        )
        if status == 200 and isinstance(body, dict) and body.get("token"):
            return body["token"]
        raise SystemExit(f"sign-in failed ({status}): {body}")
    return None


def index_by(items, key):
    return {item[key]: item for item in (items or []) if item.get(key)}


def report(summary, status, label, body):
    if 200 <= status < 300:
        summary["ok"].append(label)
        print(f"  ok    {label}")
    else:
        summary["failed"].append(f"{label}: {status} {body}")
        print(f"  FAIL  {label}: {status} {body}", file=sys.stderr)


def sync_gateway_connection(base, token, summary):
    """Give the gateway's OpenAI connection the per-chat session header.

    open-webui has no env var for per-connection custom headers that applies to
    an existing install, so read the OpenAI connection config, merge
    ``x-opencode-session: {{CHAT_ID}}`` into the matching connection's headers,
    and write it back. Idempotent, and preserves any other headers/config.
    """
    status, cfg = http("GET", base, "/openai/config", token)
    if status != 200 or not isinstance(cfg, dict):
        summary["warnings"].append(
            f"openai config unavailable ({status}); x-opencode-session not set"
        )
        return

    urls = cfg.get("OPENAI_API_BASE_URLS") or []
    configs = dict(cfg.get("OPENAI_API_CONFIGS") or {})
    idx = next(
        (i for i, url in enumerate(urls) if GATEWAY_CONNECTION_MATCH in (url or "")),
        None,
    )
    if idx is None:
        summary["warnings"].append(
            f"no OpenAI connection matching '{GATEWAY_CONNECTION_MATCH}'; "
            "x-opencode-session not set"
        )
        return

    # Configs are stored by string index, but tolerate a URL key from older data.
    key = str(idx)
    connection = dict(configs.get(key) or configs.get(urls[idx]) or {})
    headers = dict(connection.get("headers") or {})
    headers.update(GATEWAY_SESSION_HEADER)
    connection["headers"] = headers
    configs[key] = connection

    payload = {
        "ENABLE_OPENAI_API": cfg.get("ENABLE_OPENAI_API"),
        "OPENAI_API_BASE_URLS": urls,
        "OPENAI_API_KEYS": cfg.get("OPENAI_API_KEYS") or [],
        "OPENAI_API_CONFIGS": configs,
    }
    status, body = http("POST", base, "/openai/config/update", token, payload)
    report(summary, status, "gateway connection header (x-opencode-session)", body)


__all__ = [
    "http",
    "authenticate",
    "index_by",
    "report",
    "sync_gateway_connection",
]
