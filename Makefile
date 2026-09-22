# Convenience wrappers around docker compose.
.PHONY: help up down restart logs models smoke pull config

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-10s %s\n", $$1, $$2}'

up: ## Start (or apply changes to) the stack
	docker compose up -d

down: ## Stop the stack (keeps the open-webui volume)
	docker compose down

restart: ## Recreate containers (needed after changing .env)
	docker compose up -d --force-recreate

logs: ## Tail agentgateway logs
	docker compose logs -f agentgateway

models: ## List the models exposed by the gateway
	curl -s http://localhost:3000/v1/models | python3 -m json.tool

smoke: ## Send a test chat completion through the gateway
	curl -s http://localhost:3000/v1/chat/completions \
	  -H 'content-type: application/json' \
	  -d '{"model":"glm-5.3-flash","max_tokens":32,"messages":[{"role":"user","content":"Say hi in three words."}]}' \
	  | python3 -m json.tool

pull: ## Pull updated images and recreate
	docker compose pull && docker compose up -d

config: ## Validate config.yml and the compose file
	docker compose config --quiet && echo "compose OK"
