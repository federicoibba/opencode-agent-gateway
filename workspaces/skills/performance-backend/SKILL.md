---
name: performance-backend
description: >-
  Measure-first backend performance work: profiling, latency vs throughput,
  allocation and GC, lock contention, N+1 and query cost, caching, and
  timeouts/backpressure. Load when a service is slow or memory-heavy. Do not use
  to micro-optimize without a measurement or for frontend Web Vitals.
metadata:
  short-description: Measure-first backend performance tuning
---

# Backend Performance

Optimize only what a measurement proves is slow. An unmeasured change is a
guess that adds risk and often shifts the bottleneck elsewhere.

## When to use

- A service is slow, CPU-bound, memory-heavy, or timing out under load.
- Adding caching, connection pooling, batching, or backpressure.
- Reviewing a hot path, query, or concurrent code for cost.

Do not use it for frontend rendering or Core Web Vitals, or to change code whose
cost was never measured.

## How to run

1. **Define the goal and the metric.** Latency (p50/p95/p99) or throughput
   (req/s)? For which endpoint and load? "Faster" is not a target.
2. **Measure first.** If a profiler is bound, capture a profile (`py-spy`,
   `node --prof`, `pprof`, `perf`, DB `EXPLAIN ANALYZE`) before editing;
   otherwise ask the user for a profile, flame graph, or query plan.
3. **Find the dominant cost** — the one line, query, or lock that owns the time.
   Do not tune everything at once.
4. **Fix the cause, then re-measure** with the same workload and compare.
5. **Add a guard** so the regression is caught: a benchmark, load test, or
   query-cost assertion in CI.
6. **State the tradeoff** you introduced (memory for speed, staleness for cache).

## Quick reference

| Symptom | Likely cause | First check |
|---------|--------------|-------------|
| High p99, low CPU | lock contention, queueing | contention profile, pool size |
| High CPU | hot loop, JSON, regex | CPU flame graph |
| Memory grows, GC pauses | allocation churn, leak | heap profile, allocation rate |
| Many small queries | N+1 | query log, `EXPLAIN`, batching |
| Repeated slow query | missing index, full scan | `EXPLAIN ANALYZE`, index |
| Slow external call | no timeout, no cache | per-call timers, cache hit rate |
| Load-dependent failure | no backpressure | queue depth, timeouts, limits |

```text
Latency:    p50/p95/p99; the tail dominates user pain
Throughput: req/s at fixed concurrency and error budget
Always:     same workload before/after; report the delta
```

## Pitfalls

- Micro-optimizing a cold path; the profiler rarely agrees with intuition.
- Caching without invalidation or TTL; turns a slow bug into a stale bug.
- Adding a cache before checking the query or index.
- Unbounded concurrency or queues: faster locally, dead under load.
- Ignoring GC and allocation pressure when chasing throughput.
- "Optimizing" by removing a timeout, retry, or backpressure guard.

## Verification

Report the before/after numbers for the same workload (p95 latency, req/s, query
time) and the tool that produced them. If you cannot profile here, do not claim
an improvement; ask the user to run the profiler or benchmark and share the
output.

<!-- adapted from affaan-m/ECC: agents/performance-optimizer.md -->
