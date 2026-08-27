# DEVELOPE DOCUMENTATION STANDARD

Filename renamed from the prior project's `CODEX_DOCUMENTATION_STANDARD.md`
for naming consistency with `DEVELOPE_PROMT_STANDARD.md`, since this
project has no "Codex" role at all (see `PROJECT_DECISIONS.md` `DEC-002`).
This rename was proposed by Claude Code and confirmed by the Product
Owner (`DEC-006`).

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Scope](#2-scope)
- [3. Reading Order](#3-reading-order)
- [4. Update Order](#4-update-order)
- [5. Stop Conditions](#5-stop-conditions)
- [6. SSOT Rule](#6-ssot-rule)
- [7. Commit and Report Standard](#7-commit-and-report-standard)

## 1. Purpose

This document standardizes how Claude Code must read, update, and stop
when working in **TinhLuongCongDoan**, so every session is deterministic
and safe by starting from:

`README_AI.md` → `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md` → current
manifest (if any).

## 2. Scope

Applies to every ticket in this project. Defines which documents Claude
Code reads first, which it may update, when it must stop and escalate,
and how it commits and reports changes. It does not change business
rules, frozen architecture, or PO approval rules.

## 3. Reading Order

1. `README_AI.md`
2. `docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md`
3. the current manifest referenced by `PROJECT_SNAPSHOT.md`, if `Current
   Ticket` is not `None`
4. only the Required Reading listed in that manifest

Do not search random documents first, expand reading scope without
instruction, skip the manifest, or infer missing state from memory.

## 4. Update Order

Update only documents explicitly allowed by the current ticket's scope
and `docs/01_GOVERNANCE/DOCUMENT_UPDATE_MATRIX.md`.

1. identify the exact ticket
2. read `PROJECT_SNAPSHOT.md`
3. read the current manifest, if any
4. read only required supporting documents
5. update only the allowed documents
6. validate consistency
7. commit one ticket in one commit (once Git is connected)
8. push only after validation passes (once authorized)

Do not update unrelated documents, even if they appear helpful.

## 5. Stop Conditions

Stop and escalate to the Product Owner when:

- a decision in `PROJECT_DECISIONS.md` conflicts with the ticket instructions
- frozen architecture or business rules would need to change
- the manifest and the ticket scope conflict
- a required document is missing or unreadable
- PO approval is required before proceeding
- the update would expand scope beyond the ticket

Do not continue by guessing when a stop condition is present. Also stop
and report the conflict when a ticket name does not match the Current
Ticket in `PROJECT_SNAPSHOT.md`.

## 6. SSOT Rule

One source of truth per responsibility:

- `PROJECT_SNAPSHOT.md` owns live project state
- the current manifest (if any) owns ticket reading scope
- review evidence (`docs/06_REVIEWS/`) owns ticket-specific validation proof
- `PO_FINDINGS_REGISTER.md` owns PO finding traceability
- `PROJECT_DECISIONS.md` owns frozen/authoritative decisions

Do not copy live status into multiple documents unless the workflow
explicitly requires it. An "Additional PO/User Decision" field may only
carry temporary execution clarification — never business rules, scope,
SSOT, or frozen-behavior changes.

## 7. Commit and Report Standard

Commits must follow: one ticket = one commit; commit message describes
the ticket outcome; commit scope matches the ticket scope; no unrelated
files staged.

Reports (recorded in the repository for continuity, not sent to another
AI role — see `DEVELOPE_PROMT_STANDARD.md` Section 14) should include:
files changed, business impact, validation result, documentation
updated, and commit hash / GitHub URLs once available.
