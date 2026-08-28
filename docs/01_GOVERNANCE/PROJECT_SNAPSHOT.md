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
| Current Phase | `Module Phát — Milestone 1 (MVP) COMPLETED. Module Khai thác — MVP + per-employee split COMPLETED, all open pricing/mapping questions resolved (DEC-016 through DEC-018). See Section 4.` |
| Current Ticket | `None — AWAITING PO DIRECTION` |
| Next Ticket | `Not yet chosen by the Product Owner. Candidates: (a) resolve the remaining 80 distinct unmatched postman_code values in Phát's raw data (grew from 40 as more of August's data surfaced more codes - not a regression); (b) get PO/TCHC input on the 6 still-deliberately-unmapped Phát combos surfaced by DEC-019 (esp. whether "KT1 Hẹn giờ" is really meant to be a 0-priced service); (c) formal PO UI Acceptance pass on both modules; (d) start module Thu Gom or Vận chuyển. See Section 4.` |
| Last PO Status | `Product Owner has used Milestone 1 directly (logged into /admin/, explored roles) and raised no FAIL. No formal PO PASS has been recorded under PO_UI_ACCEPTANCE_WORKFLOW.md yet, since that document did not exist until this ticket.` |
| Current Branch | `Not yet a Git repository — see Repository Status below.` |
| Current Manifest | `None — no ticket-specific manifest exists yet under docs/10_TICKETS/.` |
| Current Checkpoint | `None yet.` |
| Current State | `Django app runnable locally (python serve.py or run_app.bat). Real data imported once (SanLuongChiTiet_26082026.xlsx, 6706 rows). Demo/test data created during verification has been cleaned up; only the real import and the admin superuser remain.` |
| Technical Status | `10/10 automated tests pass (python manage.py test). python manage.py check reports no issues. Manual browser walkthrough confirmed RBAC scoping (404 cross-office, 403 admin-only page), allowance entry auto-calculation, Excel export scoping, and the unmatched-mapping report.` |
| Runtime Status | `Verified via manual browser session (Claude Browser tool) during Milestone 1, not via a standing runtime check. No production deployment yet — waitress entrypoint (serve.py) exists and was smoke-tested; no Windows Scheduled Task has actually been created yet (commands documented in README.md, not yet run).` |
| PO UI Check Required | `Not yet decided for Milestone 1 retroactively — this governance document set is new. Recommend the Product Owner do a first PO_UI_ACCEPTANCE_WORKFLOW.md pass before treating Milestone 1 as fully "Module Completed" under this standard.` |
| Pricing Data Status | `Populated 2026-08-27 (DEC-009), extended 2026-08-28 (DEC-019): 48 ServiceCategory, 10 PriceGroup, 480 PriceCard rows, 221 RouteGroupMapping rows (verified 117/117 exact match against real route codes), 60 ServiceMapping rules (up from 47 - added 13 rules for "KT1 A/B/C"/"KT1 Hỏa tốc -A/B/C" after verifying they share the exact PriceCard as already-mapped "KT1 ABC"/"KT1 Hỏa Tốc ABC", plus 1 for "C-Bưu kiện" QT). Only 6 known-ambiguous combinations remain unmapped by design (down from 9/19) - see PROJECT_CONTEXT.md Section 6. New `rematch_unmatched` command re-applies mapping/postman_code to already-imported data without re-reading source files.` |
| Employee Data Status | `159 real employees (DEC-010), postman_code cross-validated against April 2026 reference data (DEC-011). PO supplied postman_code for 14/15 remaining new hires (DEC-012) - 129/159 now have a postman_code. 1 employee (00279833 NGUYEN VAN HIEU) intentionally left without one ("Mat tich" in source list, needs operations follow-up, not guessed). 00279646 NGUYEN XUAN LONG marked is_active=False per PO (DEC-013). 40 postman codes in real raw data still unmatched - visible via /bao-cao/chua-anh-xa/.` |
| UI Status | `Sidebar-based redesign shipped 2026-08-27 (DEC-015): module-grouped left nav (Phát active; Thu Gom/Vận chuyển/Khai thác shown disabled), BCVH filter on the Lương page + Excel export (RBAC-scoped). PO UI Check Required: Yes - verified working in a real browser session by Claude Code, but formal Product Owner visual review/PASS has not happened yet.` |
| Daily Data Coverage | `Full August 2026 imported 2026-08-27 (DEC-014): 26 days (01-26/08). Month sum recomputed 2026-08-28 after DEC-019's mapping fixes: 523,891,850.70d -> 542,680,336.05d (+18,788,485.35d, a real correction from 2,425 previously-unmapped rows). 2026-08-27 not yet exported by the source system. WinSCP saved site corrected to its real name cas_hue@10.1.45.10 (was documented as CAS_Hue_SFTP); scripts/pull_august_only.txt added for scoped historical backfills (do not use the unscoped -neweronly wildcard against a folder with years of history).` |
| PO Product Status | `Not formally recorded. Product Owner has not reported a FAIL.` |
| Last Closed Ticket | `MILESTONE-1-PHAT-MVP — COMPLETED / TECHNICAL SELF-VERIFIED (2026-08-27). See PROJECT_PROGRESS.md for the one-line record.` |
| Last Closed Manifest | `None — Milestone 1 was executed before this manifest-driven governance model existed; its design record lives in the Claude Code plan history for this project, not in docs/10_TICKETS/.` |
| Repository Status | `Git init + first commit + remote (https://github.com/binhle116-dev/TinhLuongCongDoan.git) authorized by Product Owner (DEC-007), being executed in this ticket. See Continuation Notes for the exact push confirmation step.` |
| Governance Version | `V1 (this document set) — first created 2026-08-27, adapted from a prior project's multi-agent standard into a single-executor (Claude Code only) model. See PROJECT_DECISIONS.md DEC-001 through DEC-005.` |
| Khai thác Module Status | `MVP + per-employee split shipped 2026-08-28 (DEC-016 through DEC-018): new app khaithac, direct SQL Server import (BCCP530100_2024 + BCCP530900) replacing the Excel/SFTP pattern used by Phát. Quỹ tiền lương computed per VB1054+VB1182 (4 Nhóm dịch vụ, date-versioned pricing) - all 12 Loại mapped, including KT1 (M-prefix) confirmed by PO as Nhóm EMS (DEC-018). Per-employee split implemented from the real shift roster ("BCC hệ số 2026 (LT).xlsx") per VB1054 §1.3 - July 2026 verified end-to-end (302.6 total hệ số matches the source file's own TỔNG cell; 17 employees paid, summing exactly to the 32,921,295đ fund). Hệ số chất lượng default of 1.0 for everyone is now a confirmed PO decision (DEC-018), not a placeholder.` |
| Last Updated | `2026-08-28` |

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

**2026-08-28 — Module Khai thác started (new app, new data-source
pattern).** The Product Owner asked to start module Khai thác (buu cuc
KTC1 Hue 1, ma `530100`) and offered SQL Server login directly, rather
than a daily Excel/SFTP feed like Phát. Before writing any payroll logic,
Claude Code first verified the T-SQL query the Product Owner supplied
(month-scoped, grouped by ca/ngay/loai) against real July 2026 data — 31/31
days present, no gaps, category totals internally consistent (~0.04%
residual not classified into R/E/C/U). The Product Owner then corrected
one data-source assumption: `KT1` (item codes starting `M`) is NOT in
`BCCP530100_2024` (which only had ~2 items/month there — clearly wrong for
a processing center this size) but in a *separate* database,
`BCCP530900`, where the real volume (~2,135 items/month) was confirmed.
Before writing pay logic, Claude Code also asked the Product Owner for (a)
the actual unit-price table and (b) how pay is split among employees per
shift — both genuinely unknown from the data. The Product Owner answered
by pointing to two real internal documents already on disk (`VB 1054/TB-
BĐHUE` and its amendment `VB 1182/TB-BĐHUE`), which gave both answers:
piece-rate pricing by 4 Nhóm dịch vụ (EMS/GHI_SO/BUU_KIEN/PHBC, 2 rate
periods in 2026), and a Hệ số ca formula for splitting the resulting fund
across employees (1.0/ca standard, 1.2/ca for a shift lead, quality
coefficient from a "Phụ lục 01" that does not exist in the file Claude Code
has access to). The MVP shipped everything computable from real data
today (raw import, Nhóm mapping, the priced monthly/daily/shift fund
total) and stopped short of the per-employee split, since that requires a
real shift roster (who worked which ca, which days, who was shift lead)
that does not exist yet in any file Claude Code has seen — this mirrors
the same "don't guess" principle used for Phát's `ServiceMapping` (DEC-005)
and is recorded as `DEC-016`.

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
