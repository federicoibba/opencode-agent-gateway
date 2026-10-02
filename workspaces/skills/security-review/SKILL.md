---
name: security-review
description: >-
  Review code for trust-boundary and OWASP-class flaws: hardcoded secrets,
  injection, SSRF, unsafe deserialization, broken authz, weak crypto, and
  vulnerable dependencies or cloud IAM. Load when code handles user input,
  auth, files, payments, or external calls. Do not use for general style review.
metadata:
  short-description: OWASP and trust-boundary security review
---

# Security Review

One real vulnerability can outweigh every other review comment. This skill
checks the trust boundaries where untrusted input crosses into privileged
operations.

## When to use

- New or changed API endpoints, auth, session, or permission code.
- Code handling user input, file uploads, URL fetching, payments, or webhooks.
- Secret handling, dependency upgrades, or cloud/IAM configuration.
- Before a release or after a CVE in a dependency.

Do not use it for cosmetic or architectural review; pair it with `code-review`.

## How to run

1. **Map trust boundaries.** For each entry point, name the untrusted source
   (request, webhook, uploaded file, third-party API) and what privileged
   operation it can reach.
2. **Scan for secret and injection patterns** (see Quick reference).
3. **Check authn/authz** on every state-changing and data-returning route.
4. **Check dependencies and IAM.** If a shell is bound, run the project's audit
   (`npm audit --audit-level=high`, `pip-audit`, etc.); otherwise review the
   lockfile or ask for the audit output.
5. **Report with severity** and a concrete fix; for CRITICAL findings, tell the
   user immediately and recommend rotating exposed credentials.

## Quick reference

| Pattern | Severity | Fix |
|---------|----------|-----|
| Hardcoded secret or token in source | CRITICAL | Move to env/secret store; rotate |
| String-concatenated SQL, shell, or template | CRITICAL | Parameterize; use safe APIs / `execFile` |
| No authz check before a privileged op | CRITICAL | Enforce server-side role/ownership check |
| Password compared in plaintext | CRITICAL | Use bcrypt/argon2 `compare` |
| `fetch(userUrl)` reachable by user | HIGH | Allowlist hosts; block metadata IPs (SSRF) |
| Unsafe deserialization of user input | HIGH | Parse with a schema; avoid native deserializers |
| `innerHTML` or raw template with user data | HIGH | Escape or sanitize; set CSP |
| Weak crypto: MD5/SHA1 for passwords, `Math.random` | HIGH | Use a vetted KDF and CSPRNG |
| Missing rate limiting on auth or expensive routes | HIGH | Add a limiter |
| Secrets or PII in logs or error responses | MEDIUM | Redact; return generic messages |
| Over-broad cloud IAM or wildcard policy | HIGH | Scope to least privilege |

Also verify: HTTPS enforced; CSRF protection on state-changing forms; tokens in
`HttpOnly; Secure; SameSite` cookies; external XML entities disabled; dependencies
current.

## Pitfalls

- Do not flag `.env.example` values, test fixtures, or intentionally public keys.
- MD5/SHA256 for checksums is fine; it is only weak for passwords/integrity use.
- Report a finding only with a named source, a privileged sink, and a bypass of
  existing controls; otherwise it is speculation.
- Sanitizing on input is not a substitute for encoding on output.
- An allowlist beats a denylist every time.

## Verification

Name the control, not just the risk: "request body reaches `db.query` with
concatenation at `src/routes.ts:42`". If you cannot run the dependency audit or
inspect the cloud config with the tools bound here, ask the user for the
`npm audit` / `pip-audit` output or the IAM policy document.

<!-- adapted from affaan-m/ECC: agents/security-reviewer.md, skills/security-review/SKILL.md -->
