"""Command-line entry point: parse args, print the plan, run the sync."""

from __future__ import annotations

import argparse
import os
import sys

from .agents import collect_skills, load_workspaces
from .constants import AGENTS_DIR, SHARED_PROMPTS
from .libraries import load_prompts_dir
from .sync import sync_folders, sync_models, sync_prompts, sync_skills
from .webui import authenticate, http, index_by, sync_gateway_connection


def print_plan(agents, prompts):
    published = [agent for agent in agents if agent["publish"]]
    print(f"plan for {len(published)} agent(s), {len(prompts)} prompt(s):\n")
    for agent in agents:
        marker = "" if agent["publish"] else "  (extend-only)"
        print(f"[{agent['id']}] {agent['name']}{marker}")
        if agent["description"]:
            print(f"  description : {agent['description']}")
        if agent["extends"]:
            print(f"  extends     : {', '.join(agent['extends'])}")
        print(f"  base_model  : {agent['base_model'] or '(missing!)'}")
        print(f"  tools       : {', '.join(agent['tools']) or '(none)'}")
        print(f"  folder      : {agent['folder'] or '(disabled)'}")
        print(f"  instructions: {len(agent['instructions'])} chars")
        for skill in agent["skills"]:
            print(f"  skill       : {skill['id']} — {skill['description']}")
        print()
    if prompts:
        print("prompts:")
        for prompt in prompts:
            print(f"  /{prompt['command']} — {prompt['name']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Sync agents into Open WebUI.")
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

    agents = load_workspaces(args.workspaces)
    prompts = load_prompts_dir(os.path.join(args.workspaces, SHARED_PROMPTS))
    skills = collect_skills(agents)

    if not agents:
        print(f"no agents found under {args.workspaces}/{AGENTS_DIR}/ (need a YAML file)")
        return 0

    if args.dry_run:
        print_plan(agents, prompts)
        print("connection  : gateway -> x-opencode-session: {{CHAT_ID}}")
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

    print(f"syncing {len(agents)} agent(s) into {args.url}")

    _, existing_skills = http("GET", args.url, "/api/v1/skills/", token)
    _, existing_prompts = http("GET", args.url, "/api/v1/prompts/", token)
    _, existing_folders = http("GET", args.url, "/api/v1/folders/", token)
    status, existing_models = http("GET", args.url, "/api/v1/models/export", token)
    if status != 200:
        existing_models = []
        if args.prune:
            print("  note  model export unavailable; model prune skipped", file=sys.stderr)

    summary = {"ok": [], "failed": [], "warnings": []}
    sync_gateway_connection(args.url, token, summary)
    sync_skills(args.url, token, skills, index_by(existing_skills, "id"), args.prune, summary)
    sync_prompts(
        args.url, token, prompts, index_by(existing_prompts, "command"), args.prune, summary
    )
    sync_folders(args.url, token, agents, index_by(existing_folders, "name"), summary)
    sync_models(
        args.url, token, agents, index_by(existing_models, "id"), args.prune, summary
    )

    for warning in summary["warnings"]:
        print(f"  warn  {warning}", file=sys.stderr)
    print(
        f"\ndone: {len(summary['ok'])} applied, "
        f"{len(summary['failed'])} failed, {len(summary['warnings'])} warnings"
    )
    return 1 if summary["failed"] else 0
