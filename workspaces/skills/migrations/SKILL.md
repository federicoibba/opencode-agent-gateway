---
name: migrations
description: >-
  Safe PostgreSQL schema and data migrations: expand/contract, backward-
  compatible changes, zero-downtime DDL, backfills, locking, reversibility, and
  a review checklist. Load when writing or reviewing a migration or planning a
  deploy. Do not use for query tuning or day-to-day schema design.
metadata:
  short-description: Safe reversible migrations
---

# Database Migrations

Production migrations are forward-only, tested against production-sized data,
and never edit history. Schema and data changes ship separately.

## When to use

- Adding, altering, or dropping columns, tables, or indexes.
- Backfilling or transforming existing data.
- Planning a zero-downtime or rollback strategy.
- Reviewing a migration before it runs in production.

Not for writing new queries (postgres skill) or designing a schema from scratch.

## How to run

1. Classify the change: schema (DDL) or data (DML). Never mix them.
2. For rename/type change use expand-contract: add the new shape, deploy code
   that writes both, backfill, switch reads, then drop the old; never rename.
3. Keep every change backward-compatible with the currently deployed code: add
   nullable columns or columns with a constant default; do not add `NOT NULL`
   without a default to an existing table.
4. For large tables use non-blocking DDL: `CREATE INDEX CONCURRENTLY` (outside a
   transaction) and batched backfills (`LIMIT` in a loop, `SKIP LOCKED`).
5. Bound locking: set `lock_timeout` and `statement_timeout` so a migration
   fails fast instead of queueing behind a long query.
6. Provide a rollback: a matching DOWN, or a new forward migration. Mark
   irreversible data migrations explicitly; never edit a deployed migration.
7. Test on production-sized data; if no DB is bound, ask for the table sizes.

## Quick reference

```sql
-- Add column safely (nullable, or constant default on PG11+)
ALTER TABLE users ADD COLUMN avatar_url TEXT;
-- Index without blocking writes (cannot run inside a transaction)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
-- Batched backfill
UPDATE users SET display_name = username
WHERE id IN (SELECT id FROM users WHERE display_name IS NULL
             LIMIT 10000 FOR UPDATE SKIP LOCKED);
-- Make it NOT NULL only after the backfill completes
ALTER TABLE users ALTER COLUMN display_name SET NOT NULL;
```

golang-migrate:
```bash
migrate create -ext sql -dir migrations -seq add_user_avatar
migrate -path migrations -database "$DATABASE_URL" up
migrate -path migrations -database "$DATABASE_URL" down 1
```

Expand: add -> write both -> backfill -> read new -> drop old (days 1-7).

## Pitfalls

- `NOT NULL` without a default on a populated table: full rewrite plus lock.
- Inline `CREATE INDEX` on a large, write-heavy table; schema and data mixed.
- Dropping a column before the code stops referencing it.
- Editing an already-deployed migration, or no rollback documented.

## Verification

Name the lock behavior and the rollback path, and say which table size the
migration was tested against. If no shell or DB was available, state that the
migration was reviewed statically and list what to run (staging apply, EXPLAIN,
`lock_timeout`).

<!-- adapted from affaan-m/ECC: skills/database-migrations -->
