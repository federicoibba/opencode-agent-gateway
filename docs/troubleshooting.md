# Troubleshooting

[Home](../README.md) · [Architecture](architecture.md) · [Configuration](configuration.md) · [Agents](agents.md) · [Operations](operations.md)

| Symptom | Cause / fix |
|---|---|
| `Request is missing x-opencode-session` | The request transformation is missing or the config did not reload. Check `config.yml` and the gateway logs for `loaded config`. |
| `Upstream request failed: Model is unavailable.` | A client sent `model: "*"`. The wildcard must stay `visibility: internal`. In open-webui, refresh the connection's model list and pick a real model or `fast`/`smart`. |
| `404 Model not found` from the gateway | The requested model is not one of the public entries. Add it to `config.yml`. |
| `error looking key 'OPENCODE_API_KEY' up` at startup | `.env` is missing or the variable is not set. Recreate with `docker compose up -d --force-recreate`. |
| open-webui shows no models | Refresh the connection (Settings → Admin → Connections). Check the base URL is `http://agentgateway:3000/v1` and the key is non-empty (a placeholder is fine — the gateway substitutes the real one). |
| open-webui still lists a stale `*` model | Hard-reload the page / click the connection's refresh icon; the list is cached client-side. |
| An agent has no system prompt | The prompt must land in `params.system` (open-webui reads it there, not from `meta`). Re-run `mise run sync-workspaces`; check `params.system` in `GET /api/v1/models/export`. |
| Agents/skills missing after `up` | The sync needs credentials. Set `WEBUI_ADMIN_EMAIL`/`WEBUI_ADMIN_PASSWORD` or `OPENWEBUI_API_KEY` in `.env`, then `mise run sync-workspaces`; read its output with `docker compose logs workspace-sync`. |
| `workspace-sync` fails: `ModuleNotFoundError: yaml` | The image needs rebuilding (`mise run sync-workspaces` uses `--build`), or run `mise run setup-deps` for the local dry-run. |
| `http://localhost:15000` won't load | The admin UI binds to loopback inside the container by default, which a Docker port mapping cannot reach. `config.adminAddr: "0.0.0.0:15000"` is set in `config.yml`; it is startup-only, so restart the container after changing it. |
| Admin UI save fails with `Read-only file system (os error 30)` | `config.yml` is mounted `:ro` in `docker-compose.yml`, so the UI cannot write back. Drop the `:ro` suffix (see [Editing config](configuration.md#editing-config)). |
| UI Logs page: `request log database is not configured` | No database is set. Add `config.database.url` (see [Configuration](configuration.md)) and restart. `config.logging.level`/`format` only affect the stdout stream, not the UI. |
| UI Logs page: `disk I/O error (code: 522)` | The SQLite DB is on a Docker Desktop **bind mount**. Use a named volume (`agentgateway-data:/data`) instead — SQLite's locking/mmap is unreliable on macOS file sharing. |
| Gateway exits with `failed to connect sqlite database` / `unable to open database file` | The `agentgateway-data` volume is root-owned but the gateway runs as uid `65532`, so it cannot create the DB. The `agentgateway-data-init` service chowns the volume on every `up` (this also repairs it after `mise run destroy`). If you removed that service, run `docker run --rm -v agent-gateway_agentgateway-data:/data alpine chown -R 65532:65532 /data` and start again. |
| Go returns `429` | A model hit its Go usage cap. Enable **Use balance** in the Zen console, or route around it (see `smart`). |
