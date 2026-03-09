# MNDA Automation

Automatically review, triage, and redline incoming Mutual Non-Disclosure Agreements — powered by Claude AI.

Two ways to use it:

| | Cowork Plugin | Python Tool |
|---|---|---|
| **Who it's for** | Anyone with Claude Cowork | Developers / technical teams |
| **Setup** | Install plugin → done | Clone repo → configure .env → run |
| **How it works** | Upload NDA, say "review this" | Monitors email/Slack automatically |
| **Requires** | Claude Cowork desktop app | Python 3.9+, API keys |

---

## Option 1 — Cowork Plugin (Recommended)

### Install in 1 click

1. Download **[mnda-automation.plugin](https://github.com/zachahrak-hub/mnda-automation/raw/main/mnda-automation.plugin)**
2. Open Claude Cowork
3. Double-click the `.plugin` file — click **Accept**

That's it. No configuration needed.

### What you can do after installing

**Triage a new NDA (30-second scan):**
> "Just got this NDA from Acme Corp — quick look?"

**Full clause-by-clause review with redlines:**
> "Review this MNDA" ← upload the file

**Use the slash command:**
```
/mnda-review path/to/nda.pdf
```

**Generate a counter-proposal** (when their NDA is unacceptable):
> "Generate a counter-proposal using our standard template"

**Get a Slack-ready summary:**
> "Format this for Slack"

### What the review covers

12 clauses checked against a built-in legal playbook:

- Mutual Structure
- Survival Period (3–5 years preferred)
- Governing Law (Delaware / California)
- Injunctive Relief
- Standard of Care
- Exceptions to Confidentiality (all 4 required)
- Return or Destruction
- No-Solicitation Clause (flag if present)
- Unilateral NDA Detection
- Definition of Confidential Information
- Agreement Term / Duration
- Permitted Disclosures (Need to Know)

**Bonterms and Common Paper MNDAs are auto-approved** — if the document matches a known industry-standard template, it gets classified GREEN immediately.

### Customise the playbook

Edit `skills/mnda-review/references/playbook.md` inside the plugin to change clause positions, preferred language, or severity levels for your organisation.

---

## Option 2 — Python Automation Tool

For teams that want automatic monitoring of an email inbox or Slack channel.

### Get started in 3 steps

**1. Clone the repository**
```bash
git clone https://github.com/zachahrak-hub/mnda-automation.git
cd mnda-automation
```

**2. Install everything**
```bash
bash install.sh
```

**3. Configure**
```bash
nano .env   # Set COMPANY_NAME at minimum
```

### Run it

```bash
# Review a single file
mnda review path/to/nda.pdf

# Monitor your email inbox
mnda watch-email

# Monitor a Slack channel
mnda watch-slack
```

### What it does

- Monitors Gmail / Outlook inbox for NDA attachments (IMAP)
- Monitors a Slack channel for shared NDA files
- Reviews with Claude AI or keyword matching (offline fallback)
- Posts colour-coded results to Slack
- Saves agreements to Google Drive or local folder, named by counterparty

See the [Setup Guide](MNDA_Automation_Setup_Guide.docx) for full configuration instructions.

---

## Repository Structure

```
mnda-automation/
├── mnda-automation.plugin        ← Cowork plugin (download this)
├── mnda_automation/              ← Python package
│   ├── review.py                 ← Review engine
│   ├── parser.py                 ← PDF/DOCX/TXT parser
│   ├── integrations.py           ← Slack, email, Drive
│   └── pipeline.py               ← End-to-end orchestration
├── playbook/
│   └── playbook.json             ← Clause checks + known standards
├── templates/
│   └── standard_mnda_template.docx
├── install.sh                    ← One-command installer
└── .env.example                  ← Configuration template
```

---

## License

MIT — free to use, modify, and distribute.
