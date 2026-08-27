# PO Review Template

Copy this into a new file under `docs/06_REVIEWS/<Module>/` (or `Shared/`
for cross-module reviews) when a ticket reaches `READY FOR PO CHECK`
under `docs/01_GOVERNANCE/PO_UI_ACCEPTANCE_WORKFLOW.md`.

---

## PO UI ACCEPTANCE REQUIRED

**Ticket:** `<ticket id/name>`
**Date:** `YYYY-MM-DD`
**PO Check Status:** `READY FOR PO CHECK`

### Affected Screen / Route

`<e.g. /luong/2026/9/>`

### Required Test Context

`<e.g. log in as a Trưởng bưu cục account for post office 533140>`

### What Changed

`<plain-language description, no code paths>`

### Expected Result

`<what the Product Owner should see/be able to do>`

### PO Check Steps

1. `...`
2. `...`
3. `...`

### PO Acceptance Checklist

- [ ] Visible output is correct
- [ ] Context/filters behave as expected
- [ ] Navigation works
- [ ] No blocking defect observed

### Known Warnings

`<non-blocking issues already known, with their responsible fix ticket, or "None">`

### Blocking Rule

A `PO FAIL` here blocks marking this ticket/module complete until the
issue is fixed and rechecked. A `PO WARNING` does not block, provided it
is linked to a responsible ticket.

### PO Response Required

Reply with one of:

- `PO PASS`
- `PO WARNING — <non-blocking issue> (tracked in <ticket>)`
- `PO FAIL — <what's wrong>`

---

Once the Product Owner responds, record the result in
`docs/06_REVIEWS/Shared/PO_FINDINGS_REGISTER.md` if it's a `WARNING` or
`FAIL`, and update `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` /
`PROJECT_PROGRESS.md` accordingly.
