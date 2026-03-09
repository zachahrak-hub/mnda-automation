---
description: Full clause-by-clause MNDA review with redlines
allowed-tools: Read, Write, WebFetch
argument-hint: [file-path or "paste NDA text"]
---

Review the MNDA provided as $ARGUMENTS (file path or pasted text).

1. If a file path is given, read the file contents first.
2. Load the playbook from `${CLAUDE_PLUGIN_ROOT}/skills/mnda-review/references/playbook.md`.
3. Run a full clause-by-clause review following the `mnda-review` skill workflow.
4. Produce the structured findings report with GREEN / YELLOW / RED classification for each clause.
5. Include exact redline language for every deviation using the preferred language from the playbook.
6. State the overall status: APPROVED, REVISIONS REQUIRED, or FLAGGED FOR LEGAL.
7. Ask the user: "Would you like me to format this as a Slack message for your team?"
8. If the overall status is FLAGGED FOR LEGAL and the user wants a counter-proposal, offer to generate one using the standard MNDA template in `${CLAUDE_PLUGIN_ROOT}/skills/mnda-review/references/standard-mnda-template.md`.
