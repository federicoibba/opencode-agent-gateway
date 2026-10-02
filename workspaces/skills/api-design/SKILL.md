---
name: api-design
description: >-
  HTTP/REST resource modelling, status semantics, versioning, pagination,
  idempotency, error envelopes, and OpenAPI as the single contract. Load when
  the user designs or reviews an endpoint, payload, or API change. Do not use
  for database schema or internal Go structure decisions.
metadata:
  short-description: Design consistent HTTP APIs
---

# API Design

Design the observable contract first: resources, methods, status codes, error
shape, and pagination. Consumers should be able to predict every response.

## When to use

- Designing or reviewing REST endpoints, resource names, or payload shapes.
- Adding pagination, filtering, sorting, or versioning.
- Changing an error response or status code that clients depend on.
- Frontend and backend (or two services) need to build in parallel.

## How to run

1. Restate the consumer job: what must a client render or do, and which fields
   are required? Design from that, never from the storage row.
2. Model resources as plural lowercase nouns; reserve verbs for state
   transitions (`POST /orders/{id}/cancel`). Nest only for ownership.
3. Pick methods by semantics: GET safe, PUT/DELETE idempotent, POST creates.
   Return real status codes (201 with `Location`, 204, 404, 409, 422, 429).
4. Define one error envelope — `{ "error": { "code", "message", "details"? } }`
   — and reuse it. Never return 200 with `success: false`; never leak internals.
5. Choose pagination: cursor (`WHERE id > $cursor ORDER BY id LIMIT n+1`) for
   large or concurrent tables; offset only for small admin views.
6. If a contract file (OpenAPI/AsyncAPI/proto) exists, make it the source of
   truth: change it first, regenerate types and mocks, then implement both sides.
7. Classify the change: additive is backward-compatible; renaming or removing a
   field, changing a type, or changing auth needs a new version or migration.

## Quick reference

| Method | Safe | Idempotent | Use for |
|--------|------|-----------|---------|
| GET | yes | yes | read, list |
| POST | no | no | create, actions |
| PUT | no | yes | full replace |
| PATCH | no | no* | partial update |
| DELETE | no | yes | remove |

| Status | When |
|--------|------|
| 201 / 204 | created / no body |
| 400 / 422 | malformed JSON / semantic validation |
| 401 / 403 | unauthenticated / not allowed |
| 404 / 409 | missing / duplicate or state conflict |
| 429 | rate limited, send `Retry-After` |

Idempotency: honor an `Idempotency-Key` on POST, store the key with the
response, and replay it on retry. Non-breaking changes are the ones in step 7.

## Pitfalls

- Verbs in resource URLs, singular resource names, or snake_case paths.
- One-off status codes or a bespoke error shape per endpoint.
- OFFSET pagination on a large, actively written table.
- Exposing database columns or internal IDs as if they were the contract.
- Versioning by silently repurposing an existing field.
- Documenting the API only in prose while the code drifts.

## Verification

Point to the OpenAPI/proto artifact and name one request/response you would
validate against it, including an error path. If no contract or shell is bound,
state that the spec and generated types were not checked.

<!-- adapted from affaan-m/ECC: skills/api-design, skills/contract-first -->
