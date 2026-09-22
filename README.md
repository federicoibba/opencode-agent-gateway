# agent-gateway

A self-hosted, OpenAI-compatible gateway in front of **OpenCode Go**, plus a chat
UI. Point any OpenAI client at `http://localhost:3000/v1` and it is backed by your
OpenCode Go subscription.

Two containers:

- **[agentgateway](https://agentgateway.dev/)** — the LLM gateway. Holds your Go
  API key, exposes an OpenAI-compatible API, lists the Go models, and derives a
  stable session ID per conversation.
- **[open-webui](https://openwebui.com/)** — a browser chat UI, pre-wired to talk
  to the gateway instead of to a provider directly.

---

## What you get

| Surface | URL | Purpose |
|---|---|---|
| LLM API | `http://localhost:3000/v1` | OpenAI-compatible endpoint (`/models`, `/chat/completions`) |
| Chat UI | `http://localhost:3080` | open-webui |
| Admin / gateway UI | `http://localhost:15000/ui` | agentgateway admin, metrics, config inspection |

- One place for the OpenCode Go key — the browser and open-webui never see it.
- The full list of Go models in the model picker, plus two aliases (`fast`, `smart`).
- A stable `x-opencode-session` per conversation, so Go can route requests and
  reuse prompt caches efficiently.

---

## Architecture

```
                 OpenAI-compatible HTTP
  open-webui  ───────────────────────────►  agentgateway  ──────────►  opencode.ai/zen/go/v1
  :3080                                     :3000 (LLM)                (OpenCode Go)
  (browser)                                 :15000 (admin)
                                                 │
                                                 ├─ injects x-opencode-session
                                                 ├─ injects User-Agent
                                                 └─ holds OPENCODE_API_KEY
```

Any other OpenAI client (a script, an SDK, your own agent) can use
`http://localhost:3000/v1` the same way.

---

## Prerequisites

- Docker with Docker Compose v2 (`docker compose ...`)
- An **OpenCode Go** subscription and API key: <https://opencode.ai/auth>

---

## Quick start

```bash
# 1. Create your env file and add your Go API key
cp .env.example .env
$EDITOR .env

# 2. Start everything
docker compose up -d

# 3. Confirm the gateway sees your models
curl -s http://localhost:3000/v1/models | jq -r '.data[].id'
```

Then open the chat UI at <http://localhost:3080> (create the first admin account on
first run) and finish the one-time open-webui step below.

### Smoke test from the command line

```bash
curl -s http://localhost:3000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"glm-5.3-flash","max_tokens":32,
       "messages":[{"role":"user","content":"Say hi in three words."}]}' | jq .
```

Or use an alias:

```bash
curl -s http://localhost:3000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"fast","messages":[{"role":"user","content":"hello"}]}' | jq .
```

---

## One-time open-webui setup

The connection is created by environment variables, but the **per-chat session
header** must be added in the UI (open-webui has no env var for custom headers yet).
It persists in the `open-webui` Docker volume.

1. **Settings → Admin → Connections →** your OpenAI connection.

   <img src="docs/connection-settings.png" alt="Settings → Connections" width="600">

2. Set **Custom headers** to:

   ```json
   { "x-opencode-session": "{{CHAT_ID}}" }
   ```

   `{{CHAT_ID}}` is interpolated by open-webui per chat.

   <img src="docs/connection-headers.png" alt="Set header" width="420">

3. Save, then click the **refresh** icon on the connection so the model list is
   re-fetched.

Without this header the gateway still gives each chat its own session by hashing
the first user message, so it works either way — the header just makes it exact.

---

## How it works

### The provider

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

### The models

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

### The session header (why the transformation exists)

OpenCode Go requires a stable `x-opencode-session` per conversation and returns
`Request is missing x-opencode-session` without one. agentgateway translates the
request into the provider's wire format, which rebuilds the upstream request and
drops client headers — so the gateway re-adds it:

```yaml
policies:
  transformations:
    request:
      set:
        x-opencode-session: |
          coalesce(
            request.headers["x-opencode-session"],
            request.headers["x-openwebui-chat-id"],
            json(request.body).chat_id,
            sha256.encode(string(json(request.body).messages.filter(m, m.role == "user")[0].content)),
            uuid()
          )
        User-Agent: '"agent-gateway/1.0"'
```

Priority order, first match wins (`coalesce` swallows errors from earlier branches):

1. an explicit `x-opencode-session` from the client (your own agent, or open-webui
   once the custom header is set),
2. open-webui's built-in `x-openwebui-chat-id` header,
3. a `chat_id` carried in the request body,
4. a SHA-256 of the **first user message** — stable across turns because the
   message history only appends, so any client gets a working per-chat session
   with zero configuration,
5. `uuid()` — only if the content cannot be hashed (e.g. multimodal message parts).

---

## Configuration reference (`config.yml`)

| Field | Meaning |
|---|---|
| `config.adminAddr` | Admin UI bind address. Set to `0.0.0.0:15000` so the Docker port mapping can reach it (startup-only; restart after changing). |
| `llm.port` | Port the OpenAI-compatible API is served on (container `3000`). |
| `llm.providers[]` | Reusable provider definitions; referenced by `provider.reference`. |
| `llm.models[].name` | The model name clients request (and that appears in `/v1/models`). |
| `llm.models[].visibility` | `public` (default, listed + requestable) or `internal` (hidden, not directly requestable). |
| `llm.models[].provider` | `{ reference: go }` points at the provider above. |
| `llm.virtualModels[]` | Aliases that route across concrete models (`weighted`, `failover`, `conditional`). |
| `llm.policies.transformations.request.set` | Header rewrites applied before the request goes upstream (CEL expressions). |

**Add a model** — copy a line in the `models:` list, or add any Go model ID and
restart/reload. **Add an alias** — add an entry under `virtualModels:` targeting
existing model names.

### Environment variables

| Variable | Required | Used by | Notes |
|---|---|---|---|
| `OPENCODE_API_KEY` | yes | agentgateway | Your OpenCode Go key. |

Referenced env vars are resolved at config load. If one is missing, agentgateway
**fails to start** (`error looking key '...' up: environment variable not found`) —
it does not fall back to a default.

---

## Operations

```bash
docker compose up -d          # start / apply changes
docker compose ps             # status
docker compose logs -f agentgateway   # gateway logs (every request is logged)
docker compose logs -f open-webui     # UI logs
docker compose pull && docker compose up -d   # update images
docker compose down           # stop (keeps the open-webui volume)
```

The `Makefile` wraps the common commands: `make up`, `down`, `restart`, `logs`,
`models`, `smoke`, `pull`, and `config` (`make help` lists them all).

- **Config changes** to `config.yml` are **hot-reloaded** — no restart needed
  (watch for `loaded config from File("/config.yml")` in the logs).
- **Env var changes** require a restart: `docker compose up -d --force-recreate`.
- open-webui data (accounts, chats, connection settings) lives in the
  `open-webui` named volume.

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Request is missing x-opencode-session` | The request transformation is missing or the config did not reload. Check `config.yml` and the gateway logs for `loaded config`. |
| `Upstream request failed: Model is unavailable.` | A client sent `model: "*"`. The wildcard must stay `visibility: internal`. In open-webui, refresh the connection's model list and pick a real model or `fast`/`smart`. |
| `404 Model not found` from the gateway | The requested model is not one of the public entries. Add it to `config.yml`. |
| `error looking key 'OPENCODE_API_KEY' up` at startup | `.env` is missing or the variable is not set. Recreate with `docker compose up -d --force-recreate`. |
| open-webui shows no models | Refresh the connection (Settings → Admin → Connections). Check the base URL is `http://agentgateway:3000/v1` and the key is non-empty (a placeholder is fine — the gateway substitutes the real one). |
| open-webui still lists a stale `*` model | Hard-reload the page / click the connection's refresh icon; the list is cached client-side. |
| `http://localhost:15000` won't load | The admin UI binds to loopback inside the container by default, which a Docker port mapping cannot reach. `config.adminAddr: "0.0.0.0:15000"` is set in `config.yml`; it is startup-only, so restart the container after changing it. |
| Go returns `429` | A model hit its Go usage cap. Enable **Use balance** in the Zen console, or route around it (see `smart`). |

---

## Notes and limits

- **Published ports:** the admin UI (`15000`) is published on host loopback only
  (`127.0.0.1:15000`) because it is unauthenticated. The LLM API (`3000`) and chat
  UI (`3080`) are published on all interfaces; change them to
  `127.0.0.1:3000:3000` / `127.0.0.1:3080:8080` in `docker-compose.yml` to restrict
  them to this machine.
- **The Go key lives only in the `agentgateway` container.** open-webui uses the
  literal key `placeholder`; the gateway replaces the auth header with the real key.
- Go usage is capped **per model** on 5-hour / weekly / monthly buckets. See the
  [Go docs](https://opencode.ai/docs/go/) for current limits.
- Multimodal messages (content as a list) fall through to a random `uuid()`
  session, so they do not share a prompt cache. To keep those stable too, hash the
  first text part instead of the raw content in the `coalesce` chain.

---

## Repository layout

```
.
├── .env.example         # copy to .env and fill in
├── .gitignore
├── Makefile             # convenience targets (up, logs, models, smoke, ...)
├── config.yml           # agentgateway config (provider, models, session policy)
├── docker-compose.yml   # agentgateway + open-webui
├── docs/                # screenshots used by this README
│   ├── connection-headers.png
│   └── connection-settings.png
└── README.md
```

---

## References

- agentgateway docs — <https://agentgateway.dev/docs/standalone/latest/>
- Custom LLM provider — <https://agentgateway.dev/docs/standalone/latest/integrations/llm/providers/custom/>
- LLM request transformations — <https://agentgateway.dev/docs/standalone/latest/documentation/llm/transformations/>
- CEL variables and functions — <https://agentgateway.dev/docs/standalone/latest/reference/cel/variables/>
- Virtual models — <https://agentgateway.dev/docs/standalone/latest/documentation/llm/virtual-models/>
- OpenCode Go — <https://opencode.ai/docs/go/>
- open-webui docs — <https://docs.openwebui.com/>
