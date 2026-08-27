# DOCUMENT INDEX

Authoritative list of every governance/AI-collaboration document in this
repository. Register a new document here when it is added or moved (see
`AI_COLLABORATION_PROTOCOL.md` Section 13.5).

## Repository root

| Document | Purpose |
| --- | --- |
| `README.md` | Human-facing setup/run guide for the Django app (pre-existing, not part of the AI governance chain). |
| `README_AI.md` | Mandatory AI entry point and onboarding chain. |
| `CLAUDE.md` | Condensed onboarding auto-loaded by Claude Code every session. |
| `PROJECT_PROGRESS.md` | Append-only, one-line-per-ticket history. Never edited retroactively. |
| `PROJECT_STATUS.md` | Very short human-readable status summary. |

## `docs/01_GOVERNANCE/`

| Document | Purpose |
| --- | --- |
| `AI_COLLABORATION_PROTOCOL.md` | Full workflow: roles, ticket rules, architecture protection, handover, golden rules. |
| `DEVELOPE_PROMT_STANDARD.md` | Lean execution/ticket standard (renamed from `CODEX_PROMPT_STANDARD.md`). |
| `DEVELOPE_DOCUMENTATION_STANDARD.md` | Reading/update/stop-condition discipline (renamed from `CODEX_DOCUMENTATION_STANDARD.md`, confirmed `DEC-006`). |
| `PO_UI_ACCEPTANCE_WORKFLOW.md` | Technical PASS → PO PASS separation and process. |
| `PROJECT_SNAPSHOT.md` | Single live-state snapshot table + continuation notes. |
| `MASTER_START_PROMPT.md` | Fallback-only onboarding prompt for conflict/recovery situations. |
| `DOCUMENT_INDEX.md` | This file. |
| `DOCUMENT_GOVERNANCE.md` | Who may edit which document, and under what authority. |
| `DOCUMENT_UPDATE_MATRIX.md` | Which documents a given ticket type must touch. |
| `PROJECT_CONTEXT.md` | Business and technical background of TinhLuongCongDoan. |
| `PROJECT_DECISIONS.md` | Numbered, frozen decision log (`DEC-001`, `DEC-002`, ...). |

## `docs/06_REVIEWS/Shared/`

| Document | Purpose |
| --- | --- |
| `PO_REVIEW_TEMPLATE.md` | Template the Product Owner (or Claude Code preparing a handoff) fills in for a PO UI review. |
| `PO_FINDINGS_REGISTER.md` | Running register of PO findings and their resolution status. |

## `docs/10_TICKETS/`

| Document | Purpose |
| --- | --- |
| `README.md` | Explains what belongs in this folder and when a ticket needs its own manifest file. |

## Not yet created

| Document | Status |
| --- | --- |
| `AUTO-BACKFILL-UI_PLAN.md` | Requested by the Product Owner as an example of the "backend-first, UI-second" principle, but its source content/link was not provided and its filename is tied to a specific ticket from the prior project. Needs either the source link or a new name/purpose confirmed by the Product Owner before authoring. |

## Maintenance rule

If a document is renamed, moved, or deleted, update this table in the
same change — this index must always match the actual repository
contents exactly (see `DEVELOPE_PROMT_STANDARD.md` verification
expectations).
