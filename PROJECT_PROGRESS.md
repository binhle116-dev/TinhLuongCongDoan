# PROJECT PROGRESS

Append-only ticket history. **Never edit or delete a prior line.** Add
exactly one new line whenever `Current Ticket` in
`docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` changes (a ticket closes or a
new one activates). This file has no other purpose — it is not a design
doc, not a snapshot, and not a place for discussion.

Format: `YYYY-MM-DD | TICKET_ID | outcome (one line)`

---

2026-08-27 | MILESTONE-1-PHAT-MVP | COMPLETED / TECHNICAL SELF-VERIFIED. Django `core`+`phat` apps built: RBAC scoped by post office (Admin/Phòng ban/Trưởng bưu cục), daily raw-data import (`SanLuongChiTiet_*.xlsx`) with idempotent re-import, admin-editable service/price mapping tables (left empty pending TCHC/TCKH confirmation), provisional piece-rate calculation, allowance entry, Excel export, unmatched-mapping report. 10/10 automated tests pass; manual browser walkthrough across 3 roles confirmed correct scoping (404 on cross-office access, 403 on admin-only page). No PO UI PASS recorded yet under this governance model (predates this document set).
