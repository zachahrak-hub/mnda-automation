# mnda-automation

Automated MNDA review and routing pipeline for SaaS companies — reviews incoming NDAs against the legal playbook and routes for approval via Slack.

---

## Overview

This repository contains the automation workflow for handling incoming Mutual Non-Disclosure Agreements (MNDAs). When a third party sends an MNDA, the pipeline:

1. **Extracts** counterparty details from the document
2. **Reviews** every clause against the legal playbook
3. **Classifies** each clause as GREEN / YELLOW / RED
4. **Posts** a Slack summary for approval or revision
5. **Saves** the final document using a standardized filename

---

## Repository Structure

```
mnda-automation/
├── playbook/
│   ├── legal_playbook.md   # Clause-by-clause review criteria and standard positions
│   └── CLAUDE.md           # AI assistant instructions and company legal profile
├── scripts/
│   └── review_mnda.py      # Core automation script
├── reviews/                # Completed review outputs (gitignored in production)
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install requests
```

### 2. Set environment variables

```bash
export COMPANY_NAME="Your SaaS Company Inc."
export COMPANY_EMAIL="nda@yourcompany.com"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

### 3. Run a review

```bash
# From a file
python scripts/review_mnda.py --file path/to/mnda.txt

# From text input
python scripts/review_mnda.py --text "paste mnda content here"

# Without posting to Slack
python scripts/review_mnda.py --file mnda.txt --no-slack
```

---

## Playbook

The `playbook/legal_playbook.md` file defines the standard positions for every key MNDA clause, including:

- Mutual disclosure structure
- Confidentiality survival period (5 years)
- Governing law and venue
- Return / deletion obligations
- Injunctive relief preservation
- File naming convention

Review findings are classified as:

| Status | Meaning |
|---|---|
| GREEN | Compliant with standard position |
| YELLOW | Deviates — fixable with redlines |
| RED | Critical issue — escalate to legal |

---

## Slack Integration

Configure `SLACK_WEBHOOK_URL` with an incoming webhook from your Slack workspace. After each review the script posts a formatted summary:

```
MNDA Review — [Counterparty Name]
Status: Revisions Required
Key Deviations: ...
Suggested Filename: 2026-03-08_MNDA_Acme_Corp_RevisionRequired.docx
Next Step: Review deviations and return redlines to counterparty.
```

---

## File Naming Convention

All finalized MNDAs are named:

```
YYYY-MM-DD_MNDA_[Counterparty Name]_[Status].docx
```

---

## Contributing

1. Update `playbook/legal_playbook.md` to reflect any changes to standard legal positions.
2. Update `playbook/CLAUDE.md` when company details change.
3. Keep `scripts/review_mnda.py` in sync with playbook check keys.

---

*Maintained by Legal Operations.*
