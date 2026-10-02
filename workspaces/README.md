# Workspaces

Agent bundles for the chat UI. The split of responsibility is deliberate:

- **The gateway** (`config.yml`) is the shared layer — providers, models and the
  MCP servers every agent can reach. It is infrastructure.
- **An agent** is one workspace — frontend, backend-go, data, cloud, whatever
  — declared as a YAML file and reconciled into open-webui's **Workspace** by the
  `workspace_sync` package (`scripts/workspace_sync/`).

You edit YAML and Markdown here; `workspace-sync` makes open-webui match it.

## Layout

```
workspaces/
├── agents/                          # one agent per YAML file
│   ├── base/                        # shared baseline (publish: false)
│   │   └── base.yml                 # extends target for every agent
│   ├── frontend/                    # Vue 3 + Nuxt
│   │   └── frontend.yml
│   ├── backend-go/
│   │   └── backend-go.yml
│   ├── data/                        # extends: backend-go
│   │   └── data.yml
│   ├── cloud/                       # Cloudflare + AWS
│   │   └── cloud.yml
│   ├── devops/                      # extends: cloud
│   │   └── devops.yml
│   ├── product/  architect/  planner/  designer/
│   ├── security/  qa/  docs/  agent-ops/
│   └── quick.yml                    # flat form: single-file agent
├── skills/<id>/SKILL.md             # shared skill library (referenced by id)
├── mcps/<name>.json                 # shared MCP library (referenced by name)
└── prompts/<command>.md             # global slash-command prompts
```

`reviewer`, `performance` and `refactor` are deliberately **not** agents: their
skills (`code-review`, `silent-failures`, `performance-web`,
`performance-backend`, `refactoring`) live on `base` and are invoked through the
`/review`, `/perf` and `/refactor` prompts.

An agent is either:

- **folder form** — `agents/<id>/<id>.yml` (the canonical name mirrors the
  folder), optionally with `skills/` and `mcps/` beside it; or
- **flat form** — `agents/<id>.yml`, for an agent with no local assets.

The agent id defaults to the file/folder name and can be overridden with `id:`.

## The baseline: `extends: base`

Every published agent inherits `agents/base/base.yml` with `extends: base`. The
baseline is marked `publish: false`, so it is **extend-only**: it creates no
Model in the picker and no sidebar folder, but its `mcps`, `skills` and
`prompt_append` flow to every agent that extends it. It carries the
`agentgateway` MCP, the `jev-agent` and `agent-self-eval` skills, and the
cross-cutting review skills (`code-review`, `silent-failures`,
`performance-web`, `performance-backend`, `refactoring`).

Put capabilities that **every** agent should have in the baseline, and
agent-specific skills in the agent's own `skills/` or the shared library. The
skill's "when to use" rules keep a broadly-shared skill from being applied in the
wrong place.

The baseline deliberately sets no `prompt` and no `base_model`: `prompt` is
replaced by a child that defines its own, and `base_model` is each agent's choice.
Shared prose is stated with `prompt_append` (concatenated parent → child) — this
is where the operating/security baseline lives.

## What maps to what

| Agent YAML             | Becomes in open-webui                   | Notes                                                        |
| ---------------------- | --------------------------------------- | ------------------------------------------------------------ |
| `prompt`               | the **Model** system prompt             | inline in the YAML                                           |
| `prompt_append`        | appended to the inherited prompt        | concatenated parent-to-child                                 |
| `base_model`           | the Model's base model                  | any gateway model: `smart`, `fast`, `glm-5.3-flash`, …       |
| `mcps`                 | the Model's bound tools                 | names from `workspaces/mcps/`                                |
| `skills`               | the Model's bound skills                | ids from `workspaces/skills/`                                |
| `tags`                 | Model tags                              | for organising the picker                                    |
| `folder`               | a sidebar **Folder** bound to the Model | default = agent name, `false` disables                       |
| `folder_icon`          | the Folder's sidebar icon               | an open-webui emoji name (e.g. `cloud`, `lock`, `test_tube`) |
| `params`               | the Model's parameters                  | optional; deep-merged across `extends`                       |
| `publish`              | whether a Model is created              | `false` = extend-only base                                   |
| `skills/<id>/SKILL.md` | a **Skill**                             | local ones attach implicitly; lazy-loaded via `view_skill`   |
| `prompts/<name>.md`    | a **Prompt** slash command              | global; invoked as `/name`                                   |

Each published agent also gets a **folder** in the sidebar (`folder.data.model_ids`),
so opening a chat inside "Frontend" starts it on the Frontend model.
`folder_icon` sets that folder's sidebar icon (an open-webui emoji name).

Folders are per-user, so they are created in the sync account's sidebar (the
admin). `--prune` never deletes folders: they hold a user's own chats.

## An agent

```yaml
# workspaces/agents/backend-go/backend-go.yml
name: Backend (Go)
description: Backend engineering workspace for Go services, HTTP APIs, concurrency and error handling.
extends: base
base_model: smart
tags: [backend, go, api]
folder: Backend (Go)
mcps: [agentgateway] # from workspaces/mcps/
skills: [go, api-design, error-handling, tdd]

prompt: |
  # Backend (Go) workspace

  You are the backend engineer for this team …
```

`prompt` is the agent's system prompt, inline. (This is separate from the
`prompts/*.md` slash commands, which are global to open-webui.)

## Sharing and spreading: `extends`

An agent can inherit from one or more other agents. This is how the Data agent
reuses the Backend (Go) agent without duplication:

```yaml
# workspaces/agents/data/data.yml
name: Data
description: Database workspace for PostgreSQL schema design, migrations and query performance.
extends: backend-go # or: extends: [backend-go, base]
folder: Data
tags: [database, postgres]
skills: [postgres, migrations, data-modeling]
prompt: |
  # Data workspace
  You specialise in PostgreSQL …
```

Merge rules:

| Field                                      | Rule                                              |
| ------------------------------------------ | ------------------------------------------------- |
| `extends`                                  | resolved recursively; a cycle is an error         |
| `skills`, `mcps`, `tags`                   | unioned (the "spread"), order-preserving, deduped |
| `params`                                   | deep-merged, child wins                           |
| `description`, `base_model`                | child overrides the parent                        |
| `prompt`                                   | child replaces the parent's prompt                |
| `prompt_append`                            | concatenated parent → child                       |
| `name`, `folder`, `folder_icon`, `publish` | per-agent, **never** inherited                    |

## Local vs shared

A skill (or MCP) lives in exactly one place:

- **local** — in the agent's own `skills/` or `mcps/`, attached implicitly to
  that agent; or
- **shared** — in `workspaces/skills/` or `workspaces/mcps/`, pulled in by id
  from the agent's `skills:` / `mcps:` list, for reuse across agents.

A local entry shadows a shared one with the same id. If two agents define the
same skill id with **different content**, the sync fails and tells you to move it
to `workspaces/skills/` — open-webui has one global skill per id.

`publish: false` marks an extend-only base: it is not created as a Model, but its
skills, MCPs, prompt and config still flow to the agents that extend it.

## MCP references

`mcps:` names files in `workspaces/mcps/`. Each JSON file gives the open-webui
tool id to bind:

```json
{
  "name": "agentgateway",
  "description": "Tools exposed by the agentgateway MCP endpoint",
  "tool_id": "server:mcp:agentgateway",
  "url": "http://agentgateway:4000/mcp",
  "auth_type": "none"
}
```

The gateway multiplexes its MCP targets into one server, wired in
`docker-compose.yml` as the `agentgateway` connection. To add servers, add
targets under `mcp.targets` in `config.yml` and reference the resulting tool ids
here.

## Adding an agent

```bash
mkdir -p workspaces/agents/payments
cp workspaces/agents/backend-go/backend-go.yml workspaces/agents/payments/payments.yml
$EDITOR workspaces/agents/payments/payments.yml   # name, prompt, skills, mcps
mise run workspaces        # dry-run: show the resolved plan
mise run sync-workspaces   # apply to open-webui
```

`workspace-sync` also runs automatically on `docker compose up`, so a fresh `up`
comes with the agents already bundled in the UI.

## Credentials

The sync needs an admin credential, from `.env` (see `.env.example`):

- `WEBUI_ADMIN_EMAIL` + `WEBUI_ADMIN_PASSWORD` — creates the first admin on a
  fresh install and signs in with it, or
- `OPENWEBUI_API_KEY` — a key from an existing account.

Without either, the sync exits 0 and leaves open-webui untouched.

## Sync behaviour

- **Upsert by id**: skills by skill id, prompts by command, models by model id.
  Re-running never duplicates and never deletes what it did not create.
- **`--prune`**: also deletes workspace-managed items (tagged `workspace:`)
  that no longer exist in the repo. Off by default.
- **`--dry-run`**: resolve and print the plan, no HTTP.
- **Managed items** carry a `workspace:` tag, so prune only ever touches things
  this repo created.

## Running the sync locally

The sync is packaged under `scripts/workspace_sync/` and run as
`python -m workspace_sync`. It needs PyYAML:

```bash
mise run setup-deps        # python3 -m pip install --user -r scripts/requirements.txt
mise run workspaces        # PYTHONPATH=scripts python3 -m workspace_sync --dry-run
```

Inside Docker the `workspace-sync` service builds `scripts/Dockerfile` with the
dependency baked in, so `mise run sync-workspaces` needs nothing local.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
