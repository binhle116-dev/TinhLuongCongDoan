# PROJECT STATUS

Very short, human-readable summary. For the full AI-oriented live state
(branch, manifest, technical/runtime status), see
`docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` — that document is authoritative
when the two ever disagree.

**Last updated:** 2026-08-27

## Where things stand

- **Module Phát**: v3 rebuilt as a multi-user Django webapp (`core` +
  `phat` apps). Milestone 1 complete — auth/roles, employee & post
  office management, daily raw-data import, allowance entry, payroll
  detail views, Excel export, unmatched-mapping diagnostics.
- **Modules Thu Gom / Vận chuyển / Khai thác**: not started.
- **Known open item**: the service/price mapping tables
  (`ServiceMapping`, `RouteGroupMapping`, `PriceCard`) are intentionally
  empty — every "công theo sản lượng" figure reads as 0 until the
  Product Owner (or TCHC/TCKH) confirms the mapping and the tables are
  populated through Django admin. This is by design, not a bug.
- **No active ticket.** Awaiting Product Owner direction on what to work
  on next (e.g., populate mapping tables, PO UI acceptance pass on
  Milestone 1, or start a new module).

## Where to go next

- Product Owner: see `PROJECT_STATUS.md` (this file) for the gist, or
  `README.md` for how to actually run the app.
- AI session: start at `README_AI.md`, not this file.
