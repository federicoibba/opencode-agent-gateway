#!/usr/bin/env python3
"""Sync domain workspaces from this repo into Open WebUI.

This repo is the source of truth for the *agent* side of the gateway. Each domain
lives in ``workspaces/<domain>/`` as plain Markdown, and this script reconciles
Open WebUI's Workspace (Models, Skills, Prompts) to match it.

Layout of a domain::

    workspaces/<domain>/
    ├── workspace.md            # frontmatter = metadata, body = system instructions
    ├── skills/<id>/SKILL.md    # Open WebUI skills (lazy-loaded, bound to the model)
    └── prompts/<command>.md    # Open WebUI prompt templates (slash commands)

What it creates per domain:

* one **Model** preset (id = domain slug) whose base model is the gateway model
  named in ``base_model``, carrying the system instructions, the bound skills and
  the MCP tool ids listed in ``tools``;
* one **Skill** per ``skills/*/SKILL.md``;
* one **Prompt** per ``prompts/*.md``.

Everything is upserted by id/command, so re-running is safe. ``--prune`` also
deletes workspace-managed items (tagged ``workspace:<domain>``) that no longer
exist in the repo.

Auth, first match wins:
  1. ``--api-key`` / ``OPENWEBUI_API_KEY``
  2. ``--email`` + ``--password`` / ``WEBUI_ADMIN_EMAIL`` + ``WEBUI_ADMIN_PASSWORD``

Standard library only: no pip install needed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

TAG_PREFIX = "workspace:"
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)
_KEY_RE = re.compile(r"^([A-Za-z0-9_.-]+):\s*(.*)$")


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Markdown frontmatter
# --------------------------------------------------------------------------- #
def _scalar(value):
    value = value.strip()
    if value[:1] in "{[":
        try:
            return json.loads(value)
        except ValueError:
            return value
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def parse_simple_yaml(text):
    """Parse a flat map with scalar values and `- item` lists.

    Complex values may be inline JSON (`{"a": 1}` / `["a", "b"]`).
    """
    data = {}
    key = None
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        item = re.match(r"^-\s+(.*)$", stripped)
        if item and key is not None and isinstance(data.get(key), list):
            data[key].append(_scalar(item.group(1)))
            continue
        match = _KEY_RE.match(line)
        if not match:
            continue
        key = match.group(1)
        value = match.group(2).strip()
        data[key] = [] if value == "" else _scalar(value)
    return data


def parse_frontmatter(text):
    match = _FRONTMATTER_RE.match(text.lstrip("\ufeff"))
    if not match:
        return {}, text
    return parse_simple_yaml(match.group(1)), match.group(2)


def slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return value.strip("-") or "item"


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #
def load_skills(domain_dir, slug):
    skills = []
    skills_dir = os.path.join(domain_dir, "skills")
    if not os.path.isdir(skills_dir):
        return skills
    for entry in sorted(os.listdir(skills_dir)):
        path = os.path.join(skills_dir, entry, "SKILL.md")
        if not os.path.isfile(path):
            continue
        meta, body = parse_frontmatter(read(path))
        skills.append(
            {
                "id": slugify(meta.get("id") or entry),
                "name": meta.get("name") or entry,
                "description": meta.get("description") or "",
                "content": body.strip(),
                "tag": f"{TAG_PREFIX}{slug}",
            }
        )
    return skills


def load_prompts(domain_dir, slug):
    prompts = []
    prompts_dir = os.path.join(domain_dir, "prompts")
    if not os.path.isdir(prompts_dir):
        return prompts
    for filename in sorted(os.listdir(prompts_dir)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(prompts_dir, filename)
        meta, body = parse_frontmatter(read(path))
        # open-webui stores the command bare (no leading slash) and only allows
        # alphanumerics and hyphens; the UI adds the "/" at invoke time.
        command = slugify(str(meta.get("command") or os.path.splitext(filename)[0]))
        name = meta.get("name") or os.path.splitext(filename)[0].replace("-", " ").title()
        prompts.append(
            {
                "command": command,
                "name": name,
                "description": meta.get("description") or "",
                "content": body.strip(),
                "tags": list(meta.get("tags") or []),
                "tag": f"{TAG_PREFIX}{slug}",
            }
        )
    return prompts


def load_domain(domain_dir):
    slug = slugify(os.path.basename(domain_dir))
    meta, body = parse_frontmatter(read(os.path.join(domain_dir, "workspace.md")))
    slug = slugify(meta.get("id") or slug)
    tags = [str(t) for t in (meta.get("tags") or [])]
    return {
        "slug": slug,
        "name": meta.get("name") or slug,
        "description": meta.get("description") or "",
        "base_model": meta.get("base_model"),
        "tools": [str(t) for t in (meta.get("tools") or [])],
        "params": meta.get("params") or {},
        "tags": tags,
        "instructions": body.strip(),
        "skills": load_skills(domain_dir, slug),
        "prompts": load_prompts(domain_dir, slug),
    }


def discover(workspaces_dir):
    if not os.path.isdir(workspaces_dir):
        raise SystemExit(f"workspaces directory not found: {workspaces_dir}")
    domains = []
    for entry in sorted(os.listdir(workspaces_dir)):
        path = os.path.join(workspaces_dir, entry)
        if os.path.isfile(os.path.join(path, "workspace.md")):
            domains.append(load_domain(path))
    return domains


def build_model(domain):
    meta = {
        "description": domain["description"],
        "system": domain["instructions"],
        "tags": domain["tags"] + [f"{TAG_PREFIX}{domain['slug']}"],
    }
    if domain["skills"]:
        meta["skillIds"] = [skill["id"] for skill in domain["skills"]]
    if domain["tools"]:
        meta["toolIds"] = domain["tools"]
    return {
        "id": domain["slug"],
        "name": domain["name"],
        "base_model_id": domain["base_model"],
        "meta": meta,
        "params": domain["params"],
        "is_active": True,
    }


# --------------------------------------------------------------------------- #
# Sync
# --------------------------------------------------------------------------- #
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


def sync_skills(base, token, domains, existing, prune, summary):
    for domain in domains:
        for skill in domain["skills"]:
            payload = {
                "id": skill["id"],
                "name": skill["name"],
                "description": skill["description"],
                "content": skill["content"],
                "meta": {"tags": [skill["tag"]]},
                "is_active": True,
            }
            if skill["id"] in existing:
                status, body = http(
                    "POST", base, f"/api/v1/skills/id/{skill['id']}/update", token, payload
                )
                action = "updated"
            else:
                status, body = http("POST", base, "/api/v1/skills/create", token, payload)
                action = "created"
            report(summary, status, f"skill {skill['id']} ({action})", body)

    if prune:
        managed = {s["id"] for d in domains for s in d["skills"]}
        for skill_id, skill in existing.items():
            tags = (skill.get("meta") or {}).get("tags") or []
            if any(str(t).startswith(TAG_PREFIX) for t in tags) and skill_id not in managed:
                status, body = http(
                    "POST", base, f"/api/v1/skills/id/{skill_id}/delete", token, {}
                )
                report(summary, status, f"skill {skill_id} (pruned)", body)


def sync_prompts(base, token, domains, existing, prune, summary):
    for domain in domains:
        for prompt in domain["prompts"]:
            payload = {
                "command": prompt["command"],
                "name": prompt["name"],
                "content": prompt["content"],
                "data": {},
                "meta": {"description": prompt["description"]},
                "tags": prompt["tags"] + [prompt["tag"]],
                "is_production": True,
            }
            current = existing.get(prompt["command"])
            if current:
                status, body = http(
                    "POST", base, f"/api/v1/prompts/id/{current['id']}/update", token, payload
                )
                action = "updated"
            else:
                status, body = http("POST", base, "/api/v1/prompts/create", token, payload)
                action = "created"
            report(summary, status, f"prompt /{prompt['command']} ({action})", body)

    if prune:
        managed = {p["command"] for d in domains for p in d["prompts"]}
        for command, prompt in existing.items():
            tags = prompt.get("tags") or []
            if any(str(t).startswith(TAG_PREFIX) for t in tags) and command not in managed:
                status, body = http(
                    "POST", base, f"/api/v1/prompts/id/{prompt['id']}/delete", token, {}
                )
                report(summary, status, f"prompt /{command} (pruned)", body)


def sync_models(base, token, domains, existing, prune, summary):
    models = []
    for domain in domains:
        if not domain["base_model"]:
            summary["warnings"].append(
                f"model {domain['slug']}: no `base_model` in workspace.md, skipped"
            )
            continue
        models.append(build_model(domain))
    if models:
        status, body = http("POST", base, "/api/v1/models/import", token, {"models": models})
        for model in models:
            report(summary, status, f"model {model['id']} (upserted)", body)

    if prune:
        managed = {m["id"] for m in models}
        for model_id, model in existing.items():
            tags = (model.get("meta") or {}).get("tags") or []
            if any(str(t).startswith(TAG_PREFIX) for t in tags) and model_id not in managed:
                status, body = http(
                    "POST", base, "/api/v1/models/model/delete", token, {"id": model_id}
                )
                report(summary, status, f"model {model_id} (pruned)", body)


def report(summary, status, label, body):
    if 200 <= status < 300:
        summary["ok"].append(label)
        print(f"  ok    {label}")
    else:
        summary["failed"].append(f"{label}: {status} {body}")
        print(f"  FAIL  {label}: {status} {body}", file=sys.stderr)


def print_plan(domains):
    for domain in domains:
        print(f"[{domain['slug']}] {domain['name']}")
        if domain["description"]:
            print(f"  description : {domain['description']}")
        print(f"  base_model  : {domain['base_model'] or '(missing!)'}")
        print(f"  tools       : {', '.join(domain['tools']) or '(none)'}")
        print(f"  params      : {json.dumps(domain['params'])}")
        print(f"  instructions: {len(domain['instructions'])} chars")
        for skill in domain["skills"]:
            print(f"  skill       : {skill['id']} — {skill['description']}")
        for prompt in domain["prompts"]:
            print(f"  prompt      : /{prompt['command']} — {prompt['name']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Sync workspaces into Open WebUI.")
    parser.add_argument("--workspaces", default="workspaces", help="workspaces directory")
    parser.add_argument(
        "--url",
        default=os.environ.get("OPENWEBUI_URL", "http://localhost:3080"),
        help="Open WebUI base URL",
    )
    parser.add_argument("--api-key", help="Open WebUI API key (admin)")
    parser.add_argument("--email", help="admin email (sign-in fallback)")
    parser.add_argument("--password", help="admin password (sign-in fallback)")
    parser.add_argument("--prune", action="store_true", help="delete managed items not in repo")
    parser.add_argument("--dry-run", action="store_true", help="parse and print, no HTTP")
    args = parser.parse_args()

    domains = discover(args.workspaces)
    if not domains:
        print(f"no workspaces found under {args.workspaces}/ (need a workspace.md)")
        return 0

    if args.dry_run:
        print(f"plan for {len(domains)} workspace(s):\n")
        print_plan(domains)
        return 0

    token = authenticate(args.url, args)
    if not token:
        print(
            "workspace-sync: no credentials configured, skipping.\n"
            "  First run — set these in .env before `docker compose up` so the admin\n"
            "  is created headlessly and the sync can sign in with it:\n"
            "      WEBUI_ADMIN_EMAIL=admin@example.com\n"
            "      WEBUI_ADMIN_PASSWORD=<strong-password>\n"
            "  Existing install — create an API key in open-webui under\n"
            "  Settings > Account > API Keys and set it in .env:\n"
            "      OPENWEBUI_API_KEY=sk-...\n"
            "  Then apply: mise run sync-workspaces",
            file=sys.stderr,
        )
        return 0

    print(f"syncing {len(domains)} workspace(s) into {args.url}")

    _, skills = http("GET", args.url, "/api/v1/skills/", token)
    _, prompts = http("GET", args.url, "/api/v1/prompts/", token)
    status, models = http("GET", args.url, "/api/v1/models/export", token)
    if status != 200:
        models = []
        if args.prune:
            print("  note  model export unavailable; model prune skipped", file=sys.stderr)

    existing_skills = index_by(skills, "id")
    existing_prompts = index_by(prompts, "command")
    existing_models = index_by(models, "id")

    summary = {"ok": [], "failed": [], "warnings": []}
    sync_skills(args.url, token, domains, existing_skills, args.prune, summary)
    sync_prompts(args.url, token, domains, existing_prompts, args.prune, summary)
    sync_models(args.url, token, domains, existing_models, args.prune, summary)

    for warning in summary["warnings"]:
        print(f"  warn  {warning}", file=sys.stderr)
    print(
        f"\ndone: {len(summary['ok'])} applied, "
        f"{len(summary['failed'])} failed, {len(summary['warnings'])} warnings"
    )
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
