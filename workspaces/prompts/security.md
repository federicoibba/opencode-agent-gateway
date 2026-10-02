---
name: Security Review
description: Review code or a design for security vulnerabilities.
tags: [security, appsec]
---

Review the code or design I share, using the `security-review` skill (and
`threat-modeling` for a design):

1. Map the trust boundaries and where untrusted input enters.
2. Check the OWASP Top 10, secrets, injection, SSRF, unsafe deserialisation and
   authorization.
3. Rank findings by exploitability and impact.

For each: location, concrete failure mode, severity and the smallest fix. Never
print a real credential. End with what you could not verify.
