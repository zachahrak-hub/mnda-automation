---
name: mnda-triage
description: >
  This skill should be used when the user receives an NDA and needs a quick
  first-pass classification before a full review — phrases like "just received
  an NDA from X", "quick look at this NDA", "should I worry about this NDA",
  "is this a standard NDA", "NDA came in from a vendor", or "sales got an NDA".
  Also use when the user pastes NDA text and wants a fast risk signal before
  deciding whether to invest time in a detailed review.
version: 1.0.0
---

# MNDA Triage Skill

Rapidly classify an incoming NDA as GREEN, YELLOW, or RED based on a targeted fast-scan of the highest-risk clauses. Output a one-page triage card with a clear recommendation and confidence level.

## Triage vs Full Review

Triage is a **30-second scan** — not a full clause-by-clause review. Its purpose is to answer: "Can I approve this quickly, or does it need attention?"

- If triage returns GREEN → proceed to signature workflow (or run full review to confirm)
- If triage returns YELLOW → run full review (`mnda-review` skill) before deciding
- If triage returns RED → escalate to legal counsel immediately; do not run full review first

## Fast-Scan Checklist

Check only these five signals (in order). Stop and flag RED as soon as one RED signal is found.

| # | Signal | Check | RED trigger |
|---|--------|-------|-------------|
| 1 | Known standard | Mentions "bonterms" or "common paper" | — (GREEN fast-path) |
| 2 | Mutual structure | Both parties have obligations | "Receiving Party only", "one-way", no mutual language |
| 3 | Exceptions present | Four standard carve-outs exist | All four missing |
| 4 | Perpetual obligations | No "perpetual" or "indefinite" term | "perpetual", "indefinitely", no survival period |
| 5 | No-solicitation | Absence of non-solicit clause | Non-solicit clause present |

## Triage Output Format

```
## NDA Triage — [Counterparty / Source]

**Classification:** GREEN / YELLOW / RED
**Confidence:** High / Medium / Low
**Known Standard:** [Name if detected, otherwise —]

### Signals Checked
| Signal | Finding |
|--------|---------|
| Known standard | [Result] |
| Mutual structure | [Result] |
| Exceptions | [Result] |
| No perpetual obligations | [Result] |
| No-solicitation | [Result] |

### Recommendation
[One sentence: approve / run full review / escalate]

### Why
[2-3 sentences max explaining the key finding]
```

## After Triage

Always offer the user one of these next steps based on the result:
- GREEN → "Run a full review to confirm?" or "Proceed to signature?"
- YELLOW → "Run a full review to identify specific issues?"
- RED → "I'll escalate this — do you want me to draft a message to legal?"
