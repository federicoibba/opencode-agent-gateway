---
name: architecture
description: >-
  System and boundary design: dependency direction, ports and adapters,
  trade-off analysis, scalability, deployment topology, and decision framing.
  Load when proposing a new service, refactor, or boundary, or reviewing one.
  Do not use for line-level code review or schema mechanics.
metadata:
  short-description: Design boundaries and trade-offs
---

# Architecture

Good architecture makes the next change cheap: clear boundaries, dependencies
pointing inward, and decisions recorded with their trade-offs.

## When to use

- Proposing a new feature, service, or cross-cutting component.
- Refactoring framework- or I/O-heavy code where domain logic is entangled.
- Evaluating options (monolith vs service, queue vs sync, DB vs cache).
- Assessing scalability, deployment topology, or failure modes.

## How to run

1. State the problem and constraints first: functional need, non-functional
   targets (latency, throughput, availability), team size, and deadline.
2. Read the code or design the user shares. Map current patterns before
   proposing anything; fit the repo instead of importing a favourite.
3. Draw the boundaries: domain (rules, no framework imports), application/use
   cases (orchestration), ports (interfaces the app owns), adapters (HTTP, DB,
   queue, SDK), and one composition root that wires them.
4. Enforce dependency direction: adapters -> application -> ports; domain ->
   nothing external. No adapter calls another adapter directly.
5. For each significant decision, write options with pros, cons, and the reason
   rejected; name the one you would pick and why. Record it as an ADR.
6. Pressure-test scaling in stages (current, 10x, 100x): what breaks first —
   database, hot partition, synchronous call? Name the mitigation and trigger.
7. Define operations: deployment units, health checks, rollback, and how the
   change fails. Keep the smallest viable architecture; defer speculation.

## Quick reference

```text
dependency direction (inward):
  HTTP/CLI/worker --> inbound adapter --> use case --> domain model
                                             |
                                             v
                                   outbound port (interface)
                                             ^
                                             |
                                   outbound adapter --> DB / API / queue
```

```text
internal/<feature>/
  domain/        entities, value objects, rules
  application/   use cases + ports/
  adapters/      inbound/ (http), outbound/ (postgres, <vendor>)
  composition/   or wire in cmd/<app>/main.go
```

Trade-off table: Option | Pros | Cons | Rejected because. Always include the
"do nothing / simplest" baseline.

## Pitfalls

- Domain importing ORM models, framework types, or vendor SDKs.
- Abstractions added before there is a second implementation or a real seam.
- Choosing a pattern because it is fashionable, not because it fits.
- Ignoring operational cost: migrations, monitoring, on-call, rollback.
- Scalability hand-waving with no bottleneck named or measurement trigger.

## Verification

Name the boundary you changed and one test or check that proves it holds
(contract test, dependency direction, or a load figure). Ask for the design
artifact or repo access if none was shared, and flag assumptions.

<!-- adapted from affaan-m/ECC: agents/architect.md, agents/code-architect.md, skills/hexagonal-architecture -->
