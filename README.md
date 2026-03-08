# mnda-automation

> Automated MNDA review pipeline. Clone it, run the installer, fill in your API keys — done.

When a counterparty sends an MNDA, this tool automatically:
- **Parses** the document (PDF, DOCX, or plain text)
- **Reviews** every clause against your legal playbook using Claude AI
- **Posts** a summary to Slack with status, deviations, and suggested redlines
- **Emails** the review back to the sender
- **Saves** the MNDA to a counterparty-named folder in Google Drive (or locally)

---

## Get Started in 3 Steps

### Step 1 — Clone and install

```bash
git clone https://github.com/zachahrak-hub/mnda-automation.git
cd mnda-automation
bash install.sh
```

The installer will:
- Check your Python version (3.9+ required)
- Create a virtual environment
- Install all dependencies
- Create a `.env` file from the template

---

### Step 2 — Fill in your `.env`

Open `.env` in any text editor. At minimum, set these four values:

```env
COMPANY_NAME="Your Company Inc."
COMPANY_NOTICE_EMAIL="nda@yourcompany.com"
ANTHROPIC_API_KEY=sk-ant-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

> Full configuration reference at the bottom of this file.

---

### Step 3 — Run it

```bash
# Activate the environment first (do this once per terminal session)
source .venv/bin/activate

# Review a single MNDA file
mnda review --file path/to/nda.pdf

# Or use make
make review FILE=path/to/nda.pdf
```

---

## All Commands

```bash
mnda review --file nda.pdf                        # Review one file
mnda review --file nda.pdf --reply-to a@co.com   # Review + email result to sender
mnda review --file nda.pdf --no-slack             # Review without posting to Slack
mnda watch-email                                   # Start email inbox watcher (runs continuously)
mnda watch-slack                                   # Start Slack bot listener (runs continuously)
```

Or with `make`:

```bash
make review FILE=nda.pdf
make watch-email
make watch-slack
make test
```

---

## What You Get After a Review

### Terminal output
```
Status       : REVISIONS_REQUIRED
Counterparty : Acme Corp Inc.
Engine       : claude-ai
Filename     : 2026-03-08_MNDA_Acme_Corp_Inc_REVISIONS_REQUIRED.docx

Findings (10):
  OK  [GREEN]  Mutual Structure
  OK  [GREEN]  Confidentiality Survival
  !!  [YELLOW] Governing Law — California
               Document uses Delaware law. Playbook requires California.
  OK  [GREEN]  Injunctive Relief
  ...
```

### Slack message
```
MNDA Review — Acme Corp Inc.

Status: Revisions Required
Counterparty: Acme Corp Inc.

Key Deviations:
  [YELLOW] Governing Law — Document uses Delaware law.
  [YELLOW] Return / Deletion Obligation — Certification requirement missing.

Proposed Redlines:
  Governing Law: "This Agreement shall be governed by the laws of the State of California."
  Return / Deletion: "...and certify compliance in writing within 10 business days."

Suggested Filename: 2026-03-08_MNDA_Acme_Corp_REVISIONS_REQUIRED.docx
Next Step: Review deviations and return redlines to counterparty.
```

### Saved file
```
reviews/
└── Acme_Corp_Inc/
    ├── 2026-03-08_MNDA_Acme_Corp_Inc_REVISIONS_REQUIRED.docx
    └── 2026-03-08_MNDA_Acme_Corp_Inc_REVISIONS_REQUIRED_review.txt
```

---

## Automating Email Intake

When `mnda watch-email` is running, any email that arrives with "NDA" in the subject line and a PDF or DOCX attachment will automatically trigger the full pipeline and reply to the sender.

**Gmail setup:**
1. Enable 2-Step Verification on your Google account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) and generate an App Password
3. Set in `.env`:

```env
EMAIL_HOST=imap.gmail.com
EMAIL_USER=legal@yourcompany.com
EMAIL_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_USER=legal@yourcompany.com
SMTP_PASSWORD=your-app-password
```

---

## Automating Slack Intake

When `mnda watch-slack` is running, any PDF or DOCX file uploaded to your Slack workspace triggers the pipeline.

**Setup:**
1. Go to [api.slack.com/apps](https://api.slack.com/apps) and create a new app
2. Enable **Socket Mode** and generate an App Token (`xapp-...`)
3. Add Bot Token scopes: `files:read`, `channels:history`, `im:history`
4. Install the app to your workspace and copy the Bot Token (`xoxb-...`)
5. Set in `.env`:

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
```

---

## Google Drive Storage

Without Google Drive configured, reviewed MNDAs are saved to `./reviews/` locally. To enable Drive:

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a project
2. Enable the **Google Drive API**
3. Create a **Service Account**, download its JSON key, and save as `credentials/google_service_account.json`
4. Share your target Drive folder with the service account email address
5. Copy the folder ID from the URL and set:

```env
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials/google_service_account.json
GOOGLE_DRIVE_PARENT_FOLDER_ID=your-folder-id-here
```

---

## Customizing the Playbook

Edit `playbook/legal_playbook.md` to change your standard legal positions. The review engine in `mnda_automation/review.py` references `PLAYBOOK_CHECKS` — keep those entries in sync with your playbook.

Edit `playbook/CLAUDE.md` to update your company's fixed details (name, address, governing law, etc.).

---

## Configuration Reference

| Variable | Required | Description |
|---|---|---|
| `COMPANY_NAME` | Yes | Your legal entity name |
| `COMPANY_NOTICE_EMAIL` | Yes | Your NDA contact email |
| `ANTHROPIC_API_KEY` | Yes (AI mode) | Claude API key — [get one here](https://console.anthropic.com) |
| `ANTHROPIC_MODEL` | No | Default: `claude-sonnet-4-6` |
| `SLACK_WEBHOOK_URL` | Yes | Incoming webhook for review notifications |
| `SLACK_BOT_TOKEN` | Slack intake | Bot token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | Slack intake | App token (`xapp-...`) |
| `EMAIL_HOST` | Email intake | Default: `imap.gmail.com` |
| `EMAIL_USER` | Email intake | Your inbox address |
| `EMAIL_PASSWORD` | Email intake | App password |
| `SMTP_HOST` | Email replies | Default: `smtp.gmail.com` |
| `SMTP_USER` | Email replies | Sending address |
| `SMTP_PASSWORD` | Email replies | App password |
| `GOOGLE_DRIVE_CREDENTIALS_PATH` | Drive storage | Path to service account JSON |
| `GOOGLE_DRIVE_PARENT_FOLDER_ID` | Drive storage | Root Drive folder for MNDA storage |
| `REVIEW_MODE` | No | `claude` / `keywords` / `both` (default: `both`) |
| `EMAIL_POLL_INTERVAL_SECONDS` | No | Default: `60` |

---

## Project Structure

```
mnda-automation/
├── install.sh                      <- Run this first
├── Makefile                        <- make review / watch-email / watch-slack
├── run.py                          <- CLI entry point
├── pyproject.toml                  <- Package definition (pip install .)
├── requirements.txt
├── .env.example                    <- Copy to .env and fill in your values
│
├── mnda_automation/
│   ├── config.py                   <- Load settings from .env
│   ├── parser.py                   <- PDF / DOCX / TXT extraction
│   ├── review.py                   <- Claude AI + keyword review engine
│   ├── integrations.py             <- Slack, email, Google Drive, local storage
│   └── pipeline.py                 <- End-to-end orchestrator
│
├── playbook/
│   ├── legal_playbook.md           <- Your clause-by-clause review criteria
│   └── CLAUDE.md                   <- Company legal profile for the AI
│
└── tests/
    └── test_review.py              <- pytest test suite
```

---

## Requirements

- Python 3.9 or higher
- An [Anthropic API key](https://console.anthropic.com) for Claude AI review
- A [Slack Incoming Webhook](https://api.slack.com/apps) for notifications

---

## License

MIT — clone it, use it, modify it freely.
