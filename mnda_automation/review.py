"""
review.py
---------
Core MNDA review engine.

Modes:
  1. claude   — sends the full document to Claude with a structured prompt
                and parses the JSON response.
  2. keywords — fast local check using the JSON playbook (no API key needed).
  3. both     — tries Claude first; falls back to keywords on API error.

The review engine loads checks from playbook/playbook.json so the playbook
can be edited without touching Python code.

Public API:
  review_mnda(text, config, counterparty_hint="") -> ReviewResult
"""

import json
import re
import logging
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Google Drive integration (optional — only active if configured)
try:
    from .drive import save_mnda_to_drive
    _DRIVE_MODULE_AVAILABLE = True
except ImportError:
    _DRIVE_MODULE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Playbook loader
# ---------------------------------------------------------------------------
_PLAYBOOK_PATH = Path(__file__).parent.parent / "playbook" / "playbook.json"
_PLAYBOOK = None


def load_playbook():
    global _PLAYBOOK
    if _PLAYBOOK is None:
        if _PLAYBOOK_PATH.exists():
            with open(_PLAYBOOK_PATH) as f:
                _PLAYBOOK = json.load(f)
            logger.info("Loaded playbook: %d checks, %d known standards",
                        len(_PLAYBOOK.get("checks", [])),
                        len(_PLAYBOOK.get("known_standards", [])))
        else:
            logger.warning("playbook.json not found — using built-in defaults.")
            _PLAYBOOK = _builtin_playbook()
    return _PLAYBOOK


def _builtin_playbook():
    return {
        "known_standards": [],
        "checks": [
            {"id": "mutual_structure", "name": "Mutual Structure", "severity": "RED",
             "keywords": ["mutual", "both parties", "each party"],
             "red_flag_keywords": ["one-way", "unilateral"],
             "guidance": "Agreement must impose confidentiality obligations on both parties.",
             "redline_suggestion": "Change to mutual obligations on both parties."},
            {"id": "injunctive_relief", "name": "Injunctive Relief", "severity": "YELLOW",
             "keywords": ["injunctive", "equitable relief", "irreparable"],
             "red_flag_keywords": [],
             "guidance": "Injunctive relief must be available to both parties.",
             "redline_suggestion": "Add injunctive relief clause."},
            {"id": "exceptions", "name": "Exceptions to Confidentiality", "severity": "RED",
             "keywords": ["public domain", "publicly available", "prior knowledge", "independently developed"],
             "red_flag_keywords": [],
             "guidance": "Must include standard four-part exceptions.",
             "redline_suggestion": "Add standard exceptions clause."},
        ]
    }


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    clause: str
    status: str
    description: str
    deviation: str = ""
    redline: str = ""


@dataclass
class ReviewResult:
    counterparty: str
    review_date: str
    overall_status: str
    findings: List[Finding] = field(default_factory=list)
    standard_match: Optional[str] = None
    raw_text: str = ""
    suggested_filename: str = ""
    review_engine: str = "keywords"
    drive_folder_link: str = ""      # populated after Drive upload

    def has_red(self):
        return any(f.status == "RED" for f in self.findings)

    def has_yellow(self):
        return any(f.status == "YELLOW" for f in self.findings)


# ---------------------------------------------------------------------------
# Known-standard detection (Bonterms, Common Paper, etc.)
# ---------------------------------------------------------------------------
def detect_known_standard(text):
    text_lower = text.lower()
    playbook = load_playbook()
    for standard in playbook.get("known_standards", []):
        if any(signal in text_lower for signal in standard.get("signals", [])):
            logger.info("Detected known standard: %s", standard["name"])
            return standard
    return None


# ---------------------------------------------------------------------------
# Keyword / heuristic review
# ---------------------------------------------------------------------------
def review_with_keywords(text, counterparty=""):
    text_lower = text.lower()
    playbook = load_playbook()
    findings = []
    standard_match = detect_known_standard(text)

    for check in playbook.get("checks", []):
        has_positive = any(kw in text_lower for kw in check.get("keywords", []))
        has_red_flag = any(kw in text_lower for kw in check.get("red_flag_keywords", []))

        if has_red_flag:
            status = check.get("severity", "YELLOW")
            deviation = f"Red-flag term detected: '{check['red_flag_keywords'][0]}'"
            redline = check.get("redline_suggestion", "")
        elif has_positive:
            status = "GREEN"
            deviation = ""
            redline = ""
        else:
            status = check.get("severity", "YELLOW")
            kws = check.get("keywords", [check.get("name", "")])
            deviation = f"Not found — '{kws[0]}' and related terms absent."
            redline = check.get("redline_suggestion", "")

        findings.append(Finding(
            clause=check.get("name", check.get("id", "")),
            status=status,
            description=check.get("guidance", ""),
            deviation=deviation,
            redline=redline,
        ))

    result = _build_result(counterparty, findings, "keywords")
    result.standard_match = standard_match["name"] if standard_match else None
    if standard_match and standard_match.get("classification") == "GREEN" and not result.has_red():
        result.overall_status = "APPROVED"
    return result


# ---------------------------------------------------------------------------
# Claude AI review
# ---------------------------------------------------------------------------
def _build_claude_prompt(text, playbook):
    checks_text = "\n".join(
        f"{i+1}. {c.get('name', c.get('id', ''))} — {c.get('guidance', '')}"
        for i, c in enumerate(playbook.get("checks", []))
    )
    standards_text = "\n".join(
        f"- {s['name']}: signals {s['signals']} — auto-{s['classification']}"
        for s in playbook.get("known_standards", [])
    )
    preferred = "\n".join(
        f"  {c.get('name', '')}: \"{c.get('preferred_language') or c.get('redline_suggestion', '')}\""
        for c in playbook.get("checks", [])
        if c.get("preferred_language") or c.get("redline_suggestion")
    )
    return f"""You are a legal operations assistant reviewing an incoming Mutual Non-Disclosure Agreement (MNDA).
Review the document against the following standard positions and respond ONLY with valid JSON.

KNOWN INDUSTRY STANDARDS:
{standards_text or "None defined."}

PLAYBOOK CHECKS:
{checks_text}

PREFERRED LANGUAGE FOR REDLINES:
{preferred}

JSON schema:
{{
  "counterparty_name": "Legal entity name from the document",
  "standard_match": "Name of known standard if detected, or null",
  "findings": [
    {{
      "clause": "Clause name",
      "status": "GREEN | YELLOW | RED",
      "description": "What the standard position requires",
      "deviation": "What the document says that differs, or empty string",
      "redline": "Exact replacement language, or empty string"
    }}
  ],
  "summary": "One-sentence plain-English summary of overall risk"
}}

Document:
---
{text[:25000]}
---
"""


def review_with_claude(text, config):
    try:
        import anthropic
    except ImportError:
        raise ImportError("Install anthropic: pip install anthropic")

    playbook = load_playbook()
    prompt = _build_claude_prompt(text, playbook)
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    message = client.messages.create(
        model=config.anthropic_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        raise ValueError("Claude response did not contain valid JSON.")
    data = json.loads(json_match.group())

    counterparty = data.get("counterparty_name", "[COUNTERPARTY NAME]")
    standard_match = data.get("standard_match")
    findings = [
        Finding(
            clause=f.get("clause", ""),
            status=f.get("status", "YELLOW"),
            description=f.get("description", ""),
            deviation=f.get("deviation", ""),
            redline=f.get("redline", ""),
        )
        for f in data.get("findings", [])
    ]
    result = _build_result(counterparty, findings, "claude-ai")
    result.standard_match = standard_match
    return result


# ---------------------------------------------------------------------------
# Google Drive helpers
# ---------------------------------------------------------------------------
def generate_redlines_text(result):
    """Generate redlines document. Named: '{Counterparty} - MNDA Redlines - {Date}.txt'"""
    lines = [
        f"MNDA REDLINES — {result.counterparty}",
        f"Date: {result.review_date}",
        f"Status: {result.overall_status}",
        f"Review Engine: {result.review_engine}",
        "=" * 60,
        "",
    ]
    redline_items = [f for f in result.findings if f.redline]
    if not redline_items:
        lines.append("No redlines required — document is fully compliant.")
    else:
        for f in redline_items:
            lines.append(f"[{f.status}] {f.clause}")
            lines.append(f"  Issue:   {f.deviation}")
            lines.append(f"  Redline: {f.redline}")
            lines.append("")
    return "\n".join(lines)


def _save_to_drive_if_configured(result, mnda_text, config):
    """
    If Google Drive is configured (GOOGLE_DRIVE_ENABLED=true in .env), uploads:
      - Original MNDA file
      - Review summary as '{Counterparty} - MNDA Review - {Date}.txt'
      - Redlines as '{Counterparty} - MNDA Redlines - {Date}.txt'
    All inside a Drive folder: 'MNDA - {Counterparty} - {Date}'
    """
    if not _DRIVE_MODULE_AVAILABLE:
        return
    if not getattr(config, "google_drive_enabled", False):
        return

    try:
        redlines_text = generate_redlines_text(result)
        review_text = format_slack_message(result)
        mnda_path = getattr(config, "mnda_file_path", None)

        drive_result = save_mnda_to_drive(
            mnda_path=mnda_path,
            review_text=review_text,
            redlines_text=redlines_text,
            mnda_text=mnda_text,
        )
        result.drive_folder_link = drive_result.get("folder_link", "")
        logger.info("Saved to Google Drive: %s", result.drive_folder_link)
        logger.info("Files uploaded: %s", [f["name"] for f in drive_result.get("files", [])])
    except Exception as e:
        logger.warning("Drive upload failed: %s", e)


# ---------------------------------------------------------------------------
# Combined entry point
# ---------------------------------------------------------------------------
def review_mnda(text, config, counterparty_hint=""):
    mode = config.review_mode.lower()

    if mode == "claude":
        result = review_with_claude(text, config)
    elif mode == "keywords":
        result = review_with_keywords(text, counterparty_hint)
    else:
        try:
            if not config.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set.")
            result = review_with_claude(text, config)
            logger.info("Claude review completed.")
        except Exception as e:
            logger.warning("Claude review failed (%s) — falling back to keywords.", e)
            result = review_with_keywords(text, counterparty_hint)

    # Save to Google Drive if configured
    _save_to_drive_if_configured(result, text, config)

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _build_result(counterparty, findings, engine):
    has_red = any(f.status == "RED" for f in findings)
    has_yellow = any(f.status == "YELLOW" for f in findings)
    if has_red:
        overall = "FLAGGED_FOR_LEGAL"
    elif has_yellow:
        overall = "REVISIONS_REQUIRED"
    else:
        overall = "APPROVED"

    date_str = datetime.date.today().isoformat()
    safe_name = re.sub(r"[^A-Za-z0-9]", "_", counterparty)
    filename = f"{date_str}_MNDA_{safe_name}_{overall}.docx"

    return ReviewResult(
        counterparty=counterparty,
        review_date=date_str,
        overall_status=overall,
        findings=findings,
        suggested_filename=filename,
        review_engine=engine,
    )


def format_slack_message(result):
    status_emoji = {"APPROVED": ":white_check_mark:", "REVISIONS_REQUIRED": ":warning:", "FLAGGED_FOR_LEGAL": ":red_circle:"}
    status_label = {"APPROVED": "Approved", "REVISIONS_REQUIRED": "Revisions Required", "FLAGGED_FOR_LEGAL": "Flagged for Legal Review"}
    emoji = status_emoji.get(result.overall_status, ":question:")
    label = status_label.get(result.overall_status, result.overall_status)
    standard_line = f"\n:bookmark: *Known Standard:* {result.standard_match}" if result.standard_match else ""
    drive_line = f"\n:file_folder: *Drive Folder:* {result.drive_folder_link}" if result.drive_folder_link else ""
    deviations = [f for f in result.findings if f.status != "GREEN"]
    dev_lines = "\n".join(f"  * [{f.status}] *{f.clause}* — {f.deviation}" for f in deviations) or "  None."
    redlines = [f for f in deviations if f.redline]
    redline_lines = "\n".join(f"  * *{f.clause}*: _{f.redline}_" for f in redlines) or "  No redlines required."
    next_step = {"APPROVED": "Ready for signature.", "REVISIONS_REQUIRED": "Return redlines to counterparty.", "FLAGGED_FOR_LEGAL": "Escalate to legal counsel."}.get(result.overall_status, "")

    return f"""{emoji} *MNDA Review — {result.counterparty}*{standard_line}
*Status:* {label} | *Reviewed:* {result.review_date} | *Engine:* {result.review_engine}{drive_line}
*Key Deviations:*
{dev_lines}
*Proposed Redlines:*
{redline_lines}
*Suggested Filename:* {result.suggested_filename}
*Next Step:* {next_step}"""


def format_email_body(result):
    status_color = {"APPROVED": "#16a34a", "REVISIONS_REQUIRED": "#d97706", "FLAGGED_FOR_LEGAL": "#dc2626"}.get(result.overall_status, "#374151")
    status_label = {"APPROVED": "Approved", "REVISIONS_REQUIRED": "Revisions Required", "FLAGGED_FOR_LEGAL": "Flagged for Legal Review"}.get(result.overall_status, result.overall_status)
    standard_html = f"<p><strong>Known Standard:</strong> {result.standard_match}</p>" if result.standard_match else ""
    drive_html = f'<p><strong>Google Drive Folder:</strong> <a href="{result.drive_folder_link}">View Files</a></p>' if result.drive_folder_link else ""
    rows = ""
    for f in result.findings:
        color = {"GREEN": "#16a34a", "YELLOW": "#d97706", "RED": "#dc2626"}.get(f.status, "#374151")
        rows += f'<tr><td style="padding:8px;border:1px solid #e5e7eb;">{f.clause}</td><td style="padding:8px;border:1px solid #e5e7eb;color:{color};font-weight:bold;">{f.status}</td><td style="padding:8px;border:1px solid #e5e7eb;">{f.deviation or "Compliant"}</td><td style="padding:8px;border:1px solid #e5e7eb;font-style:italic;font-size:12px;">{f.redline or ""}</td></tr>'
    return f"""<html><body style="font-family:Arial,sans-serif;max-width:760px;margin:0 auto;">
<h2>MNDA Review — {result.counterparty}</h2>
<p><strong>Status:</strong> <span style="color:{status_color};font-weight:bold;">{status_label}</span></p>
<p><strong>Counterparty:</strong> {result.counterparty} | <strong>Reviewed:</strong> {result.review_date} | <strong>Engine:</strong> {result.review_engine}</p>
{standard_html}{drive_html}
<h3>Review Findings</h3>
<table style="width:100%;border-collapse:collapse;font-size:14px;">
<thead><tr style="background:#f3f4f6;"><th style="padding:8px;border:1px solid #e5e7eb;text-align:left;">Clause</th><th style="padding:8px;border:1px solid #e5e7eb;text-align:left;">Status</th><th style="padding:8px;border:1px solid #e5e7eb;text-align:left;">Notes</th><th style="padding:8px;border:1px solid #e5e7eb;text-align:left;">Redline</th></tr></thead>
<tbody>{rows}</tbody></table>
<h3>Suggested Filename</h3>
<code style="background:#f3f4f6;padding:4px 8px;">{result.suggested_filename}</code>
<p style="margin-top:24px;color:#6b7280;font-size:12px;">Generated by MNDA Automation — engine: {result.review_engine}</p>
</body></html>"""
