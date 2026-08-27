# PROJECT PROGRESS

Append-only ticket history. **Never edit or delete a prior line.** Add
exactly one new line whenever `Current Ticket` in
`docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` changes (a ticket closes or a
new one activates). This file has no other purpose — it is not a design
doc, not a snapshot, and not a place for discussion.

Format: `YYYY-MM-DD | TICKET_ID | outcome (one line)`

---

2026-08-27 | MILESTONE-1-PHAT-MVP | COMPLETED / TECHNICAL SELF-VERIFIED. Django `core`+`phat` apps built: RBAC scoped by post office (Admin/Phòng ban/Trưởng bưu cục), daily raw-data import (`SanLuongChiTiet_*.xlsx`) with idempotent re-import, admin-editable service/price mapping tables (left empty pending TCHC/TCKH confirmation), provisional piece-rate calculation, allowance entry, Excel export, unmatched-mapping report. 10/10 automated tests pass; manual browser walkthrough across 3 roles confirmed correct scoping (404 on cross-office access, 403 on admin-only page). No PO UI PASS recorded yet under this governance model (predates this document set).
2026-08-27 | PRICING-DATA-SEED | COMPLETED / TECHNICAL SELF-VERIFIED (DEC-009). Added `phat/management/commands/seed_pricing_data.py`: populates ServiceCategory (48) / PriceGroup (10) / PriceCard (480) from the real "Đơn giá XD 2026" price table, RouteGroupMapping (221) from the real "Tuyến" sheet (verified 117/117 exact match against real route codes — no code transformation needed), and ServiceMapping (47 rules) derived from real observed data combinations, resolving 98.6% of real rows (6611/6706). 9 known-ambiguous combinations deliberately left unmapped. Fixed a real bug found along the way: `slugify()` was silently colliding "<=2kg"/">2kg" category names into one code, overwriting price data — fixed by including column index in the generated code. Payroll totals still not end-to-end validated (0 employees loaded yet).
