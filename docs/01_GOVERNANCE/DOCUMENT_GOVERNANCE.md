# DOCUMENT GOVERNANCE

Defines who may edit which document, and under what authority, in
**TinhLuongCongDoan**. This project has one AI role (Claude Code) and
one human role (Product Owner) — see `PROJECT_DECISIONS.md` `DEC-001`.

## 1. Edit Authority by Document

| Document | Claude Code may edit directly | Requires explicit Product Owner approval first |
| --- | --- | --- |
| `PROJECT_SNAPSHOT.md` | Yes — must be kept current as part of ticket handoff | — |
| `PROJECT_PROGRESS.md` | Yes, append-only (new line only) | Editing/deleting a prior line always requires PO approval and should essentially never happen |
| `PROJECT_STATUS.md` | Yes | — |
| `DOCUMENT_INDEX.md` | Yes, when documents are added/moved | — |
| `docs/10_TICKETS/*` (manifests) | Yes, to create/update a ticket's own manifest | — |
| `docs/06_REVIEWS/*` | Yes, to record technical findings/evidence | PO findings and their PASS/WARNING/FAIL classification are PO authority — Claude Code records what the PO said, not its own product verdict |
| `docs/06_REVIEWS/Shared/PO_FINDINGS_REGISTER.md` | Yes, to log a finding and update its status as work happens | The PO PASS/WARNING/FAIL verdict itself is PO authority |
| `PROJECT_DECISIONS.md` | Yes, to draft a new `DEC-0xx` entry | A new entry only becomes authoritative once the Product Owner has actually approved that decision (in chat or otherwise) — Claude Code should not invent a decision and mark it approved |
| `PROJECT_CONTEXT.md` | Yes, to keep technical/business background accurate | Business-rule content specifically should reflect what the Product Owner has actually said, not Claude Code's inference |
| `AI_COLLABORATION_PROTOCOL.md`, `DEVELOPE_PROMT_STANDARD.md`, `DEVELOPE_DOCUMENTATION_STANDARD.md`, `PO_UI_ACCEPTANCE_WORKFLOW.md`, this document, `DOCUMENT_UPDATE_MATRIX.md` | Only for typo/clarity fixes that don't change a rule | Yes — any change to an actual rule (roles, workflow, validation levels, PO gate definitions) needs explicit Product Owner sign-off, since these documents define the working relationship itself |
| `README_AI.md`, `CLAUDE.md` | Yes, to keep them synced with the documents above | Same as above when a referenced rule changes |
| `README.md` (human setup guide) | Yes | — |

## 2. Principle

Claude Code has broad authority to keep the *state-tracking* documents
(`PROJECT_SNAPSHOT.md`, `PROJECT_PROGRESS.md`, `PROJECT_STATUS.md`,
`DOCUMENT_INDEX.md`, ticket manifests, review evidence) accurate and
current — that is expected maintenance, not a scope expansion.

Claude Code has narrow authority over *rule-defining* documents (the
governance standards themselves): it may propose a change, but the
Product Owner must actually approve it before the new rule is treated as
binding. This mirrors `AI_COLLABORATION_PROTOCOL.md` Section 7 — the
protection is on architecture/business/workflow rules, not on routine
bookkeeping.

## 3. Renames

A rename proposed by Claude Code but not explicitly requested by the
Product Owner (e.g. `CODEX_DOCUMENTATION_STANDARD.md` →
`DEVELOPE_DOCUMENTATION_STANDARD.md`, see `PROJECT_SNAPSHOT.md`
Continuation Notes) must be flagged as a proposal, not silently treated
as final, until the Product Owner confirms it.
