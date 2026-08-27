# MASTER START PROMPT (Fallback Reference Only)

Do not use this as the default onboarding route. The default route is
`README_AI.md` → `DEVELOPE_PROMT_STANDARD.md` → `PROJECT_SNAPSHOT.md` →
Current Manifest → Required Reading (see `README_AI.md` Section 5/8).

Use this document only when:

- the current manifest explicitly requires it,
- an authority conflict exists between governance documents, or
- SSOT, frozen architecture, business rules, PO acceptance, or workflow
  interpretation itself is in question (i.e., the disagreement is about
  the rules, not about a specific ticket).

## Copy-paste fallback prompt

If a fresh AI session cannot resolve state through the normal chain
(e.g., `PROJECT_SNAPSHOT.md` is missing, corrupted, or contradicts
itself), paste this to re-establish a safe starting point:

```text
This is the TinhLuongCongDoan repository.

Read, in order:
1. README_AI.md
2. docs/01_GOVERNANCE/AI_COLLABORATION_PROTOCOL.md
3. docs/01_GOVERNANCE/DEVELOPE_PROMT_STANDARD.md
4. docs/01_GOVERNANCE/DEVELOPE_DOCUMENTATION_STANDARD.md
5. docs/01_GOVERNANCE/PROJECT_SNAPSHOT.md
6. docs/01_GOVERNANCE/PROJECT_CONTEXT.md
7. docs/01_GOVERNANCE/PROJECT_DECISIONS.md

Do not assume any prior chat history is accurate. If PROJECT_SNAPSHOT.md
conflicts with what you find in the actual repository (code, migrations,
tests), report the conflict instead of guessing which is correct, and
propose which one should be corrected.

Then report: current phase, current ticket (or "none"), and what you
believe the safe next action is — do not take any action yet.
```

## Why this exists

A single, explicit, copy-pasteable fallback avoids two failure modes: an
AI guessing project state from an unreliable source (stale memory,
partial chat scrollback), or a human having to reconstruct the full
onboarding chain from scratch during an actual conflict. It is
deliberately not the everyday path — `README_AI.md` is faster for normal
work and should be preferred whenever the repository is internally
consistent.
