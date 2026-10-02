# Operations

[Home](../README.md) · [Architecture](architecture.md) · [Configuration](configuration.md) · [Agents](agents.md) · [Troubleshooting](troubleshooting.md)

## Common commands

```bash
docker compose up -d          # start / apply changes
docker compose ps             # status
docker compose logs -f agentgateway   # gateway logs (every request is logged)
docker compose logs -f open-webui     # UI logs
docker compose pull && docker compose up -d   # update images
docker compose down           # stop (keeps the open-webui and agentgateway-data volumes)
docker compose down -v        # stop AND delete containers, networks and volumes (wipes all data)
```

The `mise.toml` tasks wrap the common commands: `mise run up`, `down`, `restart`,
`logs`, `models`, `smoke`, `pull`, `config`, `setup-deps`, `sync-workspaces`,
`workspaces`, and `destroy` (`mise tasks` lists them all).

## Lifecycle and data

- `config.yml` is mounted **read-write** and is edited on the host.
  `config.storage.mode: hybrid` sends UI-created resources to the database, so the
  file is never rewritten (see [Editing config](configuration.md#editing-config)).
- **`llm.*` changes** are **hot-reloaded** — no restart needed (watch for
  `loaded config from File("/config.yml")` in the logs).
- **`config.*` changes** (admin address, logging, database) are **startup-only** —
  restart the container: `docker compose restart agentgateway`.
- **Env var changes** require a restart: `docker compose up -d --force-recreate`.
- open-webui data (accounts, chats, connection settings) lives in the
  `open-webui` named volume.
- The gateway's request-log database (behind the UI Logs/Analytics pages) lives in
  the `agentgateway-data` named volume. `docker compose down` keeps it;
  `docker compose down -v` deletes it, along with the logs.

## Testing the Jev tool

The `jev` MCP target is a good end-to-end check of the gateway's MCP path: it
exercises an OpenAPI target, a route to an external host, and the injected key,
all without the chat UI. Call it in the **MCP Tool Playground** at
<http://localhost:15000/ui> → **MCP** → **Tool Playground**: pick the
`jev_systemone` tool and paste one of the bodies below as its `arguments`.

If the playground shows a full request field instead, wrap the body in
`{"name":"jev_systemone","arguments": …}`.

**Noul (yes/no probability):**

```json
{
  "body": {
    "state": "Help! My payouts have been failing for 3 days.",
    "model": "jev-latest",
    "questions": {
      "is_urgent": {
        "type": "noul",
        "instructions": "Does this convey urgency?"
      }
    }
  }
}
```

Expected — a flat TypeSafe envelope, not wrapped in `code`/`data`:

```json
{
  "model": "jev-1.13.0",
  "answers": { "is_urgent": { "type": "noul", "noul": 0.95 } },
  "usage": { "input_tokens": 283, "output_tokens": 23 }
}
```

**Choice (pick one option):**

```json
{
  "body": {
    "state": "Help! My payouts have been failing for 3 days.",
    "model": "jev-latest",
    "questions": {
      "team": {
        "type": "choice",
        "instructions": "Which team should handle this?",
        "criteria": {
          "billing": "Payments, invoicing, refunds",
          "technical": "Bugs, outages, integrations",
          "sales": "Pricing, upgrades, new accounts"
        }
      }
    }
  }
}
```

Do **not** add an `Authorization` header: the gateway injects the key from
`JEV_API_KEY`. The upstream status is logged, so a failure is easy to place:

```bash
docker compose logs agentgateway | grep 'v1/systemone' | tail -1
```

A `"http.status":200` means the gateway reached the API and the key was
accepted. `401` means the key was rejected — usually the key and the target host
disagree (a `thejevai.com` key does not authorise `api.typesafe.ai`, and vice
versa; see [Configuration](configuration.md#environment-variables)). With no
`JEV_API_KEY` set, the gateway fails to start rather than serving a broken tool.

## Teardown

`mise run destroy` wraps the destructive `down -v` with a confirmation prompt;
`-y` (or `FORCE=1`) skips it for scripting and tests:

```bash
mise run destroy        # asks for confirmation
mise run destroy -y     # no prompt
```

It deletes the open-webui volume (accounts, chats, settings) and the
agentgateway-data volume (request logs). Pulled images are left in place; add
`--rmi all` if you want those gone too.

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
- **Do not open the request-log SQLite DB from the host while the gateway is
  running.** Two writers across Docker Desktop's file sharing corrupt the WAL and
  cause `disk I/O error (522)`. To inspect it, stop the gateway first and read the
  `agentgateway-data` volume from a throwaway container.
- **The Logs DB stores request metadata, not message content** (model, status,
  tokens, duration, cost). To also capture prompts/completions, add
  `frontendPolicies.accessLog.database.llm: full`.
- **`config.logging.level: debug` is verbose** — it logs every SQL statement. Drop
  to `info` for normal use (`curl -X POST "http://localhost:15000/logging?level=info"`).
