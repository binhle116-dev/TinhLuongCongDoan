# PROJECT SNAPSHOT

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Current Snapshot](#2-current-snapshot)
- [3. Usage Rules](#3-usage-rules)
- [4. Continuation Notes](#4-continuation-notes)

## 1. Purpose

This document is the current-state snapshot for AI onboarding in
**TinhLuongCongDoan**. It is the shortest safe entry point for a new
session, second only to `README_AI.md`.

## 2. Current Snapshot

| Field | Value |
| --- | --- |
| Current Phase | `Module Phát — Milestone 1 (MVP) COMPLETED. No further phase activated yet.` |
| Current Ticket | `None — AWAITING PO DIRECTION` |
| Next Ticket | `Not yet chosen by the Product Owner. Candidates: (a) populate ServiceMapping/RouteGroupMapping/PriceCard once TCHC/TCKH confirms the mapping; (b) formal PO UI Acceptance pass on Milestone 1 under this governance model; (c) start module Thu Gom. See Section 4.` |
| Last PO Status | `Product Owner has used Milestone 1 directly (logged into /admin/, explored roles) and raised no FAIL. No formal PO PASS has been recorded under PO_UI_ACCEPTANCE_WORKFLOW.md yet, since that document did not exist until this ticket.` |
| Current Branch | `Not yet a Git repository — see Repository Status below.` |
| Current Manifest | `None — no ticket-specific manifest exists yet under docs/10_TICKETS/.` |
| Current Checkpoint | `None yet.` |
| Current State | `Django app runnable locally (python serve.py or run_app.bat). Real data imported once (SanLuongChiTiet_26082026.xlsx, 6706 rows). Demo/test data created during verification has been cleaned up; only the real import and the admin superuser remain.` |
| Technical Status | `10/10 automated tests pass (python manage.py test). python manage.py check reports no issues. Manual browser walkthrough confirmed RBAC scoping (404 cross-office, 403 admin-only page), allowance entry auto-calculation, Excel export scoping, and the unmatched-mapping report.` |
| Runtime Status | `Verified via manual browser session (Claude Browser tool) during Milestone 1, not via a standing runtime check. No production deployment yet — waitress entrypoint (serve.py) exists and was smoke-tested; no Windows Scheduled Task has actually been created yet (commands documented in README.md, not yet run).` |
| PO UI Check Required | `Not yet decided for Milestone 1 retroactively — this governance document set is new. Recommend the Product Owner do a first PO_UI_ACCEPTANCE_WORKFLOW.md pass before treating Milestone 1 as fully "Module Completed" under this standard.` |
| PO Product Status | `Not formally recorded. Product Owner has not reported a FAIL.` |
| Last Closed Ticket | `MILESTONE-1-PHAT-MVP — COMPLETED / TECHNICAL SELF-VERIFIED (2026-08-27). See PROJECT_PROGRESS.md for the one-line record.` |
| Last Closed Manifest | `None — Milestone 1 was executed before this manifest-driven governance model existed; its design record lives in the Claude Code plan history for this project, not in docs/10_TICKETS/.` |
| Repository Status | `Git init + first commit + remote (https://github.com/binhle116-dev/TinhLuongCongDoan.git) authorized by Product Owner (DEC-007), being executed in this ticket. See Continuation Notes for the exact push confirmation step.` |
| Governance Version | `V1 (this document set) — first created 2026-08-27, adapted from a prior project's multi-agent standard into a single-executor (Claude Code only) model. See PROJECT_DECISIONS.md DEC-001 through DEC-005.` |
| Last Updated | `2026-08-27` |

## 3. Usage Rules

- Read this document immediately after `README_AI.md`.
- Treat this document as the single live project-state snapshot for AI onboarding.
- Do not infer current state from chat history when this snapshot is available.
- Do not use this document to override `PROJECT_DECISIONS.md` or Product
  Owner decisions.
- Whenever `Current Ticket` changes, append exactly one new line to
  `PROJECT_PROGRESS.md`'s ticket history in the same update; never edit
  or delete prior lines. This snapshot does not itself keep history —
  see Section 4 for narrative continuity notes instead.

## 4. Continuation Notes

This section carries narrative context that the one-line
`PROJECT_PROGRESS.md` entries can't — the "why", not just the "what".

**2026-08-27 — Governance document set created.** The Product Owner
asked to replicate an AI-collaboration documentation standard from a
prior, much larger multi-agent project (`tntTan2292/TTVH-DHCL`, QIS V2:
Product Owner + Claude-chat-as-CTO + Antigravity + Claude Code + legacy
Codex). For `TinhLuongCongDoan`, the Product Owner explicitly chose a
leaner single-executor adaptation: Claude Code alone plays both the
coordinator and implementer role, `Antigravity` is dropped entirely (no
such tool exists in this environment), and `Codex` is dropped entirely
(no historical Codex work to preserve). The Product Owner did ask to
keep the full governance folder structure (`docs/01_GOVERNANCE/`,
`docs/06_REVIEWS/`, `docs/10_TICKETS/`) despite the smaller team, so the
supporting documents these core files reference (`DOCUMENT_INDEX.md`,
`PROJECT_DECISIONS.md`, `PROJECT_CONTEXT.md`, etc.) were created too,
rather than leaving dangling links. The 8th file from the original
request, `AUTO-BACKFILL-UI_PLAN.md`, was initially deferred pending its
source link; the Product Owner then provided it. Its content (a 2-phase
backend-then-UI plan for a KPI backfill feature) doesn't transfer
literally, so it was recreated as
`docs/10_TICKETS/PRICING_MAPPING_BACKEND_FIRST_PLAN.md` (`DEC-008`,
proposed), illustrating the same principle with Module Phát's real
pricing/mapping backend as the worked example instead.
`CODEX_DOCUMENTATION_STANDARD.md`
was renamed to `DEVELOPE_DOCUMENTATION_STANDARD.md` for naming
consistency with the Product-Owner-requested rename of
`CODEX_PROMPT_STANDARD.md` → `DEVELOPE_PROMT_STANDARD.md` — this second
rename was Claude Code's own proposal and has since been confirmed by
the Product Owner (`DEC-006`).

**Prior to this, 2026-08-27 — Module Phát rebuilt as Milestone 1.** The
Product Owner initially asked for a simple single-user Python script
that reads an already-computed monthly Excel file. That was built,
found a real double-counting bug (a "Tuyến Trại Giam" allowance already
baked into the source file's total was also being added a second time
from a manual template — fixed by removing the manual addition), and was
then extended to auto-read directly from the monthly master workbook.
The Product Owner then asked to also auto-pull and auto-price from a
*daily* raw production feed (`SanLuongChiTiet_DDMMYYYY.xlsx`, pulled via
WinSCP from an internal SFTP server). Investigating that surfaced a
harder problem: the source organization's own "chốt nội bộ" (internally
finalized) price is derived through a manual monthly calibration against
a budget figure that isn't in the data at all, and there may be a
separate, more authoritative "Thống kê sản lượng phát" report distinct
from the raw `SanLuongChiTiet` feed used for pricing — neither is safe to
guess. Rather than keep patching a single-user script around an
uncertain pricing pipeline, the Product Owner asked to throw away that
prototype and restart with the *actual* end-goal requirement: a proper
multi-user, role-based system (Admin / Phòng ban / Trưởng bưu cục, one
account per post office, scoped access) covering all 4 stages
eventually, Phát first. That is what Milestone 1 (Django, `core` +
`phat` apps) delivered — see `PROJECT_CONTEXT.md` for the full technical
and business background, and `PROJECT_DECISIONS.md` for the specific
frozen decisions (stack choice, pricing basis, RBAC mechanism).

The Milestone 1 build intentionally left `ServiceMapping`,
`RouteGroupMapping`, and `PriceCard` empty rather than guess at the
mapping — this is by design (`DEC-005`), not unfinished work that was
forgotten. The `/bao-cao/chua-anh-xa/` (unmatched report) view exists
specifically so the Product Owner or TCHC/TCKH can see exactly what
mapping is still needed from real imported data.
