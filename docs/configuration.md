# Configuration

[Home](../README.md) · [Architecture](architecture.md) · [Agents](agents.md) · [Operations](operations.md) · [Troubleshooting](troubleshooting.md)

Everything the gateway does is declared in `config.yml`, which is bind-mounted
read-write into the `agentgateway` container.

## The provider

`config.yml` defines one custom provider named `go`:

```yaml
providers:
- name: go
  provider:
    custom:
      formats: [{ type: completions }]
  params:
    apiKey: "$OPENCODE_API_KEY"
    baseUrl: "https://opencode.ai/zen/go/v1"
```

OpenCode Go normalizes its whole catalog to the OpenAI **Chat Completions** API,
so a single `completions` format covers every model. `$OPENCODE_API_KEY` is read
from the container environment at startup.

## The models

- **Public models** (the 29 explicit entries) are what show up in `/v1/models` and
  in open-webui's picker: `glm-5.3-flash`, `kimi-k2.7-code`, `qwen3.8-max`,
  `deepseek-v4.1-flash`, `grok-4.7`, and so on.
- **`*` with `visibility: internal`** is a catch-all that is **not** listed and
  **cannot** be requested directly. It exists only as a backing target for virtual
  models. This is deliberate: if the wildcard were public, it would be advertised
  as a model literally named `*`, which Go rejects with
  `Upstream request failed: Model is unavailable.`
- **Virtual models**:
  - `fast` — weighted across `glm-5.3-flash` (60%) and `mimo-v2.6-flash` (40%),
    for bulk sub-agent work.
  - `smart` — failover from `kimi-k2.7-code` to `glm-5.2`, for planning/review.

**Add a model** — copy a line in the `models:` list, or add any Go model ID and
reload. **Add an alias** — add an entry under `virtualModels:` targeting existing
model names.

## `config.yml` reference

| Field | Meaning |
|---|---|
| `config.adminAddr` | Admin UI bind address. Set to `0.0.0.0:15000` so the Docker port mapping can reach it (startup-only; restart after changing). |
| `config.storage.mode` | How UI-managed config is persisted. `hybrid` (set here) keeps `config.yml` as the documented baseline and stores UI-created resources in the database, so the UI never rewrites the file. Alternatives: `file` (UI writes to the file — strips comments), `readOnly` (UI cannot write). Startup-only. |
| `config.logging.level` | Log verbosity: `error`/`warn`/`info`/`debug`/`trace`, or per-module (`info,proxy::httpproxy=trace`). Set to `debug` here. Startup-only; change it live at `http://localhost:15000/logging`. |
| `config.logging.format` | Log output format: `text` (default) or `json`. Set to `json` here. |
| `config.database.url` | Database behind the UI's **Logs / Analytics / Costs** pages; setting it also persists access logs to a `request_logs` table. SQLite or PostgreSQL. Set to SQLite at `/data/agentgateway.db`. Startup-only. |
| `llm.port` | Port the OpenAI-compatible API is served on (container `3000`). |
| `llm.providers[]` | Reusable provider definitions; referenced by `provider.reference`. |
| `llm.models[].name` | The model name clients request (and that appears in `/v1/models`). |
| `llm.models[].visibility` | `public` (default, listed + requestable) or `internal` (hidden, not directly requestable). |
| `llm.models[].provider` | `{ reference: go }` points at the provider above. |
| `llm.virtualModels[]` | Aliases that route across concrete models (`weighted`, `failover`, `conditional`). |
| `llm.policies.transformations.request.set` | Header rewrites applied before the request goes upstream (CEL expressions). See [the session header](architecture.md#the-per-chat-session-header). |

## Editing config

`config.yml` is bind-mounted **read-write**, and `config.storage.mode: hybrid`
keeps it as the documented baseline:

- **On the host** — edit `config.yml` directly. It is the source of truth for
  everything in it, comments included.
- **In the admin UI** (`http://localhost:15000/ui`) — resources you create in the
  UI are stored in the `agentgateway-data` database, not written back to this
  file, so the file (and its comments) is never rewritten. (With the `file`
  default, the UI rewrites `config.yml` and strips its comments.)

How a change is applied depends on the section:

- **`llm.*`** (models, providers, policies, virtual models) is **hot-reloaded** — no
  restart. Watch for `loaded config from File("/config.yml")` in the logs.
- **`config.*`** (`adminAddr`, `storage`, `logging`, `database`, `tracing`, …) is
  **startup-only** — it is read once at startup, so either restart
  (`docker compose restart agentgateway`) or set the field before the first start.

## Environment variables

| Variable | Required | Used by | Notes |
|---|---|---|---|
| `OPENCODE_API_KEY` | yes | agentgateway | Your OpenCode Go key. |
| `WEBUI_ADMIN_EMAIL` | no | workspace-sync | Admin email; with the password, bootstraps the first admin and signs the sync in. |
| `WEBUI_ADMIN_PASSWORD` | no | workspace-sync | Admin password. |
| `OPENWEBUI_API_KEY` | no | workspace-sync | API key alternative to the admin pair. |

Referenced env vars are resolved at config load. If one is missing, agentgateway
**fails to start** (`error looking key '...' up: environment variable not found`) —
it does not fall back to a default. See `.env.example` for the workspace-sync
credential options.
