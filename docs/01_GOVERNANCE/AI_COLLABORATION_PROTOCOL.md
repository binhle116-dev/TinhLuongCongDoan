# AI COLLABORATION PROTOCOL

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Roles](#2-roles)
- [3. Standard Workflow](#3-standard-workflow)
- [4. Module Delivery Order](#4-module-delivery-order)
- [5. Review Workflow](#5-review-workflow)
- [6. Ticket Rules](#6-ticket-rules)
- [7. Architecture Protection Rules](#7-architecture-protection-rules)
- [8. Layering Rules](#8-layering-rules)
- [9. Context Rules](#9-context-rules)
- [10. Communication Rules](#10-communication-rules)
- [11. Handover Rules](#11-handover-rules)
- [12. Golden Rules](#12-golden-rules)
- [13. Ticket Completion Protocol](#13-ticket-completion-protocol)
- [14. Prompt/Plan Standard](#14-promptplan-standard)
- [15. Product Owner to Claude Code Collaboration Workflow](#15-product-owner-to-claude-code-collaboration-workflow)
- [16. PO UI Acceptance Gate](#16-po-ui-acceptance-gate)

## 1. Purpose

This protocol defines how the Product Owner and Claude Code work
together across the full lifecycle of **TinhLuongCongDoan**.

Purpose:

- keep decisions consistent
- preserve SSOT and frozen architecture
- prevent scope drift
- ensure ticket-by-ticket execution
- maintain continuity across sessions/handovers

This is a deliberately lean, single-executor adaptation (see
`PROJECT_DECISIONS.md` `DEC-001`, `DEC-002`) of a heavier multi-agent
protocol used on a prior project. There is no separate "CTO chat" and no
second executor role (`Antigravity`/`Codex`) in this project.

## 2. Roles

### Product Owner

- decides business direction
- approves or rejects proposals
- prioritizes roadmap
- freezes business decisions
- gives final acceptance (PO PASS / WARNING / FAIL)

### Claude Code

- Coordinator **and** Implementation Engineer in one role
- receives requests, scopes tickets, decides purely technical questions,
  implements, tests, documents, and reports
- executes only approved tickets; does not invent new scope
- does not change architecture or business rules by itself
- owns implementation, backend, data, tests, documentation, and Git
  (commit, push) once a remote is connected and pushing is authorized
- asks the Product Owner only for business rules, product behavior,
  SSOT, acceptance criteria, or product direction

## 3. Standard Workflow

Business Discussion → Architecture/Data-Model Decision → Technical
Planning → Development → Review → Next Ticket.

This workflow is sequential and must not be bypassed unless the Product
Owner explicitly changes the process.

## 4. Module Delivery Order

Each payroll module (Phát done; Thu Gom, Vận chuyển, Khai thác planned)
should be delivered in the following order:

Data model (`core`/module-specific models) → Import/Ingestion logic →
Business logic (calculation, RBAC scoping) → UI (views/templates) →
Review PASS → Next module.

Rules:

- The data model establishes structure shared with `core`.
- Import/ingestion logic gets raw data into the system safely
  (idempotent, never silently guessing at ambiguous mappings).
- Business logic implements calculation and access control.
- UI exposes the result to each role appropriately scoped.
- Review confirms readiness before moving to the next module.

## 5. Review Workflow

Claude Code reviews its own work against:

- Architecture (does it fit `core`'s shared model, RBAC scoping)
- Runtime (does it actually run — migrations, tests, manual check)
- Data correctness (does a computed number match a hand-verified case)
- Technical Debt
- PASS / WARNING / FAIL

Claude Code must not self-declare a **Product** PASS — only a
**Technical** PASS. Product acceptance belongs to the Product Owner
(Section 16).

## 6. Ticket Rules

Every ticket should identify:

- Goal
- Scope (In / Out)
- Validation performed
- Risk
- Commit (once Git is connected)

Additional rules:

- One Bug = One Ticket = One Commit
- no hidden scope expansion
- no unrelated refactor
- no cross-module rewriting
- keep ticket boundaries strict

## 7. Architecture Protection Rules

The following must not be changed without explicit Product Owner
approval (see `PROJECT_DECISIONS.md` for the authoritative list):

- The RBAC post-office scoping mechanism (`core/permissions.py`,
  `scope_queryset`) — this is the single mechanism every view/query
  touching post-office-scoped data must use.
- The decision to price piece-rate pay using "đơn giá chốt nội bộ BĐTP
  Huế" rather than "đơn giá TCT" (`DEC-004`).
- The decision to leave `ServiceMapping`/`RouteGroupMapping`/`PriceCard`
  empty rather than guess values (`DEC-005`).
- The `core` app's shared models (`PostOffice`, `Employee`,
  `UserProfile`) — changes here affect all four planned modules.

If a change affects any of the above, it must be treated as a decision
item for the Product Owner, not a code convenience.

## 8. Layering Rules

- Views own permission scoping (via `core.permissions.scope_queryset`);
  templates must not bypass it by querying the database directly.
- Business/pricing logic lives in `phat/services/` (or the equivalent
  `<module>/services/` for future modules), not scattered across views.
- Management commands (`phat/management/commands/`) are the entry point
  for scheduled/automated jobs (daily import, backup) — they call into
  `services/`, they do not duplicate its logic.
- A month once `MonthlyPayrollRun.status = FINALIZED` must not be
  silently recomputed by a later mapping-table edit (see
  `phat/services/pricing.py` docstring and `PROJECT_CONTEXT.md`).

## 9. Context Rules

Not yet applicable at this project's current size (single module, no
cross-screen drill-down state to preserve). When the UI grows multi-screen
navigation (e.g., dashboard → post office → employee detail), this
section should be filled in with the actual context fields that must
survive navigation, following the same principle as Section 8: do not
lose context, do not silently reset a parent screen's filters.

## 10. Communication Rules

Claude Code should use the Product-Owner-facing three-part format
(`README_AI.md` Section 4) for milestone-level summaries: onboarding
continuation, implementation-result review, remediation findings,
validation failures, and next-ticket activation. Ordinary in-conversation
back-and-forth does not require the formal format.

Claude Code must:

- keep the conversation anchored to SSOT and frozen documents
  (`PROJECT_DECISIONS.md`, `PROJECT_CONTEXT.md`)
- avoid inventing new business rules
- review before moving to the next ticket when review is required

Product Owner must:

- approve business changes
- approve architecture freezes
- approve ticket scope changes

## 11. Handover Rules

One conversation serves one ticket or one major delivery wave. Continue
remediation and validation for the same bounded ticket or wave in the
current conversation. Start a new conversation for a new ticket, a new
major wave, or materially different work scope.

Claude Code must proactively warn the Product Owner when the current
conversation is excessively long or risks mixing obsolete and current
authority.

Before changing conversations, update required repository evidence,
commit, push (once authorized), and verify the remote state.

When moving to a new session, it must read:

1. `README_AI.md`
2. `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md`
3. Current Manifest referenced by `PROJECT_SNAPSHOT.md`, if any
4. Only the Required Reading listed in the manifest
5. `docs/01_GOVERNANCE/DEVELOPE_DOCUMENTATION_STANDARD.md` when
   documentation workflow rules are needed
6. `docs/01_GOVERNANCE/PROJECT_CONTEXT.md` when business/technical
   background is needed
7. This document when protocol details are needed

The new session must not rely on chat memory as the source of truth.
Repository governance is authoritative; conversation history is
temporary working context.

## 12. Golden Rules

1. `PROJECT_DECISIONS.md` is the final reference for frozen decisions.
2. Runtime/test evidence is stronger than visual assumptions.
3. No business change without PO approval.
4. No architecture change without a recorded decision.
5. RBAC scoping is centralized (`core.permissions.scope_queryset`) —
   never re-implemented ad hoc in a view.
6. Mapping/pricing tables are never populated with guessed values.
7. Each ticket is isolated by scope.
8. Review comes before the next module.
9. Claude Code must preserve continuity across sessions, not recreate history.

## 13. Ticket Completion Protocol

A ticket is only `COMPLETED` when all applicable items below are
satisfied.

### 13.1 Source Code

Development is complete within the approved scope.

### 13.2 Build/Test

Relevant tests pass (`python manage.py test`), and `python manage.py
check` reports no issues.

### 13.3 Runtime Verification

Manual runtime check performed if the ticket touches user-facing
behavior (see `PO_UI_ACCEPTANCE_WORKFLOW.md`).

### 13.4 Review

Self-review against Section 5 passes.

### 13.5 Documentation Synchronization

Before committing, check and update if needed:

- `README_AI.md`
- `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md`
- current manifest under `docs/10_TICKETS/`, if any
- `docs/01_GOVERNANCE/DEVELOPE_DOCUMENTATION_STANDARD.md` when
  documentation workflow changes
- `docs/01_GOVERNANCE/PROJECT_CONTEXT.md`
- `CLAUDE.md` when governance workflow or roles change
- `PROJECT_PROGRESS.md` — append exactly one new line when Current
  Ticket changes; never edit or delete prior lines
- `PROJECT_STATUS.md` if the status changes
- `docs/01_GOVERNANCE/DOCUMENT_INDEX.md` if documents are added or moved
- `docs/01_GOVERNANCE/PO_UI_ACCEPTANCE_WORKFLOW.md` when PO UI review applies
- `docs/06_REVIEWS/Shared/PO_FINDINGS_REGISTER.md` when PO findings exist
- the ticket's review document, if one exists

### 13.6 Current Project State

Current Phase, Current Ticket, Next Ticket, and Repository Status are
owned by `PROJECT_SNAPSHOT.md`.

### 13.7 Commit Policy

A commit should include the required delivery artifacts for the ticket
(source code, documentation update, review update, progress update).
Source code must not be committed if Documentation Synchronization has
not been completed.

If `PO UI Check Required = Yes`, the ticket must not be described as
completed until the PO gate is satisfied.

### 13.8 Push Policy

After push (once a remote is connected and authorized), the report
should include: Completed Ticket, Next Ticket, Documentation Updated,
Repository Status, commit hash, and GitHub Blob URLs of updated
documents once available.

### 13.9 Plan Rule

Future tickets should follow this protocol by default; they may
reference it succinctly with: `Follow Ticket Completion Protocol defined
in AI_COLLABORATION_PROTOCOL.md`.

### 13.10 PO UI Acceptance Applicability

Every ticket must explicitly decide `PO UI Check Required: Yes` or `No`,
based on whether it produces a visible, independently checkable product
change. If `Yes`, follow `docs/01_GOVERNANCE/PO_UI_ACCEPTANCE_WORKFLOW.md`.

## 14. Prompt/Plan Standard

All future tickets should follow the canonical standard defined in
`docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md`.

## 15. Product Owner to Claude Code Collaboration Workflow

### 15.1 Mandatory Three-Part Response Format

See `README_AI.md` Section 4. Claude Code uses this for milestone-level
summaries to the Product Owner:

1. `### Phân tích kết quả` (< 5 sentences)
2. `### Phương án` (< 5 sentences)
3. exactly one of `### Kế hoạch thực thi` or `### Yêu cầu PO quyết định`

### 15.2 Post-Review Remediation Loop

When self-review finds an issue resolvable within the active ticket,
Claude Code must not stop after reporting the finding — it should
immediately propose and, once any needed PO decision is made, implement
the remediation, keeping the active ticket current until remediation,
revalidation, and required PO acceptance are complete.

Do not activate the next ticket before current-ticket PO PASS unless the
Product Owner explicitly permits parallel work.

Request a Product Owner decision only when the finding requires a
business-rule, SSOT, frozen-behavior, scope, threshold, acceptance, or
authority decision. A failed repository search alone is not sufficient
proof that authority does not exist — inspect `PROJECT_DECISIONS.md`,
`PROJECT_CONTEXT.md`, code, tests, and Git history first.

## 16. PO UI Acceptance Gate

The authoritative workflow lives in
`docs/01_GOVERNANCE/PO_UI_ACCEPTANCE_WORKFLOW.md`. The findings register
lives in `docs/06_REVIEWS/Shared/PO_FINDINGS_REGISTER.md`.

Rules:

- PO Product Review PASS belongs to the Product Owner.
- Technical PASS is not Product PASS.
- Runtime PASS is not Product PASS.
- A module cannot be marked completed before the applicable PO gate is satisfied.
- PO findings must be traced to a responsible ticket or backlog decision.
