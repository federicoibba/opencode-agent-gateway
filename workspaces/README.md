# Workspaces

Domain bundles for the chat UI. The split of responsibility is deliberate:

- **The gateway** (`config.yml`) is the shared layer — providers, models and the
  MCP servers every domain can reach. It is infrastructure.
- **A workspace** is one domain — frontend, backend, data, whatever — expressed
  as plain Markdown and reconciled into open-webui's **Workspace** by
  `tools/workspace_sync.py`.

You edit Markdown here; `workspace-sync` makes open-webui match it.

## Layout

```
workspaces/
└── frontend/
    ├── workspace.md               # metadata (frontmatter) + system instructions (body)
    ├── skills/
    │   ├── accessibility-audit/
    │   │   └── SKILL.md           # one open-webui skill
    │   └── design-tokens/
    │       └── SKILL.md
    └── prompts/
        └── review-ui.md           # one open-webui prompt (/review-ui)
```

A directory becomes a workspace when it contains a `workspace.md`. Everything
else is optional.

## What maps to what

| File | Becomes in open-webui | Notes |
| --- | --- | --- |
| `workspace.md` (body) | the **Model** system prompt | the domain's instructions |
| `workspace.md` `base_model` | the Model's base model | any gateway model: `smart`, `fast`, `glm-5.3-flash`, … |
| `workspace.md` `tools` | the Model's bound tools | MCP references, e.g. `server:mcp:agentgateway` |
| `workspace.md` `params` | the Model's parameters | inline JSON, e.g. `{"temperature": 0.3}` |
| `workspace.md` `tags` | Model tags | for organising the picker |
| `skills/<id>/SKILL.md` | a **Skill**, bound to the Model | lazy-loaded on demand via `view_skill` |
| `prompts/<name>.md` | a **Prompt** slash command | invoked as `/name`; override the slug with `command:` |

The Model is created with the domain's id (the directory name), so a domain
shows up in the model picker as its own agent — no manual setup in the UI.

## Frontmatter

`workspace.md` is a flat map of scalars, lists and inline JSON:

```yaml
---
name: Frontend
description: Frontend engineering workspace for UI, accessibility and design systems.
base_model: smart
tools: ["server:mcp:agentgateway"]
tags: ["frontend", "ui"]
params: {"temperature": 0.3}
---

# Frontend workspace

You are the frontend engineering assistant …
```

`SKILL.md` uses the open-webui skill standard — `name` (slug) and a one-sentence
`description` that the model reads when deciding whether to load it. The
directory name is the skill id. `prompts/*.md` takes `name`, `description` and an
optional `command` (a bare slug, invoked as `/command`; defaults to the
filename).

## Adding a domain

```bash
cp -r workspaces/frontend workspaces/backend
$EDITOR workspaces/backend/workspace.md
# edit/replace the skills and prompts, then:
mise run workspaces        # dry-run: show the plan
mise run sync-workspaces   # apply to open-webui
```

`workspace-sync` also runs automatically on `docker compose up`, so a fresh
`up` comes with the domains already bundled in the UI.

## Credentials

The sync needs an admin credential, from `.env` (see `.env.example`):

- `WEBUI_ADMIN_EMAIL` + `WEBUI_ADMIN_PASSWORD` — creates the first admin on a
  fresh install and signs in with it, or
- `OPENWEBUI_API_KEY` — a key from an existing account.

Without either, the sync exits 0 and leaves open-webui untouched.

## Sync behaviour

- **Upsert by id**: skills by skill id, prompts by command, models by model id.
  Re-running never duplicates and never deletes what it did not create.
- **`--prune`**: also deletes workspace-managed items (tagged
  `workspace:<domain>`) that no longer exist in the repo. Off by default.
- **`--dry-run`**: parse and print the plan, no HTTP.
- **Managed items** carry a `workspace:<domain>` tag, so prune only ever touches
  things this repo created.

## MCP references

`tools` in `workspace.md` holds open-webui tool ids. The gateway multiplexes its
MCP targets into one server, wired in `docker-compose.yml` as the
`agentgateway` connection, whose id is `server:mcp:agentgateway`. To give a
domain its own servers, add targets under `mcp.targets` in `config.yml` and
reference the resulting tool ids here.
