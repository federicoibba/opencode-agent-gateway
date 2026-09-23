"""Shared constants: tags, directory names and the gateway session header."""

TAG_PREFIX = "workspace:"
# Every managed skill/prompt carries this tag, so --prune only ever deletes
# things this repo created.
SHARED_TAG = f"{TAG_PREFIX}shared"

# Custom header that gives the gateway a stable per-chat session. open-webui has
# no env var that applies to an existing install, so the sync sets it on the
# gateway's OpenAI connection through the admin API.
GATEWAY_SESSION_HEADER = {"x-opencode-session": "{{CHAT_ID}}"}
GATEWAY_CONNECTION_MATCH = "agentgateway"

AGENTS_DIR = "agents"
SHARED_SKILLS = "skills"
SHARED_MCPS = "mcps"
SHARED_PROMPTS = "prompts"
YAML_EXTS = (".yml", ".yaml")
