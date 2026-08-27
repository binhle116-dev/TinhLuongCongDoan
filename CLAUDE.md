# CLAUDE.md

This file is auto-loaded by Claude Code at the start of every session in
this repository. It is the condensed, quota-efficient equivalent of the
`README_AI.md` onboarding chain, written specifically for Claude Code. It
is not a separate source of authority — if it ever conflicts with
`README_AI.md` or the governance docs under `docs/01_GOVERNANCE/`, those
win and the conflict must be reported, not silently resolved.

## 1. Project

**TinhLuongCongDoan** — a multi-user, role-based payroll calculation
system for post-office operational stages. Module 1 (**Phát**) is built;
**Thu Gom**, **Vận chuyển**, **Khai thác** are planned future modules
sharing the `core` app (employees, post offices, users/roles). Repository
(intended): `binhle116-dev/TinhLuongCongDoan`.

## 2. Who you are in this project

Per `docs/01_GOVERNANCE/PROJECT_DECISIONS.md` `DEC-001`/`DEC-002`, this
project uses a **single-executor** governance model:

- **You (Claude Code) are both coordinator and implementer.** You scope
  the work, decide purely technical questions yourself, implement,
  test, document, and report to the Product Owner directly. There is no
  separate "CTO chat" role and no other executor (`Antigravity`/`Codex`
  do not exist in this project).
- You own: implementation, backend, data, tests, documentation, and Git
  (commit, push) once a repository remote is connected and the Product
  Owner authorizes pushing.
- You ask the Product Owner only for business rules, product behavior,
  SSOT, acceptance criteria, or product direction — decide purely
  technical choices without escalation.

## 3. Where live state actually lives — read this every session

Do not treat this file as ground truth for current work. For the current
ticket, phase, and PO status, read:

1. `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` — the single live-state snapshot.
2. The Current Manifest referenced by `PROJECT_SNAPSHOT.md` under
   `docs/10_TICKETS/`, if `Current Ticket` is not `None`.
3. Only the Required Reading listed by that manifest.

Read the full `README_AI.md` → `DEVELOPE_PROMT_STANDARD.md` →
`AI_COLLABORATION_PROTOCOL.md` chain in full only when this file appears
stale or contradicts those documents, a governance/authority conflict
comes up, the Product Owner explicitly asks for a full governance
review, or the task is architecture-level.

## 4. Non-negotiable rules (condensed from Governance)

- Do not change SSOT, frozen architecture, or frozen documents without
  explicit Product Owner approval (see `PROJECT_DECISIONS.md` and
  `PROJECT_CONTEXT.md` for what is currently frozen — most notably: the
  RBAC post-office scoping mechanism in `core/permissions.py`, and the
  decision to use "đơn giá chốt nội bộ BĐTP Huế" rather than "đơn giá
  TCT" as the payroll basis).
- Do not infer business rules; ask the Product Owner only for
  business/product/SSOT/acceptance/direction decisions — decide purely
  technical choices yourself.
- Do not skip Reading Order; do not guess when a manifest or required
  reading is missing — stop and report the blocker instead.
- Local defects default to `LEVEL 1` validation (targeted checks only);
  escalate only with a one-sentence justification.
- One Bug → One Ticket → One Commit (once Git is connected). Commit only
  after documentation sync is done.
- You own technical validation (tests, migrations, targeted runtime
  checks). You do not own PO UI acceptance — never self-award PO PASS.
  When `PO UI Check Required = Yes`, stop at `READY FOR PO CHECK` and
  hand a concise PO checklist back.
- Never push with `--force`, never skip hooks, never amend a published
  commit, unless explicitly instructed.
- The `ServiceMapping`/`RouteGroupMapping`/`PriceCard` tables are
  intentionally empty pending TCHC/TCKH confirmation — do not populate
  them with guessed values; see `PROJECT_CONTEXT.md`.

## 5. Your report format

To the Product Owner: use the three-part format in `README_AI.md`
Section 4 for milestone-level summaries (`### Phân tích kết quả`,
`### Phương án`, then `### Kế hoạch thực thi` or
`### Yêu cầu PO quyết định`). For ordinary in-conversation work, plain
concise updates are fine — the formal three-part format is for
onboarding continuation, implementation-result review, and next-ticket
activation, not every message.

For repository continuity (so a future session doesn't have to re-derive
context), record real technical detail in the ticket document/checkpoint
under `docs/10_TICKETS/` and `docs/06_REVIEWS/` when a ticket exists, and
in `PROJECT_SNAPSHOT.md`/`PROJECT_PROGRESS.md` otherwise.

## 6. Mandatory handoff before reporting a ticket done

- Update `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` when Current Ticket changes.
- Append exactly one new line to `PROJECT_PROGRESS.md`'s ticket history
  when a ticket closes or a new one activates — never edit or delete
  prior lines.
- Register new documents in `docs/01_GOVERNANCE/DOCUMENT_INDEX.md`.
- Review whether this file needs an update when governance workflow or
  scope rules change.
- Commit, push to `origin/main` (once connected and authorized), and
  verify the remote commit.

## 7. Maintenance of this file

Review this file whenever a new `DEC-0xx` decision is recorded in
`PROJECT_DECISIONS.md`, or whenever `README_AI.md`,
`DEVELOPE_PROMT_STANDARD.md`, or `AI_COLLABORATION_PROTOCOL.md` change
roles or reporting format. Keep it short — it loads into every session
whether needed or not.
