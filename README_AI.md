# TinhLuongCongDoan AI Entry Point

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Mandatory Start](#2-mandatory-start)
- [2.1 First-Prompt Governance Gate](#21-first-prompt-governance-gate)
- [3. Operating Rules](#3-operating-rules)
- [4. Mandatory Response Format](#4-mandatory-response-format)
- [5. Governance Onboarding Route](#5-governance-onboarding-route)
- [6. Quick Links](#6-quick-links)
- [7. Conversation Context Capacity and Fresh-Chat Handoff](#7-conversation-context-capacity-and-fresh-chat-handoff)
- [8. Golden Rule](#8-golden-rule)

## 1. Purpose

This repository belongs to **TinhLuongCongDoan** — a payroll calculation
system for post-office operational stages (starting with **Phát**;
**Thu Gom**, **Vận chuyển**, **Khai thác** planned as future modules).

It is designed so any AI session can onboard quickly, without guessing
workflow or reading random files, and is the single external entry point
for fresh AI continuity.

This governance model is a lean, single-executor adaptation of a larger
multi-agent standard used on a prior project. Here there is **one**
executor role: **Claude Code**. It plans, decides purely technical
questions, implements, tests, documents, and reports directly to the
Product Owner — there is no separate coordinator chat and no other
executor (see `docs/01_GOVERNANCE/PROJECT_DECISIONS.md` `DEC-001`,
`DEC-002`).

## 2. Mandatory Start

Every AI session must:

1. Read `README_AI.md` (this file).
2. Read [docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md) before writing or executing any first ticket-level plan.
3. Read [docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md).
4. Read the Current Manifest referenced by `PROJECT_SNAPSHOT.md`, if any (`Current Ticket = None` means there is no manifest to read yet).
5. Read only the Required Reading listed by that manifest.
6. Prefer the GitHub Blob URLs embedded in this onboarding chain once the repository is pushed to `origin/main`; until then, use repository-relative paths.

## 2.1 First-Prompt Governance Gate

Before writing the first execution plan in any new AI/chat session, read
`docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md`.

Until read, do not start implementation work framed as a "ticket."

The first execution plan for a new ticket defaults to:

- one defect or objective only;
- delta-only scope;
- fewer than `250` words of *plan* framing (does not limit code/tests
  themselves) unless Governance explicitly allows an exception;
- no repetition of Manifest content, SSOT text, ticket history, or
  repository-owned instructions.

## 3. Operating Rules

Claude Code must:

- follow Governance and Authority Level defined in this doc set
- not change SSOT (`docs/01_GOVERNANCE/PROJECT_CONTEXT.md` Section on
  Frozen Decisions, and `PROJECT_DECISIONS.md`) without explicit PO approval
- not skip Reading Order
- not change frozen documents unilaterally
- not infer business rules — ask the Product Owner only for business
  rules, product behavior, SSOT, acceptance criteria, or product
  direction; decide purely technical choices without escalation
- own implementation, automated testing, build/lint, and targeted
  technical runtime checks
- treat Product Owner visible UI/product acceptance as separate from
  technical validation (see `PO_UI_ACCEPTANCE_WORKFLOW.md`)
- stop at `READY FOR PO CHECK` when `PO UI Check Required = Yes`
- provide a concise manual PO checklist for visible changes
- not perform broad UI acceptance or award PO PASS on its own authority
- before drafting or executing a ticket-level plan, follow
  `docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md` and
  `docs/01_GOVERNANCE/DEVELOPE_DOCUMENTATION_STANDARD.md`; active-ticket
  follow-ups default to delta-only and `LEVEL 1` unless broader scope is
  explicitly justified

## 4. Mandatory Response Format

Audience: Product Owner. After onboarding and for post-onboarding
continuation, implementation-result review, remediation findings,
validation failures, and next-ticket activation, Claude Code should
respond with this concise three-part format when reporting to the
Product Owner (full technical detail always remains available in the
ticket/checkpoint documents in the repository, and inline in the
conversation when the Product Owner asks for it):

1. `### Phân tích kết quả`
   - fewer than 5 sentences
   - state only the result, finding, blocker, or readiness
   - use Product Owner management/no-code language
2. `### Phương án`
   - fewer than 5 sentences
   - state the immediate execution path
3. exactly one of:
   - `### Kế hoạch thực thi` (Claude Code proceeds directly — no
     separate "hand off a prompt" step exists in a single-executor model)
   - `### Yêu cầu PO quyết định`

Do not use class names, function names, code paths, raw logs, or
technical jargon in the first two sections unless necessary for a PO
decision. Put technical detail in the ticket document, validation
evidence, or a dedicated technical note.

This format is a communication convenience for PO-facing summaries, not
a requirement for every single reply in an ongoing working conversation
— use judgment for routine back-and-forth.

## 5. Governance Onboarding Route

`README_AI.md`

↓

[docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md)

↓

[docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md)

↓

No active ticket — no Current Manifest to read (`Current Ticket = None`,
`AWAITING PO DIRECTION`).

↓

Most recently closed: **Milestone 1 — Phát Module MVP** (Django
multi-user webapp: `core` + `phat` apps, RBAC scoped by post office,
daily raw-data import, provisional piece-rate calculation, Excel export,
unmatched-mapping report). `COMPLETED / TECHNICAL SELF-VERIFIED` — see
`PROJECT_SNAPSHOT.md` for full closure detail. No PO UI PASS has been
formally recorded yet under this governance model (it predates this
document set); the Product Owner has used the app directly and raised no
FAIL.

↓

Current project state is owned by `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md`.

Ticket naming conventions do not change this route; the live state must
always be resolved from `README_AI.md` → `DEVELOPE_PROMT_STANDARD.md` →
`PROJECT_SNAPSHOT.md` → Current Manifest → Required Reading.

## 6. Quick Links

- [docs/01_GOVERNANCE/AI_COLLABORATION_PROTOCOL.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/AI_COLLABORATION_PROTOCOL.md)
- [docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md)
- [docs/01_GOVERNANCE/DEVELOPE_DOCUMENTATION_STANDARD.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/DEVELOPE_DOCUMENTATION_STANDARD.md)
- [docs/01_GOVERNANCE/PO_UI_ACCEPTANCE_WORKFLOW.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/PO_UI_ACCEPTANCE_WORKFLOW.md)
- [docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md)
- [docs/01_GOVERNANCE/MASTER_START_PROMPT.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/MASTER_START_PROMPT.md) fallback reference only
- [docs/01_GOVERNANCE/DOCUMENT_INDEX.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/DOCUMENT_INDEX.md)
- [docs/01_GOVERNANCE/DOCUMENT_GOVERNANCE.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/DOCUMENT_GOVERNANCE.md)
- [docs/01_GOVERNANCE/DOCUMENT_UPDATE_MATRIX.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/DOCUMENT_UPDATE_MATRIX.md)
- [docs/01_GOVERNANCE/PROJECT_CONTEXT.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/PROJECT_CONTEXT.md)
- [docs/01_GOVERNANCE/PROJECT_DECISIONS.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/01_GOVERNANCE/PROJECT_DECISIONS.md)
- [docs/06_REVIEWS/Shared/PO_REVIEW_TEMPLATE.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/06_REVIEWS/Shared/PO_REVIEW_TEMPLATE.md)
- [docs/06_REVIEWS/Shared/PO_FINDINGS_REGISTER.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/docs/06_REVIEWS/Shared/PO_FINDINGS_REGISTER.md)
- [PROJECT_STATUS.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/PROJECT_STATUS.md)
- [PROJECT_PROGRESS.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/PROJECT_PROGRESS.md)
- [README.md](https://github.com/binhle116-dev/TinhLuongCongDoan/blob/main/README.md) — human-facing setup/run guide (separate purpose from this file)

## 7. Conversation Context Capacity and Fresh-Chat Handoff

Claude Code must monitor whether the current conversation has become
excessively long, repetitive, or likely to lose critical project
context.

One conversation serves one ticket or one major delivery wave. Start a
new conversation only for a new ticket, a new major wave, or materially
different work scope.

When context risk is high, proactively tell the Product Owner to open a
new conversation, and provide a concise handoff: repository, branch,
current phase, current ticket, current manifest, latest commit, PO
status, next required action, unresolved decisions.

The new conversation must begin from `README_AI.md`, not from copied
chat memory alone. Repository governance is authoritative; conversation
history is temporary working context.

## 8. Golden Rule

Every AI session must start from `README_AI.md` and follow the
manifest-driven route above. `MASTER_START_PROMPT.md` and the full
governance chain are fallback references only when the manifest requires
them, an authority conflict exists, or SSOT/business-rule/PO-acceptance
interpretation is involved. Do not skip the manifest-driven route.
