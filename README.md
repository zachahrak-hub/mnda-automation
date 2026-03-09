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
"Just got this NDA from Acme — quick look?"       ← 30-second triage
"Review this MNDA"  (upload the file)              ← Full review + redlines
/mnda-review path/to/nda.pdf                       ← Slash command
"Generate a counter-proposal"                      ← When their NDA is unacceptable
"Format this for Slack"                            ← Slack-ready summary
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
nano .env   # Set COMPANY_NAME at minimum

# 3. Run
mnda review path/to/nda.pdf   # Review a file
mnda watch-email               # Monitor inbox
mnda watch-slack               # Monitor Slack channel
```

Monitors Gmail/Outlook for NDA attachments, reviews with Claude AI (keyword fallback), posts results to Slack, saves to Google Drive or local folder.

See [MNDA_Automation_Setup_Guide.docx](MNDA_Automation_Setup_Guide.docx) for full setup instructions.

---

## Repository Structure

```
mnda-automation/
├── plugin/                           ← Cowork plugin source (build this into .plugin)
│   ├── .claude-plugin/plugin.json
│   ├── commands/mnda-review.md
│   ├── skills/mnda-review/           ← Full review + redlines
│   ├── skills/mnda-triage/           ← Quick 30-second triage
│   └── CONNECTORS.md
├── mnda_automation/                  ← Python package
│   ├── review.py                     ← Review engine
│   ├── parser.py                     ← PDF/DOCX/TXT parser
│   ├── integrations.py               ← Slack, email, Google Drive
│   └── pipeline.py                   ← End-to-end orchestration
├── playbook/playbook.json            ← Structured clause checks + known standards
├── templates/standard_mnda_template.docx
├── install.sh                        ← One-command Python installer
└── .env.example                      ← Configuration template
```

---

## License

MIT — free to use, modify, and distribute.
