# PROJECT CONTEXT

Business and technical background for **TinhLuongCongDoan**. Read this
when a decision needs background that `PROJECT_SNAPSHOT.md` (live state)
and `PROJECT_DECISIONS.md` (frozen decisions) don't carry on their own.

## Table of Contents

- [1. Business Purpose](#1-business-purpose)
- [2. Organizational Roles](#2-organizational-roles)
- [3. The Four Modules](#3-the-four-modules)
- [4. Module Phát — Domain Detail](#4-module-phát--domain-detail)
- [5. Data Sources](#5-data-sources)
- [6. The Pricing Ambiguity (Important, Unresolved)](#6-the-pricing-ambiguity-important-unresolved)
- [7. Technical Architecture](#7-technical-architecture)
- [8. What Is Deliberately Not Automated](#8-what-is-deliberately-not-automated)

## 1. Business Purpose

The Product Owner works at Trung tâm Vận hành, Bưu điện Thành phố Huế
(BĐTP Huế). This system exists to **officially finalize** ("chốt")
monthly payroll for employees across the post office's operational
stages — not just display data. It replaces manual, per-office Excel
workbooks and ad hoc file exchange with a proper multi-user application.

## 2. Organizational Roles

- **Admin** (the Product Owner) — full control: employee/post-office
  master data, pricing/mapping configuration, monthly finalization.
- **Phòng ban** (departments, e.g. TCHC/TCKH — finance/HR) — read
  access, and ultimately the authority that must confirm the pricing
  mapping (Section 6).
- **Trưởng bưu cục** (post office head) — one account per post office
  (~50+ offices), scoped strictly to their own office's employees and
  data. Enters manual allowances, reviews/confirms production figures
  for their own staff, manages their own office's employee roster.

This maps directly to `core.models.UserProfile.role` and the RBAC
scoping mechanism in `core/permissions.py` (`ADMIN`, `PHONG_BAN`,
`TRUONG_BUU_CUC`).

## 3. The Four Modules

The end goal is one system covering four operational stages, each with
its own pay calculation:

1. **Phát** (delivery) — built, Milestone 1 complete.
2. **Thu Gom** (collection) — planned, not started.
3. **Vận chuyển** (transport) — planned, not started.
4. **Khai thác** (sorting/processing) — planned, not started.

All four share the `core` app: `PostOffice`, `Employee`, `UserProfile`,
and the RBAC scoping mechanism. Each module gets its own Django app
(`phat`, and eventually `thu_gom`, `van_chuyen`, `khai_thac`) with its
own models/services/views following the same layering pattern (see
`AI_COLLABORATION_PROTOCOL.md` Section 8).

## 4. Module Phát — Domain Detail

Pay for a bưu tá (postman) in the Phát module has two components:

1. **Piece-rate by production volume** — priced per delivered item,
   depending on which of ~49 named service categories the item falls
   into (see `phat.models.ServiceCategory`) and which price group (1-12,
   `phat.models.PriceGroup`) the employee's delivery route belongs to.
2. **Fixed/manual allowances** — small monthly amounts per employee for
   specific situations: "Lương cố định tuyến phát đặc biệt khó khăn"
   (hardship route, per tờ trình 3107/QĐ-BĐHUE), "Trực đêm giao nhận túi
   gói" (night-shift bag handling, default 4,000,000₫/month), "Hỗ trợ
   nhận hàng sân bay" (airport pickup, variable rate/tháng), "Hỗ trợ
   phát ngoài giờ HC" (overtime delivery, variable rate/tháng). These are
   entered by the Trưởng bưu cục via `phat.models.AllowanceEntry`.

**Important, already-discovered bug class**: a "Trợ cấp tuyến trại giam
Bình Điền" allowance existed in an earlier prototype and was found to
already be included inside the source file's own "Tổng công phát" total
— adding it again from a manual template double-counted it. It was
removed entirely (see `PROJECT_DECISIONS.md` for the general principle:
never add an allowance on top of a total without first confirming the
total doesn't already include it).

## 5. Data Sources

Several real files/feeds exist; not all are currently wired into the app:

- **`SanLuongChiTiet_DDMMYYYY.xlsx`** — daily raw transaction export
  (one row per scanned parcel: `LADING_CODE`, `POSTMAN_CODE`,
  `ROUTE_PO_CODE`, `SERVICE_CODE`, `TYPE_CODE_PAYROLL`,
  `SERVICE_NAME_PAYROLL`, `AREA_CODE`, `KG`, `QUANTITY`,
  `STATUS_DATE`...). Pulled from an internal SFTP server
  (`10.1.45.10:22`, SFTPGo, folder `/SLP Chitiet`) via a WinSCP script
  (`scripts/pull_and_import_daily.bat` + `pull_sanluong_chitiet.txt`,
  saved site name `CAS_Hue_SFTP`). This is what `phat.services.importer`
  loads into `RawDailyProduction`.
- **`CÔNG PHÁT THÁNG MM.yyyy - ttvh.xlsx`** — the monthly master
  workbook someone in the operations center builds by hand/formula each
  month. Contains a `CÁ NHÂN T{mm}.{yy}` sheet with the final
  per-employee "Tổng công phát" figure (both an official Tổng-công-ty
  price basis and an internally-adjusted "chốt nội bộ BĐTP Huế" basis —
  see Section 6), an `LĐ` sheet (employee roster with `Loại hợp đồng`),
  and several dedicated allowance sheets ("Lương cố định tuyến phát",
  "HỖ TRỢ PHÁT NGOÀI GIỜ HC", "BẢNG THANH TOÁN SÂN BAY", "TRỰC ĐÊM GIAO
  NHẬN TGÓI - PLOC"). An earlier prototype (since deleted, see
  `PROJECT_SNAPSHOT.md` Continuation Notes) read this file directly and
  validated against it — the Django app's `ServiceMapping`/
  `RouteGroupMapping`/`PriceCard` tables are meant to eventually
  reproduce the "chốt nội bộ" figure from raw daily data instead, but
  are currently empty (Section 6).
- **A possible separate "Thống kê sản lượng phát" report** — a
  standard statistics export from the postal operations system (BCCP),
  grouped by employee/route/weight-band with an official "Tên chỉ tiêu"
  service name. A stale copy (dated Feb 2026) was found inside the July
  master workbook under a sheet named "CÔNG PHÁT DGDK". This may be the
  *actual* correct input for pricing rather than `SanLuongChiTiet`
  (which is more granular/raw) — **not confirmed**, needs TCHC/TCKH or
  whoever maintains the master workbook to clarify.

## 6. The Pricing Ambiguity (Important, Unresolved)

This is the single biggest open risk in Module Phát and the reason
`ServiceMapping`/`RouteGroupMapping`/`PriceCard` are deliberately empty.

The monthly master workbook computes **two different totals** for the
same month:

- **"Đơn giá TCT"** — the official Tổng công ty (headquarters) price per
  VB 1085/BĐVN-TCNS (and VB 2468 for DHL). Fully deterministic from raw
  data + a service-code mapping table, no monthly calibration needed.
- **"Đơn giá chốt nội bộ BĐTP Huế"** — the price the local unit actually
  pays, derived by applying several rounds of manual "điều chỉnh"
  (adjustment) to reconcile with a budget figure handed down externally
  each month/quarter. This adjustment ratio is **not present in the raw
  data** and cannot be derived by formula — it is an operational decision
  made by BĐTP Huế/TCHC each period.

These two totals do not match (observed ~18-38 triệu đồng/month
difference across BĐTP Huế in a sampled month). The source workbook
itself already carries a note recommending reconciliation with
Phòng TCHC/TCKH before official payment — this is a known, acknowledged
discrepancy, not something this project introduced.

**Decision** (`DEC-004`): the Product Owner chose to keep using "đơn giá
chốt nội bộ BĐTP Huế" as the app's pricing basis (matching what earlier
prototypes already validated against real July 2026 figures:
781,188,261đ piece-rate total, independently verified line-by-line for
at least one employee). This decision stands for Module Phát going
forward unless TCHC/TCKH direct otherwise.

**What is still missing** to compute that basis automatically from raw
`SanLuongChiTiet` data:

1. The mapping from (`SERVICE_CODE`, `TYPE_CODE_PAYROLL`,
   `SERVICE_NAME_PAYROLL`, `AREA_CODE`, weight band) to one of the ~49
   named service categories (`Đơn giá XD 2026` table's columns). Several
   specific cases are genuinely ambiguous from the data alone: `C-Báo
   Phát`, `Gói nhỏ thường` (quốc tế), `L-AppEpacket`, and rows with
   `AREA_CODE` = `R` or `M`. The `/bao-cao/chua-anh-xa/` view in the app
   surfaces exactly which combinations appear in real imported data, to
   ground this conversation in facts rather than guesses.
2. The mapping from `ROUTE_PO_CODE` to price group (1-12) — route codes
   observed in raw data have inconsistent lengths (7-9 digits) and don't
   trivially match the `Tuyến` reference sheet's `mã tuyến` format;
   this needs the actual translation rule, not an assumed truncation.
3. The monthly calibration ratio itself (or confirmation that it is no
   longer needed because "Đơn giá XD 2026" is now a fixed, already-
   settled price table for the year rather than something recalculated
   fresh every month — this is plausible but unconfirmed).

**Update 2026-08-27 (`DEC-009`)**: the Product Owner directed populating
these tables from available real data rather than continuing to wait —
`phat/management/commands/seed_pricing_data.py` now does this,
idempotently, from the July master workbook's "Đơn giá XD 2026" sheet
(price table) and "Tuyến" sheet (route→group, **verified 117/117 exact
string match** against real `ROUTE_PO_CODE` values — no code
transformation needed, contrary to earlier concern about differing
digit lengths). `ServiceMapping` rules were derived from the actual
`SERVICE_NAME_PAYROLL`/`TYPE_CODE_PAYROLL`/`AREA_CODE`/weight
combinations observed in real imported data (not guessed): items 1-2
above are resolved this way for **98.6%** of real rows (6611/6706 in
the 2026-08-26 sample). The 9 previously-flagged ambiguous combinations
(`C-Báo Phát`, `Gói nhỏ thường`, the `KT1 ...- B`/`...- C`/`KT1 B`/`KT1
C` lettered variants, `KT1 Hỏa tốc Hẹn giờ`) remain deliberately
unmapped — they still show up in `/bao-cao/chua-anh-xa/` rather than
being guessed. Item 3 (the monthly calibration ratio / whether "Đơn giá
XD 2026" is a fixed year-long table) is **still unconfirmed** — this
population trusts that table as-is, which is a reasonable read given its
"XD 2026" (built for 2026) naming, but has not been independently
re-verified against a known full-month total (no complete month of daily
`SanLuongChiTiet` files exists yet, and no `Employee.postman_code` data
is loaded yet to compute a real payroll total end-to-end). Treat computed
totals as provisional until that validation happens.

A one-time gotcha worth knowing if this seed script is ever rewritten:
the "Đơn giá XD 2026" sheet contains the same price table duplicated
twice plus a third, differently-shaped "Đơn giá 2025"/"90%" reference
table further down in the same sheet — naive row-scanning must filter
for rows whose first cell starts with "NHÓM", not just "first cell is
non-empty". Also, `django.utils.text.slugify()` strips `<=`/`>` symbols
entirely, so naively slugifying category names like "EMS nội tỉnh
<=2kg" and "EMS nội tỉnh >2kg" collide into the same code — the seed
script works around this by including the source column index in the
generated `ServiceCategory.code`.

## 7. Technical Architecture

- **Stack**: Django 6.1 + SQLite (WAL mode, `core/apps.py`
  `connection_created` signal) + waitress (`serve.py`) — chosen for a
  non-professional-developer Admin operating on Windows, internal
  LAN/VPN only, modest concurrent load (see `PROJECT_DECISIONS.md`
  `DEC-003`).
- **Apps**: `core` (shared: `PostOffice`, `Employee`, `UserProfile`,
  `permissions.py` RBAC scoping, `textutils.py`), `phat` (module-specific
  models/services/views/templates).
- **RBAC mechanism**: `core.permissions.scope_queryset(queryset, user,
  field_name)` is the single, centralized place every view/query
  touching post-office-scoped data must go through. Verified by
  automated tests (`core/tests.py`, `phat/tests.py`) and a manual
  browser walkthrough (404 on cross-office access, 403 on admin-only
  pages).
- **Pipeline**: `phat.management.commands.import_daily_production` →
  `phat.services.importer.import_sanluong_chitiet` (idempotent by
  `production_date`) → `phat.services.pricing` (mapping resolution +
  provisional pay calculation, `EmployeeMonthlyPay`/
  `EmployeeMonthlyPayDetail` snapshots per `MonthlyPayrollRun`).
- **Immutability rule**: once a `MonthlyPayrollRun.status = FINALIZED`,
  its `EmployeeMonthlyPay` snapshot must not be silently recomputed by a
  later mapping-table edit — only draft/provisional months recompute
  live.

## 8. What Is Deliberately Not Automated

- **Trực đêm giao nhận túi gói** allowance stays manual-entry only — its
  source spreadsheet has a multi-section layout with blank spacer rows
  and pre-existing `#VALUE!` formula errors, too unreliable to parse
  automatically with confidence.
- **Git repository connection** (`git init`, remote add, first push to
  `binhle116-dev/TinhLuongCongDoan`) has not been performed — this is an
  explicit action requiring Product Owner authorization before it
  happens, not an oversight.
- **Windows Scheduled Tasks** for the daily pull/import and nightly
  backup are documented (`README.md`) with exact commands but have not
  actually been created on the Product Owner's machine — creating a
  scheduled task is a system-configuration change the Product Owner
  should run themselves (or explicitly ask Claude Code to run, per the
  safety rules around modifying system settings).
