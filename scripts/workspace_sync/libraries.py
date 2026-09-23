"""Load skills, MCPs and prompts from the shared libraries."""

from __future__ import annotations

import json
import os

from .text import as_list, parse_frontmatter, read, slugify


def load_skill(path):
    meta, body = parse_frontmatter(read(path))
    entry = os.path.basename(os.path.dirname(path))
    return {
        "id": slugify(meta.get("id") or entry),
        "name": meta.get("name") or entry,
        "description": meta.get("description") or "",
        "content": body.strip(),
    }


def load_skills_dir(skills_dir):
    """Index ``<skills_dir>/<id>/SKILL.md`` by skill id."""
    out = {}
    if not os.path.isdir(skills_dir):
        return out
    for entry in sorted(os.listdir(skills_dir)):
        path = os.path.join(skills_dir, entry, "SKILL.md")
        if not os.path.isfile(path):
            continue
        skill = load_skill(path)
        out[skill["id"]] = skill
    return out


def load_mcp(path):
    try:
        data = json.loads(read(path))
    except ValueError as exc:
        raise SystemExit(f"{path}: invalid JSON ({exc})")
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: top level must be a JSON object")
    stem = os.path.splitext(os.path.basename(path))[0]
    name = slugify(data.get("name") or stem)
    tool_id = data.get("tool_id") or data.get("toolId")
    if not tool_id:
        raise SystemExit(f"{path}: missing `tool_id` (the open-webui tool id to bind)")
    return {
        "name": name,
        "tool_id": str(tool_id),
        "description": data.get("description") or "",
    }


def load_mcps_dir(mcps_dir):
    """Index ``<mcps_dir>/<name>.json`` by mcp name."""
    out = {}
    if not os.path.isdir(mcps_dir):
        return out
    for entry in sorted(os.listdir(mcps_dir)):
        if not entry.endswith(".json"):
            continue
        mcp = load_mcp(os.path.join(mcps_dir, entry))
        out[mcp["name"]] = mcp
    return out


def load_prompts_dir(prompts_dir):
    prompts = []
    if not os.path.isdir(prompts_dir):
        return prompts
    for filename in sorted(os.listdir(prompts_dir)):
        if not filename.endswith(".md"):
            continue
        meta, body = parse_frontmatter(read(os.path.join(prompts_dir, filename)))
        # open-webui stores the command bare (no leading slash) and only allows
        # alphanumerics and hyphens; the UI adds the "/" at invoke time.
        command = slugify(meta.get("command") or os.path.splitext(filename)[0])
        name = meta.get("name") or os.path.splitext(filename)[0].replace("-", " ").title()
        prompts.append(
            {
                "command": command,
                "name": name,
                "description": meta.get("description") or "",
                "content": body.strip(),
                "tags": [str(t) for t in as_list(meta.get("tags"))],
            }
        )
    return prompts
