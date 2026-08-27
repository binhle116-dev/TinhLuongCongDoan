# PROJECT DECISIONS

Numbered, frozen decision log. An entry here is authoritative once the
Product Owner has actually approved it — Claude Code may draft an entry
but must not mark it approved on its own (see `DOCUMENT_GOVERNANCE.md`
Section 1). Do not edit or delete a numbered entry once recorded;
supersede it with a new entry that references the old one if it changes.

| ID | Date | Decision | Status |
| --- | --- | --- | --- |
| DEC-001 | 2026-08-27 | This project uses a single-executor governance model: Claude Code plays both the coordinator ("CTO") and implementer role in one session, reporting directly to the Product Owner. There is no separate Claude-chat coordinator role. | Approved |
| DEC-002 | 2026-08-27 | The `Antigravity` (UI/UX + Windows runtime specialist) and `Codex` (legacy implementation engineer) roles from the prior project's governance model are dropped entirely — no such tools exist in this environment and this project has no historical Codex work to preserve. | Approved |
| DEC-003 | 2026-08-27 | Module Phát's rebuild (Milestone 1) uses Django + SQLite (WAL mode) + waitress, run via Windows Task Scheduler (or NSSM later if reliability requires it), chosen for a non-professional-developer Admin on Windows, internal LAN/VPN only, modest concurrency. See `PROJECT_CONTEXT.md` Section 7. | Approved |
| DEC-004 | 2026-08-27 | Module Phát's piece-rate pay uses **"đơn giá chốt nội bộ BĐTP Huế"** as its pricing basis, not the official "đơn giá TCT" — even though the two are known to disagree (see `PROJECT_CONTEXT.md` Section 6). This carries forward a decision already made in an earlier prototype, validated against real July 2026 figures. | Approved |
| DEC-005 | 2026-08-27 | `ServiceMapping`, `RouteGroupMapping`, and `PriceCard` are intentionally left empty at Milestone 1 delivery rather than populated with inferred/guessed values, because the service-code-to-category mapping and the route-to-price-group mapping are not fully confirmed (see `PROJECT_CONTEXT.md` Section 6). Every "công theo sản lượng" figure reads as 0 until these are populated via Django admin. This is by design, not a defect. | Approved |
| DEC-006 | 2026-08-27 | The governance document rename `CODEX_DOCUMENTATION_STANDARD.md` → `DEVELOPE_DOCUMENTATION_STANDARD.md` (proposed by Claude Code for naming consistency) is confirmed by the Product Owner. | Approved |
| DEC-007 | 2026-08-27 | Connecting this repository to `https://github.com/binhle116-dev/TinhLuongCongDoan.git` (git init, remote add, first push) is authorized by the Product Owner. | Approved |
| DEC-008 | 2026-08-27 | The prior project's `AUTO-BACKFILL-UI_PLAN.md` example is recreated as `docs/10_TICKETS/PRICING_MAPPING_BACKEND_FIRST_PLAN.md`, renamed because "AUTO-BACKFILL-UI" is meaningless outside the source project — content illustrates the same backend-first/UI-second principle using Module Phát's real pricing/mapping work instead. | Proposed — needs Product Owner confirmation |

## How to add a decision

1. Draft the row with the next sequential `DEC-0xx` ID, today's date, and a one-sentence decision statement.
2. Mark its Status `Proposed` until the Product Owner has actually approved it in conversation.
3. Once approved, update Status to `Approved` in the same edit — do not leave it `Proposed` after approval is given.
4. If a later decision changes an earlier one, add a new row that says so explicitly (e.g. "Supersedes DEC-004") rather than editing the old row.
