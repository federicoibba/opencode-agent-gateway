---
name: docs-writer
description: >-
  Write and update task-oriented READMEs, guides, API docs, and changelog
  entries, keeping examples runnable and docs in sync with code. Load when
  documenting a feature or fixing stale docs. Do not use to restate code line by
  line or when current upstream docs matter.
metadata:
  short-description: Task-oriented docs that stay in sync
---

# Documentation Writer

Good docs answer "how do I accomplish X" with a path that actually runs. Docs
that drift from the code are worse than none.

## When to use

- Adding a feature, endpoint, config flag, or dependency that needs documenting.
- A README, guide, or changelog is stale or missing.
- The user asks for setup or usage instructions.

Do not hand-write library or framework API behavior from memory; look up
current upstream docs first (see Verification). Do not narrate code line by line.

## How to run

1. **Identify the reader and the task.** Write for the person trying to get work
   done, not the person who wrote the code.
2. **Structure by task**, not by file:
   - **README**: what it is, install, a runnable quickstart, tasks, config, links.
   - **Guide**: one goal per page, numbered steps, copy-pasteable commands.
   - **API doc**: endpoint or function, params, return, errors, a minimal example.
   - **Changelog**: Added / Changed / Fixed / Removed, user-visible, linked to PRs.
3. **Make examples real.** Verify every command and snippet compiles or runs;
   use real names, never a secret value.
4. **Update adjacent docs** — README, `.env.example`, config tables, and
   references to renamed things, in the same change as the code.
5. **Add a freshness signal** where the project uses one (version or date).

## Quick reference

```markdown
# Project — one-line what + who it's for.
## Install
<command>
## Quickstart
1. <step that works> → expected output
## Configuration
| Name | Default | Purpose |
## API
`fn(args) -> result` — errors: ...
```

Changelog entry: `### Fixed` → `- Reject expired session tokens (#123)`.

## Pitfalls

- Untested snippets with wrong flags, renamed functions, or fake paths.
- Writing for the author's mental model instead of the reader's first attempt.
- Duplicating content across files; link to one source of truth instead.
- Missing prerequisites (runtime version, env vars, permissions), or copying
  real credentials into an example instead of placeholders.

## Verification

Every example must run as written; if a shell is bound, execute the setup and
quickstart commands and confirm the output, otherwise flag which snippets are
unverified. For behavior of third-party libraries, fetch current upstream docs
before writing, and cite the version when it matters.

<!-- adapted from affaan-m/ECC: agents/doc-updater.md, skills/documentation-lookup/SKILL.md -->
