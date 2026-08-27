# PO UI Acceptance Workflow

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Applicability Decision](#2-applicability-decision)
- [3. Workflow](#3-workflow)
- [4. PO UI Acceptance Notice](#4-po-ui-acceptance-notice)
- [5. PO Result Definitions](#5-po-result-definitions)
- [6. Module Completion Rules](#6-module-completion-rules)
- [7. PO Findings Traceability](#7-po-findings-traceability)
- [8. Blocking Rules](#8-blocking-rules)
- [9. Authority](#9-authority)

## 1. Purpose

This document defines the mandatory Product Owner UI acceptance workflow
for **TinhLuongCongDoan** tickets that produce visible, independently
checkable product changes. It exists to separate: Technical PASS,
Runtime PASS, PO Product Review PASS, and Module Completed.

## 2. Applicability Decision

Every ticket must explicitly state `PO UI Check Required: Yes` or `No`,
with a concise reason.

Set `Yes` when the ticket affects any visible UI, navigation, screen,
table, filter, workflow, label, report, or other user-facing behavior
(e.g., anything in `phat/templates/`, `phat/views.py` response content).

Set `No` only when the ticket is purely internal (e.g., a management
command, a migration with no visible effect, an internal refactor).

## 3. Workflow

### 3.1 When PO UI Check Required = Yes

Technical PASS → Runtime PASS (manual check) → Ready for PO Check →
Product Owner manual review → PO PASS / WARNING / FAIL → Documentation
Synchronization → Module Completed or Recovery.

### 3.2 When PO UI Check Required = No

Technical PASS → Runtime PASS or Runtime Not Required → PO UI Check
Required: No → Documentation Synchronization → Module Completed.

## 4. PO UI Acceptance Notice

When `PO UI Check Required = Yes`, Claude Code must include a clearly
visible section titled `PO UI ACCEPTANCE REQUIRED`, including:

- PO Check Status
- Affected Screen / Route (e.g., `/luong/<year>/<month>/`)
- Required Test Context (e.g., which role to log in as)
- What Changed
- Expected Result
- PO Check Steps
- PO Acceptance Checklist
- Known Warnings
- Blocking Rule

Claude Code prepares the implementation and technical evidence but does
not replace PO review, and must not self-award PO PASS. If PO
observations conflict with Claude Code's own visual assessment, PO
observations override.

## 5. PO Result Definitions

**PO PASS** — the visible output is correct, context is correct,
navigation works, no blocking product defect remains.

**PO WARNING** — core behavior works but a non-blocking issue remains,
linked to a responsible fix ticket.

**PO FAIL** — the UI, data, workflow, or business result does not meet
the expected product outcome. Blocks module completion until fixed.

## 6. Module Completion Rules

A module cannot be marked `Module Completed` unless Technical PASS is
achieved, Runtime PASS is achieved where applicable, and PO PASS is
achieved when `PO UI Check Required = Yes`. Module completion must not
be implied by tests passing alone.

## 7. PO Findings Traceability

Every PO finding recorded in `docs/06_REVIEWS/Shared/PO_FINDINGS_REGISTER.md`
must be traceable to: affected screen/route, related ticket,
classification, responsible fix ticket, blocking status, PO recheck
point, and final PO result.

## 8. Blocking Rules

- A PO FAIL blocks module completion.
- A PO WARNING does not block progress if it is linked to a responsible ticket.
- A finding cannot be closed by test PASS alone.
- A finding cannot be closed without PO recheck evidence when PO review applies.
- The next ticket should not be activated before current-ticket PO PASS
  unless the Product Owner explicitly permits parallel work.

### 8.1 PO Decision Boundary

Request a Product Owner decision only when a finding requires a
business-rule, SSOT, frozen-behavior, scope, threshold, acceptance, or
authority decision. A failed repository search alone does not prove
missing authority — check `PROJECT_DECISIONS.md`, `PROJECT_CONTEXT.md`,
code, tests, and Git history first.

## 9. Authority

Product Owner has final authority over PO PASS, PO WARNING, and PO FAIL.
Claude Code may classify and recommend but cannot override Product Owner
product acceptance. Claude Code must report the PO gate status
explicitly and must not collapse technical acceptance into product
acceptance.
