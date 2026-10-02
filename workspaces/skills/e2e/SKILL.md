---
name: e2e
description: >-
  Design stable end-to-end browser tests: journey selection, semantic selectors,
  deterministic waits, test-data isolation, flake quarantine, and artifact
  capture for CI. Load when writing Playwright or Agent Browser tests or fixing
  a flaky E2E run. Do not use for unit logic or pure API contract tests.
metadata:
  short-description: Stable Playwright end-to-end testing
---

# End-to-End Testing

E2E tests are the last line before production: they catch integration breakage
unit tests cannot see. Stability matters more than coverage here.

## When to use

- Writing or maintaining Playwright (or Agent Browser) specs.
- A critical flow (login, checkout, signup, payment) needs a guard.
- A test is flaky in CI and must be diagnosed or quarantined.

Do not use it for pure functions or single-module logic — keep E2E few and
high-value and push detail down to unit and integration tests.

## How to run

1. **Pick journeys by risk.** Rank HIGH (auth, payments, data loss), MEDIUM
   (search, navigation), LOW (cosmetic). Test HIGH first.
2. **Model the page** (Page Object Model) and expose semantic locators.
3. **Write the spec** with assertions at each key step; capture artifacts at
   critical points.
4. **Replace all fixed sleeps** with condition waits.
5. **Run locally 3–5 times** to surface flakiness. If a shell is bound, use
   `--repeat-each=10`; otherwise ask the user to run it and paste results.
6. **Quarantine** unstable tests with `test.fixme(true, 'Flaky - Issue #N')` and
   track the issue; do not silently `skip`.
7. **Wire CI**: install browsers, run with `retries` on CI only, always upload
   the report and traces.

## Quick reference

| Concern | Do | Don't |
|---------|----|-------|
| Selector | `[data-testid="..."]`, role | CSS chains, XPath, index |
| Wait | `waitForResponse`, `expect(...).toBeVisible` | `waitForTimeout(5000)` |
| Data | per-test unique fixtures, own tenant | shared accounts or rows |
| Failure | trace/screenshot/video on failure | re-run until green |
| Flake | quarantine and file an issue | bump the timeout |

```typescript
// deterministic wait
await page.waitForResponse(r => r.url().includes('/api/search'))
await expect(page.getByTestId('results')).toBeVisible()

// config for debugging
use: { trace: 'on-first-retry', screenshot: 'only-on-failure',
       video: 'retain-on-failure' }
```

## Pitfalls

- `page.click(sel)` bypasses auto-wait; use `page.locator(sel).click()`.
- Tests that depend on each other or on seed data someone else mutated.
- Clicking mid-animation; wait for visibility or `networkidle` first.
- Retries on CI without fixing flakes: they hide real races.
- Asserting only the happy path; include the empty and error states.
- Committing artifacts; upload them and gitignore the output dir.

## Verification

Run the journey and report pass/fail with the artifact path. If you cannot run
the browser here, give the user the exact command
(`npx playwright test path --trace on`) and ask them to share the report or the
failing trace instead of claiming it passes.

<!-- adapted from affaan-m/ECC: skills/e2e-testing/SKILL.md, agents/e2e-runner.md -->
