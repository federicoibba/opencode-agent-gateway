"""Build and upsert models, skills, prompts and folders into open-webui."""

from __future__ import annotations

from .constants import SHARED_TAG, TAG_PREFIX
from .webui import http, report


def build_model(agent):
    # open-webui reads the model's system prompt from `params.system`
    # (see open_webui/routers/models.py), not from `meta`.
    params = dict(agent["params"] or {})
    params["system"] = agent["instructions"]
    meta = {
        "description": agent["description"],
        "tags": agent["tags"] + [f"{TAG_PREFIX}{agent['id']}"],
    }
    if agent["skills"]:
        meta["skillIds"] = [skill["id"] for skill in agent["skills"]]
    if agent["tools"]:
        meta["toolIds"] = agent["tools"]
    return {
        "id": agent["id"],
        "name": agent["name"],
        "base_model_id": agent["base_model"],
        "meta": meta,
        "params": params,
        "is_active": True,
    }


def sync_skills(base, token, skills, existing, prune, summary):
    for skill in skills:
        payload = {
            "id": skill["id"],
            "name": skill["name"],
            "description": skill["description"],
            "content": skill["content"],
            "meta": {"tags": [SHARED_TAG]},
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
        managed = {skill["id"] for skill in skills}
        for skill_id, skill in existing.items():
            tags = (skill.get("meta") or {}).get("tags") or []
            if any(str(t).startswith(TAG_PREFIX) for t in tags) and skill_id not in managed:
                status, body = http(
                    "POST", base, f"/api/v1/skills/id/{skill_id}/delete", token, {}
                )
                report(summary, status, f"skill {skill_id} (pruned)", body)


def sync_prompts(base, token, prompts, existing, prune, summary):
    for prompt in prompts:
        payload = {
            "command": prompt["command"],
            "name": prompt["name"],
            "content": prompt["content"],
            "data": {},
            "meta": {"description": prompt["description"]},
            "tags": prompt["tags"] + [SHARED_TAG],
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
        managed = {prompt["command"] for prompt in prompts}
        for command, prompt in existing.items():
            tags = prompt.get("tags") or []
            if any(str(t).startswith(TAG_PREFIX) for t in tags) and command not in managed:
                status, body = http(
                    "POST", base, f"/api/v1/prompts/id/{prompt['id']}/delete", token, {}
                )
                report(summary, status, f"prompt /{command} (pruned)", body)


def sync_folders(base, token, agents, existing, summary):
    """Create one sidebar folder per published workspace, bound to its model.

    Folders are per-user: the sync runs as the admin, so these land in the
    admin's sidebar. ``--prune`` never touches folders (deleting a user's folder
    is destructive and there is no reliable ownership marker).
    """
    for agent in agents:
        if not agent["publish"] or not agent["folder"]:
            continue
        payload = {"name": agent["folder"], "data": {"model_ids": [agent["id"]]}}
        current = existing.get(agent["folder"])
        if current:
            status, body = http(
                "POST", base, f"/api/v1/folders/{current['id']}/update", token, payload
            )
            action = "updated"
        else:
            status, body = http("POST", base, "/api/v1/folders/", token, payload)
            action = "created"
        report(summary, status, f"folder {agent['folder']} ({action})", body)


def sync_models(base, token, agents, existing, prune, summary):
    models = []
    for agent in agents:
        if not agent["publish"]:
            continue
        if not agent["base_model"]:
            summary["warnings"].append(
                f"model {agent['id']}: no `base_model` in the agent YAML, skipped"
            )
            continue
        model = build_model(agent)
        # open-webui merges `meta` on update, so a key this sync stops sending
        # lingers. Clear the legacy (wrong-location) `meta.system` from models
        # written by older versions; the prompt now lives in `params.system`.
        if "system" in ((existing.get(model["id"]) or {}).get("meta") or {}):
            model["meta"]["system"] = None
        models.append(model)
    if models:
        status, body = http("POST", base, "/api/v1/models/import", token, {"models": models})
        for model in models:
            report(summary, status, f"model {model['id']} (upserted)", body)

    if prune:
        managed = {model["id"] for model in models}
        for model_id, model in existing.items():
            tags = (model.get("meta") or {}).get("tags") or []
            if any(str(t).startswith(TAG_PREFIX) for t in tags) and model_id not in managed:
                status, body = http(
                    "POST", base, "/api/v1/models/model/delete", token, {"id": model_id}
                )
                report(summary, status, f"model {model_id} (pruned)", body)
