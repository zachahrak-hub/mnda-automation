# MNDA Automation

Automatically review, triage, and redline incoming Mutual Non-Disclosure Agreements — powered by Claude AI.

| | Cowork Plugin | Python Tool |
|---|---|---|
| **Who it's for** | Anyone with Claude Cowork | Developers / technical teams |
| **Setup** | 2 commands → done | Clone → configure .env → run |
| **How it works** | Upload NDA, say "review this" | Monitors email/Slack automatically |
| **Requires** | Claude Cowork desktop app | Python 3.9+ |

---

## Option 1 — Cowork Plugin (no coding needed)

### Install in 2 steps

**Step 1 — Build the plugin file:**
```bash
git clone https://github.com/zachahrak-hub/mnda-automation.git
cd mnda-automation/plugin && zip -r ../mnda-automation.plugin . && cd ..
```

**Step 2 — Install in Cowork:**
- Double-click **`mnda-automation.plugin`**
- Click **Accept**

Done. No API keys, no configuration needed.

### What you can do after installing
```
"Just got this NDA from Acme — quick look?"     ← 30-second triage
"Review this MNDA" (upload the file)             ← Full review + redlines
/mnda-review path/to/nda.pdf                     ← Slash command
"Generate a counter-proposal"                    ← When their NDA is unacceptable
"Format this for Slack"                          ← Slack-ready summary
```

### What the review covers

12 clauses checked against a built-in legal playbook — Mutual Structure, Survival Period (3–5 years preferred), Governing Law (Delaware/California), Injunctive Relief, Standard of Care, Exceptions to Confidentiality (all 4 required), Return or Destruction, No-Solicitation (flag if present), Unilateral NDA Detection, Definition of Confidential Information, Agreement Term, and Permitted Disclosures.

**Bonterms and Common Paper MNDAs are auto-approved** — known industry-standard templates get classified GREEN immediately.

### Customise the playbook

Edit `plugin/skills/mnda-review/references/playbook.md` to change clause positions, preferred language, or severity levels.

---

## Option 2 — Python Automation Tool

For teams that want automatic monitoring of an inbox or Slack channel.

```bash
# 1. Clone and install
git clone https://github.com/zachahrak-hub/mnda-automation.git
cd mnda-automation && bash install.sh

# 2. Configure
cp .env.example .env
nano .env  # Add your API keys

# 3. Run
mnda review path/to/nda.pdf   # Review a single file
mnda watch-email               # Monitor inbox automatically
mnda watch-slack               # Monitor Slack channel
```

### What it does automatically

When an NDA arrives via email or Slack, the tool:

1. Detects the NDA attachment and extracts the text
2. Reviews it clause by clause against your playbook using Claude AI
3. Identifies the counterparty name from the document
4. Creates a Google Drive folder: `MNDA - {Counterparty} - {Date}`
5. Saves the original NDA, review report, and redlines file to that folder
6. Sends a Slack notification with the full summary and a link to Drive

### Risk classification

| Status | Meaning | Action |
|---|---|---|
| ✅ GREEN | Meets all standard positions | Ready to sign |
| 🟡 YELLOW | Minor deviations found | Send auto-generated redlines |
| 🔴 RED | Significant issues | Escalate to legal counsel |

### Required configuration (.env)

| Setting | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude AI review engine |
| `SLACK_BOT_TOKEN` | Optional | Slack notifications |
| `EMAIL_USER` / `EMAIL_PASSWORD` | Optional | Email monitoring |
| `GOOGLE_DRIVE_ENABLED=true` | Optional | Auto Drive folder creation |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Optional | Path to Drive credentials |

### Review modes

```bash
# In your .env file:
REVIEW_MODE=claude    # Full Claude AI review (recommended)
REVIEW_MODE=keywords  # Fast offline review — no API key needed
REVIEW_MODE=both      # Claude first, keywords as fallback
```

---

## Forking & Customising for Your Own Company

Want to use this tool with your own company's legal playbook? Fork it in 5 steps.

### Step 1 — Fork the repository

Go to [github.com/zachahrak-hub/mnda-automation](https://github.com/zachahrak-hub/mnda-automation) and click **Fork** (top right).
This creates your own copy at `github.com/YOUR-USERNAME/mnda-automation`.

### Step 2 — Clone your fork

```bash
git clone https://github.com/YOUR-USERNAME/mnda-automation
cd mnda-automation
```

### Step 3 — Install

```bash
bash install.sh
```

### Step 4 — Configure for your company

```bash
cp .env.example .env
# Fill in your API keys
```

### Step 5 — Customise the playbook

Edit `playbook/playbook.json` to match your company's legal standards — change preferred language, severity levels, governing law, or add new clause checks. No Python knowledge needed.

### Keep up to date with the original repo

```bash
git remote add upstream https://github.com/zachahrak-hub/mnda-automation
git fetch upstream
git merge upstream/main
```

---

## Repository Structure

```
mnda-automation/
├── plugin/                          ← Cowork plugin source
│   ├── .claude-plugin/plugin.json
│   ├── commands/mnda-review.md
│   ├── skills/mnda-review/          ← Full review + redlines
│   ├── skills/mnda-triage/          ← Quick 30-second triage
│   └── CONNECTORS.md
├── mnda_automation/                 ← Python package
│   ├── review.py                    ← Review engine (Claude AI + keywords)
│   ├── drive.py                     ← Google Drive integration
│   ├── parser.py                    ← PDF/DOCX/TXT parser
│   └── config.py                    ← Configuration loader
├── playbook/playbook.json           ← 12-clause playbook + known standards
├── install.sh                       ← One-command installer
└── .env.example                     ← Configuration template
```

---

## License

MIT — free to use, modify, and distribute.
