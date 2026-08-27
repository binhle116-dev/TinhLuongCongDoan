# DOCUMENT UPDATE MATRIX

Which documents a ticket must touch, by ticket type. This is a checklist
aid for `AI_COLLABORATION_PROTOCOL.md` Section 13.5 (Documentation
Synchronization) — it does not replace reading that section.

| Ticket type | Always update | Update if applicable |
| --- | --- | --- |
| Any ticket that closes or activates | `PROJECT_SNAPSHOT.md`, `PROJECT_PROGRESS.md` (append one line) | `PROJECT_STATUS.md` if the human-readable summary changed |
| New feature / bug fix (code change) | `PROJECT_SNAPSHOT.md` | Ticket manifest under `docs/10_TICKETS/` if one exists for it; `docs/06_REVIEWS/` evidence if a defect was found and fixed |
| Change with a visible UI/product effect | Everything above | `docs/01_GOVERNANCE/PO_UI_ACCEPTANCE_WORKFLOW.md` gate applies — the ticket must state `PO UI Check Required` and follow through; `PO_FINDINGS_REGISTER.md` if a PO finding is being closed |
| Change to a frozen/architectural decision | Everything above, plus | `PROJECT_DECISIONS.md` (new `DEC-0xx` entry, PO-approved), `AI_COLLABORATION_PROTOCOL.md` Section 7 if the protected-items list itself changes |
| New document added or moved | `DOCUMENT_INDEX.md` | `DOCUMENT_GOVERNANCE.md` if its edit-authority differs from the default pattern |
| Change to governance workflow, roles, or model rules | `README_AI.md`, `CLAUDE.md`, `AI_COLLABORATION_PROTOCOL.md`, `DEVELOPE_PROMT_STANDARD.md` (whichever actually changed) | `PROJECT_DECISIONS.md` new entry recording why |
| New module started (e.g. Thu Gom) | `PROJECT_CONTEXT.md` (business/technical background), `PROJECT_SNAPSHOT.md` | `AI_COLLABORATION_PROTOCOL.md` Section 4 (module delivery order) if the pattern needs adjusting for that module |
| Documentation-only change | `DOCUMENT_INDEX.md` if a file moved | Nothing else if content-only |

If a ticket doesn't cleanly fit a row above, use the closest one and note
the deviation in the ticket's own record — do not skip documentation
synchronization because the ticket type wasn't listed.
