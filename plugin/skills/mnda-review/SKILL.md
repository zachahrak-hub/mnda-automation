---
name: mnda-review
description: >
  This skill should be used when the user uploads or shares an NDA or MNDA file
  and asks to "review this NDA", "review this MNDA", "check this agreement",
  "redline this NDA", "what's wrong with this NDA", "is this NDA ok to sign",
  or any request to analyse or evaluate a non-disclosure agreement. Also triggers
  when the user forwards an NDA received from a counterparty and asks what to do with it.
version: 1.0.0
---

# MNDA Review Skill

Review incoming Mutual Non-Disclosure Agreements clause by clause against the legal playbook, classify each issue as GREEN / YELLOW / RED, generate redline suggestions, and produce a structured report ready to share with the team.

## Workflow

1. **Read the document** — parse the uploaded file or text provided by the user
2. **Detect known standards** — check if it matches Bonterms, Common Paper, or another known template
3. **Run playbook checks** — evaluate each clause against the 12 checks in `references/playbook.md`
4. **Classify overall status** — APPROVED, REVISIONS REQUIRED, or FLAGGED FOR LEGAL
5. **Generate redlines** — for every deviation, produce exact replacement language from the playbook
6. **Produce the review report** — structured markdown output with findings table and next steps
7. **Offer Slack summary** — ask if the user wants a formatted Slack message to send to the team

## Classification Rules

| Status | Meaning | Action |
|--------|---------|--------|
| GREEN | Clause meets or exceeds standard position | No action needed |
| YELLOW | Clause deviates but is fixable | Return redlines to counterparty |
| RED | Clause violates a non-negotiable position | Escalate to legal counsel |

**Overall status:**
- Any RED finding → **FLAGGED FOR LEGAL** — do not sign, escalate immediately
- Any YELLOW, no RED → **REVISIONS REQUIRED** — send redlines back to counterparty
- All GREEN → **APPROVED** — proceed to signature workflow

## Known Standards Fast-Path

If the document mentions "bonterms", "bonterms.com", "common paper", or "commonpaper.com", flag it as a known industry-standard template. Known-standard MNDAs with no RED flags can be classified APPROVED immediately. State the match prominently in the report.

## Report Format

```
## MNDA Review — [Counterparty Name]

**Status:** [APPROVED / REVISIONS REQUIRED / FLAGGED FOR LEGAL]
**Counterparty:** [Name]
**Reviewed:** [Date]
**Known Standard:** [Name if detected, otherwise —]

### Findings

| Clause | Status | Issue | Suggested Redline |
|--------|--------|-------|-------------------|
...

### Summary
[2-3 sentences on overall risk and recommended next step]

### Next Step
[One clear action: approve / send redlines / escalate]
```

## Playbook Reference

Load `references/playbook.md` for the full 12-clause playbook with preferred language for each check.

## Standard MNDA Template

If the counterparty's NDA has RED issues and needs to be replaced entirely, offer to generate a counter-proposal using the standard MNDA template in `references/standard-mnda-template.md`.
