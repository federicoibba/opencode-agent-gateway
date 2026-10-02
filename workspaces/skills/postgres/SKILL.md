---
name: postgres
description: >-
  PostgreSQL schema design, indexing, EXPLAIN plans, N+1 avoidance, transactions
  and isolation, constraints, RLS basics, and connection pooling. Load when
  writing or reviewing SQL, a schema, or a slow query. Do not use for migration
  sequencing, which has its own skill.
metadata:
  short-description: PostgreSQL schema and query review
---

# PostgreSQL Patterns

Correct types, indexed access paths, and short transactions matter more than any
query micro-optimisation. Verify with a plan, not intuition.

## When to use

- Writing or reviewing SQL, schema DDL, or an ORM model.
- A query is slow, does a sequential scan, or hides an N+1.
- Adding indexes, constraints, or RLS policies.
- Configuring pooling, timeouts, or transaction boundaries.

Migration sequencing lives in the migrations skill.

## How to run

1. Get the query, the schema, and (if possible) `EXPLAIN (ANALYZE, BUFFERS)`.
   If a shell or DB is bound, run the plan; otherwise ask for it, plus
   `pg_stat_statements` rows. Never approve a query you have not planned.
2. Check types: `bigint`/`IDENTITY` (or UUIDv7) for IDs, `text` for strings,
   `timestamptz` for time, `numeric` for money, `boolean` for flags.
3. Check access: every WHERE/JOIN column and FK is indexed; composite indexes
   are equality-then-range; don't index a write-hot table without checking use.
4. Look for N+1: queries inside loops or per-row ORM lazy loads. Batch with
   `WHERE id = ANY($1)` or a join; batch inserts/upserts, never one per row.
5. Check transactions: keep them short, set isolation deliberately, lock in a
   consistent order, use `SKIP LOCKED` for queues, and never span an API call.
6. Enforce integrity in the database: PK, FK with `ON DELETE`, `NOT NULL`,
   `CHECK`, unique — do not rely on application code alone.
7. Multi-tenant: enable RLS, index the policy column, and use
   `USING ((SELECT auth.uid()) = user_id)` so the function is evaluated once.

## Quick reference

| Query pattern | Index |
|---------------|-------|
| `col = v` / `col > v` | B-tree |
| `a = x AND b > y` | composite `(a, b)` |
| `jsonb @>` / `tsv @@` | GIN |
| large time ranges | BRIN |
| active rows only | partial `WHERE deleted_at IS NULL` |

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;                      -- confirm, not guess
SELECT * FROM products WHERE id > $last ORDER BY id LIMIT 20;  -- cursor, O(1)
UPDATE jobs SET status = 'processing' WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED) RETURNING *;
```

Pooling: use a pooler (PgBouncer/Supabase); set `statement_timeout` and
`idle_in_transaction_session_timeout`; size `max_connections` to RAM. Own one
pool per service instance, not per request.

## Pitfalls

- `SELECT *` in production; missing index on a foreign key or RLS column.
- Wrong types: `int` IDs, `varchar(255)` by habit, `timestamp` without tz,
  floating money.
- Random UUIDv4 PKs fragmenting B-tree inserts; prefer `IDENTITY`/UUIDv7.
- N+1 queries from lazy loading; RLS disabled, or a per-row policy function.

## Verification

State the plan operator you expect (e.g. "Index Scan on idx_orders_status") and
ask to see `EXPLAIN (ANALYZE, BUFFERS)` on representative data. If no database
was reachable, say the plan was not run and name the query to check.

<!-- adapted from affaan-m/ECC: skills/postgres-patterns, agents/database-reviewer.md -->
