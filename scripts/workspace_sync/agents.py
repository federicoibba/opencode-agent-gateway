"""Discover agents, resolve ``extends`` and validate the result."""

from __future__ import annotations

import os
import sys

import yaml

from .constants import AGENTS_DIR, SHARED_MCPS, SHARED_SKILLS, YAML_EXTS
from .libraries import load_mcps_dir, load_skills_dir
from .text import as_list, deep_merge, read, slugify, union_scalars


def discover_agent_files(workspaces_dir):
    """Return agent YAML paths: ``agents/<id>.yml`` or ``agents/<id>/<id>.yml``."""
    agents_dir = os.path.join(workspaces_dir, AGENTS_DIR)
    if not os.path.isdir(agents_dir):
        raise SystemExit(f"agents directory not found: {agents_dir}")
    files = []
    for entry in sorted(os.listdir(agents_dir)):
        if entry.startswith("."):
            continue
        path = os.path.join(agents_dir, entry)
        if os.path.isdir(path):
            found = next(
                (
                    os.path.join(path, entry + ext)
                    for ext in YAML_EXTS
                    if os.path.isfile(os.path.join(path, entry + ext))
                ),
                None,
            )
            if found:
                files.append(found)
            else:
                print(
                    f"  warn  {AGENTS_DIR}/{entry}/ has no {entry}.yml; skipped",
                    file=sys.stderr,
                )
        elif entry.endswith(YAML_EXTS):
            files.append(path)
    return files


def agent_identity(path, workspaces_dir):
    """Return (agent_dir_or_None, default_id) for an agent YAML path."""
    agents_dir = os.path.realpath(os.path.join(workspaces_dir, AGENTS_DIR))
    parent = os.path.dirname(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    if os.path.realpath(parent) != agents_dir:
        return parent, os.path.basename(parent)
    return None, stem


def load_agent_sources(workspaces_dir):
    """Load every agent YAML, keyed by resolved id. Detects duplicate ids."""
    sources = {}
    for path in discover_agent_files(workspaces_dir):
        data = yaml.safe_load(read(path)) or {}
        if not isinstance(data, dict):
            raise SystemExit(f"{path}: top level must be a YAML mapping")
        agent_dir, default_id = agent_identity(path, workspaces_dir)
        agent_id = slugify(data.get("id") or default_id)
        if agent_id in sources:
            raise SystemExit(
                f"duplicate agent id '{agent_id}': "
                f"{path} and {sources[agent_id]['path']}"
            )
        sources[agent_id] = {
            "id": agent_id,
            "path": path,
            "dir": agent_dir,
            "data": data,
        }
    return sources


def build_layer(source, shared_skills, shared_mcps):
    """Turn one agent YAML into a raw layer (before ``extends`` is applied)."""
    data = source["data"]
    agent_id = source["id"]

    # Skills: shared refs first, then local — a local id shadows a shared one.
    skills = {}
    for ref in as_list(data.get("skills")):
        ref_id = slugify(ref)
        if ref_id not in shared_skills:
            raise SystemExit(
                f"{source['path']}: unknown skill '{ref}' "
                f"(no {SHARED_SKILLS}/{ref_id}/SKILL.md)"
            )
        skills[ref_id] = shared_skills[ref_id]
    if source["dir"]:
        skills.update(load_skills_dir(os.path.join(source["dir"], SHARED_SKILLS)))

    # MCPs: same shadowing rule.
    mcps = {}
    for ref in as_list(data.get("mcps")):
        ref_name = slugify(ref)
        if ref_name not in shared_mcps:
            raise SystemExit(
                f"{source['path']}: unknown mcp '{ref}' "
                f"(no {SHARED_MCPS}/{ref_name}.json)"
            )
        mcps[ref_name] = shared_mcps[ref_name]
    if source["dir"]:
        mcps.update(load_mcps_dir(os.path.join(source["dir"], SHARED_MCPS)))

    # `name`, `folder` and `publish` are per-agent and never inherited; only
    # these scalars flow through `extends`.
    scalar_keys = ("description", "base_model", "params")
    return {
        "id": agent_id,
        "path": source["path"],
        "extends": [slugify(e) for e in as_list(data.get("extends"))],
        "skills": list(skills.values()),
        "mcps": list(mcps.values()),
        "tags": [str(t) for t in as_list(data.get("tags"))],
        "prompt": data.get("prompt"),
        "prompt_append": data.get("prompt_append"),
        "name": data.get("name"),
        "folder": data.get("folder", True),
        "publish": data.get("publish", True) is not False,
        "scalars": {key: data[key] for key in scalar_keys if key in data},
    }


def merge_layers(parents, own):
    """Fold parent layers into ``own`` (parents first, child wins)."""
    skills, mcps, tags, scalars = {}, {}, [], {}
    prompt, appends = None, []
    for parent in parents:
        for skill in parent["skills"]:
            skills[skill["id"]] = skill
        for mcp in parent["mcps"]:
            mcps[mcp["name"]] = mcp
        tags = union_scalars(tags, parent["tags"])
        if parent["prompt"] is not None:
            prompt = parent["prompt"]
        appends.extend(parent["appends"])
        scalars = deep_merge(scalars, parent["scalars"])

    for skill in own["skills"]:
        skills[skill["id"]] = skill
    for mcp in own["mcps"]:
        mcps[mcp["name"]] = mcp
    tags = union_scalars(tags, own["tags"])
    if own["prompt"] is not None:
        prompt = own["prompt"]
    if own["prompt_append"] is not None:
        appends.append(str(own["prompt_append"]))
    scalars = deep_merge(scalars, own["scalars"])

    return {
        "id": own["id"],
        "path": own["path"],
        "extends": own["extends"],
        "skills": list(skills.values()),
        "mcps": list(mcps.values()),
        "tags": tags,
        "prompt": prompt,
        "appends": appends,
        "name": own["name"],
        "folder": own["folder"],
        "publish": own["publish"],
        "scalars": scalars,
    }


def resolve_agents(sources, shared_skills, shared_mcps):
    layers = {
        agent_id: build_layer(source, shared_skills, shared_mcps)
        for agent_id, source in sources.items()
    }
    resolved = {}

    def resolve(agent_id, stack):
        if agent_id in resolved:
            return resolved[agent_id]
        if agent_id in stack:
            raise SystemExit("extends cycle: " + " -> ".join(stack + [agent_id]))
        layer = layers[agent_id]
        for parent_id in layer["extends"]:
            if parent_id not in layers:
                raise SystemExit(
                    f"{layer['path']}: extends unknown agent '{parent_id}'"
                )
        parents = [
            resolve(parent_id, stack + [agent_id]) for parent_id in layer["extends"]
        ]
        resolved[agent_id] = merge_layers(parents, layer)
        return resolved[agent_id]

    return {agent_id: resolve(agent_id, []) for agent_id in layers}


def finalize(agent):
    """Turn a resolved layer into the flat structure the sync uses."""
    scalars = agent["scalars"]
    prompt = agent["prompt"] or ""
    instructions = "\n\n".join([prompt] + agent["appends"]).strip()

    name = agent["name"] or agent["id"]
    raw_folder = agent["folder"]
    if raw_folder is False:
        folder_name = None
    elif raw_folder in (True, None, "", []):
        folder_name = name
    else:
        folder_name = str(raw_folder)

    return {
        "id": agent["id"],
        "name": name,
        "description": scalars.get("description") or "",
        "base_model": scalars.get("base_model"),
        "tags": agent["tags"],
        "folder": folder_name,
        "params": scalars.get("params") or {},
        "publish": agent["publish"],
        "instructions": instructions,
        "skills": agent["skills"],
        "mcps": agent["mcps"],
        "tools": union_scalars([mcp["tool_id"] for mcp in agent["mcps"]]),
        "extends": agent["extends"],
    }


def check_conflicts(agents):
    """A skill id or mcp name must mean the same thing everywhere it appears."""
    skills, mcps = {}, {}
    for agent in agents:
        if not agent["publish"]:
            continue
        for skill in agent["skills"]:
            previous = skills.get(skill["id"])
            if previous and previous[0] != skill["content"]:
                raise SystemExit(
                    f"conflicting skill '{skill['id']}': same id, different content "
                    f"(agent '{previous[1]}' vs '{agent['id']}'). "
                    f"Move it to {SHARED_SKILLS}/{skill['id']}/SKILL.md to share it."
                )
            skills.setdefault(skill["id"], (skill["content"], agent["id"]))
        for mcp in agent["mcps"]:
            previous = mcps.get(mcp["name"])
            if previous and previous[0] != mcp["tool_id"]:
                raise SystemExit(
                    f"conflicting mcp '{mcp['name']}': different tool_id "
                    f"(agent '{previous[1]}' vs '{agent['id']}'). "
                    f"Move it to {SHARED_MCPS}/{mcp['name']}.json to share it."
                )
            mcps.setdefault(mcp["name"], (mcp["tool_id"], agent["id"]))


def collect_skills(agents):
    """Distinct skills bound to at least one published agent."""
    out = {}
    for agent in agents:
        if not agent["publish"]:
            continue
        for skill in agent["skills"]:
            out.setdefault(skill["id"], skill)
    return list(out.values())


def load_workspaces(workspaces_dir):
    if not os.path.isdir(workspaces_dir):
        raise SystemExit(f"workspaces directory not found: {workspaces_dir}")
    shared_skills = load_skills_dir(os.path.join(workspaces_dir, SHARED_SKILLS))
    shared_mcps = load_mcps_dir(os.path.join(workspaces_dir, SHARED_MCPS))
    sources = load_agent_sources(workspaces_dir)
    resolved = resolve_agents(sources, shared_skills, shared_mcps)
    agents = [finalize(resolved[agent_id]) for agent_id in resolved]
    check_conflicts(agents)
    return agents
