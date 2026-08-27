# Lean Execution Standard for Claude Code

Filename: `DEVELOPE_PROMT_STANDARD.md` (renamed from the prior project's
`CODEX_PROMPT_STANDARD.md`; spelling of "Promt" preserved per Product
Owner instruction). This project has a single executor — Claude Code —
so there is no "which executor/model" selection section here; see
`PROJECT_DECISIONS.md` `DEC-001`/`DEC-002` for why.

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Lean Plan Rule](#2-lean-plan-rule)
- [2.1 First-Prompt Governance Gate](#21-first-prompt-governance-gate)
- [2.2 Active-Session Delta Rule](#22-active-session-delta-rule)
- [3. Active-Ticket Delta Rule](#3-active-ticket-delta-rule)
- [Single-defect remediation](#single-defect-remediation)
- [4. Validation Levels](#4-validation-levels)
- [5. Mandatory Handoff](#5-mandatory-handoff)
- [6. Active Manifest Readiness Gate](#6-active-manifest-readiness-gate)
- [7. Post-Onboarding Behavior](#7-post-onboarding-behavior)
- [8. Minimal Default Ticket Template](#8-minimal-default-ticket-template)
- [9. Output Standard](#9-output-standard)
- [10. Technical Validation vs PO UI Acceptance](#10-technical-validation-vs-po-ui-acceptance)
- [11. Additional PO/User Decision Rule](#11-additional-pouser-decision-rule)
- [12. Conversation Context Capacity](#12-conversation-context-capacity)
- [13. Self-Pass Criteria](#13-self-pass-criteria)
- [14. Reporting](#14-reporting)

## 1. Purpose

This document defines the lean standard Claude Code follows once it has
completed onboarding (`README_AI.md`). It replaces the "CTO writes a
prompt for an executor" step of the original protocol with "Claude Code
scopes the ticket for itself and proceeds" — the discipline (lean scope,
validation levels, one-defect-per-remediation) is preserved because it
is useful regardless of whether one AI or several are involved.

## 2. Lean Plan Rule

When starting a ticket, the internal plan/scope statement should stay
concise and avoid duplicating content already in the repository. It
should normally include only:

- Ticket objective
- Any Product Owner decision not yet stored in the repository
- Scope restriction (In / Out)
- Required completion and handoff instruction

It should not duplicate: Required Reading already listed in an existing
manifest, business context already defined there, or standard Governance
rules (commit/push/documentation/handoff) already defined in
`AI_COLLABORATION_PROTOCOL.md`.

If a ticket name would conflict with the Current Ticket in
`PROJECT_SNAPSHOT.md`, stop and report the conflict instead of guessing
which one is correct.

## 2.1 First-Prompt Governance Gate

In every new session, `README_AI.md` routes here before the first ticket
is scoped. Until this document has been read, do not frame work as a
ticket with formal completion/handoff obligations (ordinary
conversation/question-answering is unaffected).

The first ticket in a new session defaults to one independently
verifiable objective, delta-only scope, and a plan framing under `250`
words unless a documented exception applies.

## 2.2 Active-Session Delta Rule

This clarifies Section 2.1 for continuation inside the same active
session. Once Claude Code has read the onboarding chain in the current
session and already holds the ticket's context, the next step in the
same session does not need to repeat the onboarding recitation — state
only the new defect, delta, or decision (Section 3).

Re-read onboarding in full only when a genuinely new session starts. If
unclear whether context was lost, re-read rather than assume continuity.

## 3. Active-Ticket Delta Rule

Follow-up work within an active ticket should describe only the new
defect, delta, or decision — not the whole manifest, ticket history, or
already-accepted evidence.

Local defects default to `LEVEL 1` validation. Escalation above `LEVEL 1`
requires a one-sentence justification.

Required workflow: `Khoanh vùng → đọc tối thiểu → xác minh nguyên nhân →
sửa đúng chỗ → test đúng phạm vi → dừng.`

## Single-defect remediation

When the Product Owner reports multiple independent defects, handle one
independently verifiable defect at a time. Do not mix frontend, backend,
or business-logic fixes unless evidence proves one shared root cause.

Report root cause, changed scope, and validation for each defect. Confirm
the current defect `PASS` with the Product Owner before starting the
next one when the fixes are otherwise unrelated.

## 4. Validation Levels

`LEVEL 1 — Targeted Checks` (default for active-ticket local defects):
read only directly affected files/components; run focused tests that
prove the fix; do not run a broad/repository-wide check unless evidence
requires escalation.

`LEVEL 2 — Module Regression`: use when the defect can affect a shared
service (e.g. `core.permissions`, `phat.services.pricing`) or a repeated
workflow. Include focused checks plus relevant regression tests.
Escalation from `LEVEL 1` requires a one-sentence justification.

`LEVEL 3 — Handoff / Release Validation`: use for ticket closure, PO
handoff, or high-risk cross-module changes (e.g. anything touching
`core` models shared by future modules). Include focused checks, module
regressions, `python manage.py test`, migrations check, and handoff
evidence. Escalation requires a one-sentence justification.

## 5. Mandatory Handoff

Before reporting a ticket complete:

- update the ticket document/manifest status, if one exists
- update `PROJECT_SNAPSHOT.md`
- append exactly one new line to `PROJECT_PROGRESS.md` when Current
  Ticket changes; never edit or delete prior lines
- register new documents in `DOCUMENT_INDEX.md`
- review whether `CLAUDE.md` needs an update
- commit using One Ticket = One Commit (once Git is connected)
- push to `origin/main` and verify the remote commit (once authorized)
- confirm a fresh onboarding read (starting only from `README_AI.md`)
  would let a new session reach the current state without guessing

## 6. Active Manifest Readiness Gate

Before activating a next ticket that has a dedicated manifest under
`docs/10_TICKETS/`, verify it:

- describes the actual active ticket (not a stale placeholder)
- contains sufficient scope definition or an explicit blocker state
- defines In Scope and Out of Scope
- defines validation, documentation, PO, and handoff requirements
- does not require guessing or additional user clarification to start

`PROJECT_SNAPSHOT.md` exclusively owns mutable current project state
(Current Phase, Current Ticket, Current Manifest, PO Status). A manifest
should reference `PROJECT_SNAPSHOT.md` for that instead of duplicating it.

For a project this size, most tickets will not need a dedicated manifest
file — `PROJECT_SNAPSHOT.md` plus the conversation is enough. Create a
manifest under `docs/10_TICKETS/` when a ticket is large enough to need
its own durable scope document that will outlive one conversation.

## 7. Post-Onboarding Behavior

When onboarding completes and no governance blocker exists, proceed
directly into ticket work without waiting for another user request,
using the Product-Owner-facing format for the summary
(`### Phân tích kết quả` / `### Phương án` / `### Kế hoạch thực thi`).

Stop only when the situation is genuinely `BLOCKED`, `WAITING FOR PO`,
`WAITING FOR SSOT`, `WAITING FOR REQUIREMENT`, or another explicit
blocking state.

When review finds a remediable issue, do not stop after reporting it —
propose the fix, and proceed once any needed PO decision is made.

## 8. Minimal Default Ticket Template

```text
PROJECT
TinhLuongCongDoan

TICKET
[Active Ticket]

Onboarding already read this session (or: read README_AI.md → PROJECT_SNAPSHOT.md → Current Manifest first).

Objective:
[one sentence]

Additional PO/User Decision:
[Only include a decision not yet stored in the repository, otherwise: None]

Scope:
- In: [...]
- Out: [...]

Restrictions:
- Do not infer missing business rules.
- Do not modify frozen or unrelated files (see AI_COLLABORATION_PROTOCOL.md Section 7).
- Apply the mandatory validation, documentation, commit, push, and handoff workflow.
- Do not perform PO UI acceptance; do not self-award PO PASS.
- Provide a concise manual PO checklist for visible changes.

Report:
- Product-Owner-facing three-part format for the milestone summary.
- Full technical detail preserved in the ticket document / PROJECT_SNAPSHOT.md, not omitted for brevity.
```

## 9. Output Standard

A ticket plan/report is valid when it is sufficient to implement and
verify the ticket by following the repository onboarding chain, while
staying lean (under 250 words for the plan framing) unless a documented
exception applies.

## 10. Technical Validation vs PO UI Acceptance

Claude Code owns technical validation: implementation, tests, migrations,
targeted checks, contract/data correctness.

Product Owner owns: visible UI correctness, chart/table presentation,
filter behavior, wording, usability, and final product acceptance.

Browser automation is optional, not default — use it only when a defect
can only be proven in a browser, or the Product Owner requests it. Any
browser evidence Claude Code captures remains technical evidence, never
PO PASS.

`READY FOR PO CHECK` requires the applicable technical pass and a
concise PO checklist: screen/URL, required test context, filters/actions
to perform, expected result, PASS/WARNING/FAIL criteria.

## 11. Additional PO/User Decision Rule

An "Additional PO/User Decision" may contain only temporary execution
clarification that does not change business rules, scope, SSOT, or
frozen behavior. Any authoritative change must first be recorded in
`PROJECT_DECISIONS.md` or the relevant document — not implemented from a
decision that exists only in chat.

## 12. Conversation Context Capacity

Monitor whether the conversation has become excessively long or risks
losing context. One conversation serves one ticket or major wave. When
context risk is high, tell the Product Owner to open a new conversation
and provide a concise handoff (see `README_AI.md` Section 7).

## 13. Self-Pass Criteria

Claude Code may self-pass a technical change — close it as `PASS`
without a separate Product Owner decision request — only when **all
four** hold together:

1. The change implements only technical scope already approved; it does
   not infer a new business rule.
2. The change does not touch UI (UI always requires the Product Owner's
   own eyes before `PASS` — Section 10).
3. The change does not raise operational risk (does not newly enable a
   real write, a real send, or any new live capability).
4. The change does not alter schema or the meaning of business data.

If even one is missing, escalate to the Product Owner as normal. Self-pass
never applies when `PO UI Check Required = Yes`, and it is authority to
close a report that already satisfies all four — not authority to skip
validation or the handoff in Section 5/6.

## 14. Reporting

There is one reporting relationship in this project: **Claude Code →
Product Owner**. Use the three-part format (`README_AI.md` Section 4)
for milestone-level summaries. For routine work, plain concise updates
in the conversation are fine.

For continuity across sessions, record real technical detail (what
changed, why, validation performed, residual risk) in
`PROJECT_SNAPSHOT.md`, `PROJECT_PROGRESS.md`, and — for tickets large
enough to warrant one — a ticket document under `docs/10_TICKETS/` or a
review under `docs/06_REVIEWS/`. This detail is for the next session
reading the repository, not a report to another AI role.

Target length for a milestone technical record: roughly 100-250 words
for a simple/docs-only change, 250-500 words for a real defect with root
cause — go longer only when evidence genuinely requires it. Do not pad
with unused headings or process narration (which file was read in what
order, restrictions simply followed with nothing to report).
