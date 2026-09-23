"""Small text/YAML helpers shared across the sync."""

from __future__ import annotations

import re

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", str(value).strip().lower())
    return value.strip("-") or "item"


def as_list(value):
    """Coerce a scalar or ``None`` into a list."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def deep_merge(base, overlay):
    out = dict(base or {})
    for key, value in (overlay or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def union_scalars(*lists):
    """Concatenate lists, keeping the first occurrence of each item."""
    seen = set()
    out = []
    for items in lists:
        for item in items:
            if item not in seen:
                seen.add(item)
                out.append(item)
    return out


def parse_frontmatter(text):
    """Split a ``---`` YAML frontmatter block from a Markdown body."""
    match = _FRONTMATTER_RE.match(text.lstrip("\ufeff"))
    if not match:
        return {}, text
    data = yaml.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        data = {}
    return data, match.group(2)
