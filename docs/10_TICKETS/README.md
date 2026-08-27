# docs/10_TICKETS/

This folder holds **ticket manifests** — durable scope documents for
work large enough to outlive one conversation.

## When a ticket needs a manifest here

Most day-to-day work in this project does **not** need one:
`docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` plus the conversation is enough
for a small, bounded ticket (see
`docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md` Section 6).

Create a manifest here when a ticket is:

- large enough to span multiple sessions,
- a new module (Thu Gom, Vận chuyển, Khai thác), or
- something the Product Owner explicitly wants a durable written scope
  for before work starts.

## Manifest naming

`<TICKET-ID>_MANIFEST.md`, e.g. `THU-GOM-MODULE-001_MANIFEST.md`.

## Minimum manifest contents

- Ticket ID and one-line objective
- In Scope / Out of Scope
- Required Reading (specific files, not "read everything")
- Validation requirements
- `PO UI Check Required: Yes/No` and why
- Next ticket / follow-up, once known

Once a ticket closes, its manifest stays in this folder as a historical
record (do not delete it) — update its status field to `CLOSED` and
update `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` plus
`PROJECT_PROGRESS.md` per the standard handoff.

This folder is currently empty — no ticket has needed a dedicated
manifest yet (see `PROJECT_SNAPSHOT.md`: `Current Ticket = None`).
