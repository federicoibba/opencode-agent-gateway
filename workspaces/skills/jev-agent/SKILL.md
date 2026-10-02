---
name: jev-agent
description: >-
  Use the Jev AI decision API from an AI coding agent when a workflow needs a
  typed choice, score, or yes/no judgment for routing, classification,
  verification, context compression, or a safety gate. On first use, guide the
  user through language, API key, and help configuration. Do not use it for
  open-ended writing, deterministic rules, exact lookups, or final permission
  enforcement.
metadata:
  short-description: Add typed Jev decisions to agent workflows
---

# Jev Agent

Jev AI is a decision service for software and agents. It receives application
state plus explicit typed questions and returns structured answers with
probabilities. The agent or application still owns the workflow, permissions,
human approval, and final action.

## First-use onboarding

This agent runs against a gateway that already holds the Jev API key. Before the
first Jev request in a session, check whether the `jev_systemone` tool is
available. Do not search shell history, repository files, or unrelated files for
secrets, and never ask the user to paste an API key into the conversation.

In this deployment the environment variables below are handled by the gateway,
not by you:

```text
JEV_LANGUAGE      response language; optional, defaults to en-US
JEV_API_KEY       held by the gateway; injected upstream, never sent to you
JEV_API_BASE_URL  optional API origin; default https://thejevai.com
JEV_MODEL         optional model id; default jev-latest
```

Follow the language the surrounding agent is configured for. Do not ask the user
to choose a language unless they raise it. The language controls the agent's
communication and question wording; it does not change the model's API contract.

If the `jev_systemone` tool is missing, or the gateway reports `401`/`402`,
explain that the Jev API key is configured on the gateway (its `JEV_API_KEY`
setting, from `https://thejevai.com/settings/apikeys`) and ask the operator to
check it. Never ask for or accept the key value yourself.

Never print, log, commit, or place an API key in source code, a markdown
example with a real value, a client bundle, or a generated artifact.

During onboarding, show this short help in the configured language and then
return to the user's task. The default English help is:

```text
Jev Agent can help you:
- use Choice for classification, routing, and selecting among candidates;
- use Score for risk, priority, and quality ratings;
- use Noul for yes/no probabilities, gates, escalation, and human review.

Basic flow: prepare minimal state → ask a clear question → read answers → let
your code or agent decide the next action.
Jev judges; it does not write long-form content, execute tools, or grant
permissions.
```

When `JEV_LANGUAGE=zh-CN`, present the same help in Simplified Chinese:

```text
Jev Agent 可以帮助你：
- 用 Choice 做分类、路由和候选项选择；
- 用 Score 做风险、优先级和质量评分；
- 用 Noul 做真假概率、放行、升级和人工复核判断。

基本流程：准备最小 state → 提出明确问题 → 读取 answers → 由代码或 Agent 执行动作。
Jev 负责判断，不负责写长文本、执行工具或授予权限。
```

If the user asks for `help`, `帮助`, configuration, or a setup check later,
show the same help in the configured language and report only whether the key
is present; never reveal its value.

## When to use Jev

Use Jev when the answer space can be defined before the request and the result
will drive a program or agent branch, for example:

- route a task, ticket, request, or context to one of several known paths;
- classify or extract a bounded value from text;
- score urgency, risk, quality, or complexity on an ordered rubric;
- decide whether evidence is sufficient, a tool call needs review, or a task
  should be escalated;
- decide whether old context should be kept, truncated, or dropped.

Do not call Jev for prose generation, code generation, explanations, exact
database lookups, arithmetic, authentication, authorization, or a rule that
can be expressed deterministically. For high-impact actions, Jev may provide
a risk signal, but deterministic policy, permissions, and human approval must
remain authoritative.

## API contract

The gateway exposes the hosted API as the `jev_systemone` tool. It calls:

```http
POST https://thejevai.com/v1/systemone
Authorization: Bearer <injected by the gateway>
Content-Type: application/json
```

Call the tool; do not send an `Authorization` header and do not try to read the
key. The default model is `jev-latest`; the tool applies it when `model` is
omitted.

The request body has three required fields:

```json
{
  "model": "jev-latest",
  "state": "A customer was charged twice for the same order.",
  "questions": {
    "needs_human": {
      "type": "noul",
      "instructions": "Does this case require human review before a refund?"
    }
  }
}
```

`state` can be a string, object, or array. Send only the facts needed for the
decision and remove secrets, payment credentials, and unrelated personal data.

Question types:

- `choice`: choose one option from a `criteria` object;
- `score`: evaluate an ordered scale in a `criteria` array;
- `noul`: return the probability that a yes/no statement is true.

Ask one narrow judgment per question. Batch related independent questions in
one request when they share the same state. Do not make a later question depend
on an earlier answer in the same request; make a second request after the
application has obtained the needed evidence.

The tool returns one of two response shapes, depending on the host the gateway
targets. Accept both.

**Flat (TypeSafe, `api.typesafe.ai`)** — answers at the top level:

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "needs_human": {
      "type": "noul",
      "noul": 0.94
    }
  },
  "usage": {
    "input_tokens": 42,
    "output_tokens": 23
  }
}
```

**Wrapped (hosted Jev, `thejevai.com`)** — answers under `data.result`, with a
status `code`:

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "result": {
      "answers": {
        "needs_human": {
          "type": "noul",
          "noul": 0.94
        }
      },
      "usage": {
        "input_tokens": 42,
        "output_tokens": 0
      },
      "elapsedMs": 180
    },
    "creditsUsed": 1
  }
}
```

To read answers regardless of shape, take `response.answers` if it is present,
otherwise `response.data.result.answers`. The same applies to `usage`
(`response.usage` or `response.data.result.usage`) and to the model id
(`response.model` or `response.data.result.model`). Only check `code` when the
field exists: the flat shape has none, so a missing `code` is **not** a failure.

For `choice` and `score`, inspect the returned `choice` or `score`, its
`probabilities`, and `confidence`. For `noul`, inspect `noul` as a value from
0 to 1. Treat probabilities and confidence as signals, not proof or
authorization. Choose thresholds from the user's actual risk and historical
data; do not invent a universal threshold.

## Calling the API

Use the `jev_systemone` tool, passing the request body as its arguments. Do not
make a live request merely to demonstrate that the Skill exists; when the user
has asked for a Jev-backed workflow, make the call as part of that workflow. A
deliberate low-risk test is fine, but avoid unrequested calls that consume
credits or carry sensitive data.

Tool arguments (the same body the REST endpoint takes):

```json
{
  "model": "jev-latest",
  "state": "The customer has tried to connect Stripe for three days.",
  "questions": {
    "urgent": {
      "type": "noul",
      "instructions": "Does this message express urgency?"
    }
  }
}
```

Ask before making an otherwise unrequested request that can consume credits or
contains sensitive data. A Jev request itself does not execute the action being
judged.

Handle failures explicitly:

- non-2xx responses: surface the status and safe error message;
- wrapped shape only: if `code` is present and not `0`, do not read the response
  as a valid result;
- no answers found via `answers` or `data.result.answers`: treat the response as
  invalid;
- `401`: tell the user the gateway's Jev API key is missing, invalid, or issued
  for a different host than the gateway targets; never ask them to paste a key
  into the conversation;
- `402`: tell the user the gateway's Jev account needs credits;
- timeout, `429`, or upstream failure: use bounded retry with backoff only when
  the surrounding workflow is safe to retry;
- never repeat a consequential action just because the decision request failed.

## Agent safety boundary

This Skill teaches an agent when and how to ask Jev for a judgment. It does not
create a new tool, grant authority, intercept shell calls, or enforce a policy
outside the agent's existing permissions. The agent must still ask for user
confirmation when required, obey the current workspace and tool restrictions,
and keep irreversible actions behind deterministic checks and normal approval
boundaries.

Keep question definitions, business thresholds, and action mapping in a small,
reviewable code location. Record the model version, question definitions, safe
input summary, decision, and final action when the workflow needs an audit
trail, but never record the API key.

## Installation and help

This skill is installed locally at `workspaces/agents/jev/skills/jev-agent/`
and is reconciled into open-webui by `workspace-sync`. It is bound to the `Jev`
agent and lazy-loaded through open-webui's skill mechanism. Ask the agent to
`use the Jev Agent skill` or run a configuration/help request. The first-use
onboarding above must happen before the first live Jev request.

For current product details and account actions, use:

- API documentation: `https://thejevai.com/docs`
- API key management: `https://thejevai.com/settings/apikeys`
- Playground: `https://thejevai.com/playground`
