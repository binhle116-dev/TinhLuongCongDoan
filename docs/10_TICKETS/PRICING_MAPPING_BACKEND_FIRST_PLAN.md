# Pricing/Mapping Backend-First, UI-Second Plan (`PRICING-MAPPING-UI`)

Filename chosen instead of the prior project's `AUTO-BACKFILL-UI_PLAN.md`
— that name is specific to a different project's KPI-backfill feature
and would be meaningless here. This document illustrates the same
underlying principle (**backend built and proven correct before any
dedicated UI is built on top of it**) using this project's own real
example. See `docs/01_GOVERNANCE/PROJECT_DECISIONS.md` `DEC-008`
(proposed, pending Product Owner confirmation of this rename).

Status: **Phase A retrospective (COMPLETED, Milestone 1) + Phase B
proposal (NOT STARTED, awaiting PO approval)** — 2026-08-27.

> [!IMPORTANT]
> Phase B is a proposal only. No frontend work for a dedicated pricing
> configuration screen has been started or authorized.

---

## 1. Executive Summary

Module Phát's biggest open risk is the service/price mapping needed to
turn raw daily production data into money (see `PROJECT_CONTEXT.md`
Section 6). Rather than build a nice-looking configuration screen first
and let it quietly default ambiguous mappings to a guess, Milestone 1
applied the inverted order:

1. **Phase A (done)**: build the data model
   (`ServiceMapping`/`RouteGroupMapping`/`PriceCard`) and the pricing
   engine (`phat/services/pricing.py`) first, expose them through Django
   admin (functional, not polished), and build a diagnostic report
   (`/bao-cao/chua-anh-xa/`) that shows exactly which raw data isn't
   resolvable yet — instead of guessing.
2. **Phase B (proposed)**: only once real mapping data exists in the
   tables and a computed month's total has been checked against a known
   validated figure, consider building a friendlier "Cấu hình đơn giá"
   (pricing configuration) UI on top of the same backend.

This mirrors the reference project's own inverted-order lesson: a UI
built before the backend is trustworthy tends to either block on missing
APIs or quietly paper over ambiguity with a plausible-looking default —
exactly the mistake this project is trying to avoid with pricing.

---

## 2. Two-Phase Sequence

```
+---------------------------------------------------------------------+
| PHASE A: PRICING/MAPPING BACKEND (Milestone 1 — COMPLETED)          |
| Deliverables:                                                       |
|  - ServiceCategory / ServiceMapping / PriceGroup /                  |
|    RouteGroupMapping / PriceCard models                             |
|  - phat/services/pricing.py: match_service_category(),              |
|    compute_provisional_pay()                                        |
|  - Django-admin CRUD (+ django-import-export for bulk Excel edit)   |
|  - /bao-cao/chua-anh-xa/ unmatched-data diagnostic view             |
+---------------------------------------------------------------------+
                                  │
                                  ▼ Real mapping data entered AND
                                    a computed month verified against
                                    a known-correct total
+---------------------------------------------------------------------+
| PHASE B: PRICING CONFIGURATION UI (PROPOSED — NOT STARTED)          |
| Deliverables (if approved):                                         |
|  - Friendlier admin-facing screen for ServiceMapping/PriceCard/     |
|    RouteGroupMapping (Django admin remains usable in the meantime)  |
|  - Guided "resolve this unmatched combination" flow driven by the   |
|    unmatched report, instead of a blank form                        |
|  - No-code Vietnamese labels for mapping-resolution states (Section 4)|
+---------------------------------------------------------------------+
```

Phase B must not start before Phase A's backend has real, PO/TCHC-
confirmed mapping data — building a nicer form around empty or guessed
tables would not fix the actual open risk in `PROJECT_CONTEXT.md`
Section 6.

---

## 3. Proof Criteria Before Auto-Resolving a Raw Row

A raw `RawDailyProduction` row must never be silently priced from a
guess. It only counts as resolved when **all** of the following hold —
mirroring the reference project's "never auto-exempt without proof"
rule:

```
[ Raw row imported from SanLuongChiTiet ]
               │
               ▼
   Check resolution criteria:
   1. SERVICE_CODE + TYPE_CODE_PAYROLL + SERVICE_NAME_PAYROLL +      NO --+
      AREA_CODE + weight band match an active ServiceMapping rule?       |
   2. POSTMAN_CODE matches exactly one Employee.postman_code?        NO --+--> [ STAYS UNMATCHED ]
   3. That employee's ROUTE_PO_CODE resolves to exactly one            |    (never silently priced,
      PriceGroup via RouteGroupMapping?                              NO --+     surfaced in
   4. A PriceCard exists for (ServiceCategory, PriceGroup) with no      |     /bao-cao/chua-anh-xa/)
      ambiguous overlapping effective-date range?                    NO --+
               │
              YES (all 4 proven)
               │
               ▼
   [ RESOLVED: priced in the provisional monthly total ]
```

This is already how `phat/services/pricing.py` behaves today — this
section documents the rule explicitly so a future change doesn't
accidentally weaken it (e.g. by adding a fallback default price "just to
make the number non-zero").

## 4. Row Resolution States

Formalizing what the code already does implicitly, for clarity when this
becomes a UI:

| State | Technical Definition | Vietnamese Display | Action & Routing |
| --- | --- | --- | --- |
| `MAPPED` | Employee and service category both resolved | **Đã ánh xạ** | Included in provisional total. |
| `SERVICE_UNMATCHED` | Employee resolved, no `ServiceMapping` rule matched | **Chưa xác định dịch vụ** | Excluded from total. Listed in `/bao-cao/chua-anh-xa/` by (service_code, type_code_payroll, service_name_payroll, area_code). |
| `EMPLOYEE_UNMATCHED` | Service resolved, `POSTMAN_CODE` not found in `Employee` | **Chưa khớp nhân viên** | Excluded from total. Listed by `postman_code` — usually means the employee roster needs an entry. |
| `BOTH_UNMATCHED` | Neither resolved | **Chưa xác định cả hai** | Excluded from total. Appears in both lists above. |

`ImportBatch.unmatched_count` currently counts `SERVICE_UNMATCHED` +
`EMPLOYEE_UNMATCHED` + `BOTH_UNMATCHED` together; splitting it into these
four named states is a small, low-risk Phase B improvement (better
visibility), not a Phase A correctness change.

## 5. Exception Isolation Rules

- An unmatched row is a **valid, expected outcome** during Phase A — it
  must never abort the import batch or be treated as an error. Today's
  `import_sanluong_chitiet` already does this correctly (`bulk_create`
  proceeds regardless; unmatched rows are just counted).
- A genuinely corrupt/unreadable source file (missing required columns,
  unparseable `STATUS_DATE`) **is** a hard stop for that batch —
  `import_sanluong_chitiet` already raises `ValueError` for missing
  columns rather than silently importing partial garbage. This must stay
  distinct from "many rows unmatched," which is normal, not an error.
- Re-importing the same `production_date` must remain idempotent
  (already true: `ImportBatch.objects.filter(production_date=...).delete()`
  before re-inserting) — Phase B must not change this without a
  documented reason.

## 6. Future UI Mockup (Phase B, Not Built)

Illustrative only — not implemented, not authorized:

```
+---------------------------------------------------------------------+
|  CẤU HÌNH ĐƠN GIÁ CÔNG ĐOẠN PHÁT                                    |
|  Bộ lọc: [ Chỉ dòng chưa ánh xạ v ]  [ Tháng 08/2026 v ]            |
+---------------------------------------------------------------------+
|                                                                       |
|  Chưa xác định dịch vụ (12 tổ hợp, 3,204 dòng)                      |
|  +-------------------------------------------------------------+    |
|  | C-Báo Phát / LT / DV_T_KCOD  | 2 dòng  | [ Gán vào dịch vụ v]|    |
|  | Gói nhỏ thường / QT           | 1 dòng  | [ Gán vào dịch vụ v]|    |
|  | L-AppEpacket / QT             | 1 dòng  | [ Gán vào dịch vụ v]|    |
|  +-------------------------------------------------------------+    |
|                                                                       |
|  Chưa khớp nhân viên (48 mã bưu tá)                                 |
|  +-------------------------------------------------------------+    |
|  | 53A247  | Chưa có trong danh sách | [ Thêm nhân viên ]       |    |
|  +-------------------------------------------------------------+    |
|                                                                       |
+---------------------------------------------------------------------+
```

## 7. Verification Plan & Deliverables Checklist

### 7.1 Phase A Verification (already performed, Milestone 1)

- `phat/tests.py`: import idempotency, real-sample-file row count.
- Manual: computed provisional total for a synthetic mapping scenario
  matched hand-calculated expected value exactly (84 × 2,000 + 18 ×
  1,500 = 195,000₫).
- Manual: `/bao-cao/chua-anh-xa/` verified against real August 2026 data
  — correctly surfaced the same ambiguous cases already known from
  `PROJECT_CONTEXT.md` Section 6 (`C-Báo Phát`, `Gói nhỏ thường`,
  `L-AppEpacket`).

### 7.2 Phase B Deliverables Checklist (proposed, not started)

- [ ] Product Owner approval to start Phase B
- [ ] Real `ServiceMapping`/`RouteGroupMapping`/`PriceCard` data entered
      and confirmed by TCHC/TCKH
- [ ] A full month's provisional total cross-checked against a known
      validated figure before Phase B UI work begins
- [ ] `SERVICE_UNMATCHED`/`EMPLOYEE_UNMATCHED`/`BOTH_UNMATCHED` split
      implemented in the unmatched report
- [ ] Guided resolution UI built and PO-reviewed per
      `docs/01_GOVERNANCE/PO_UI_ACCEPTANCE_WORKFLOW.md`
