"""
review.py
---------
Core MNDA review engine.

Two modes:
  1. Claude AI   — sends the full document to Claude with a structured prompt
                   and parses the JSON response.
  2. Keywords    — fast local check using regex / keyword matching.
  3. Both        — runs Claude first; falls back to keywords on API error.

Public API:
  review_mnda(text, config) -> ReviewResult
"""

import json
import re
import logging
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    clause: str
    status: str            # GREEN | YELLOW | RED
    description: str
    deviation: str = ""    # What the counterparty's version says
    redline: str = ""      # Suggested replacement language


@dataclass
class ReviewResult:
    counterparty: str
    review_date: str
    overall_status: str            # APPROVED | REVISIONS_REQUIRED | FLAGGED_FOR_LEGAL
    findings: List[Finding] = field(default_factory=list)
    raw_text: str = ""
    suggested_filename: str = ""
    review_engine: str = "keywords"

    def has_red(self) -> bool:
        return any(f.status == "RED" for f in self.findings)

    def has_yellow(self) -> bool:
        return any(f.status == "YELLOW" for f in self.findings)


# ---------------------------------------------------------------------------
# Keyword / heuristic review (no API key required)
# ---------------------------------------------------------------------------

PLAYBOOK_CHECKS = [
    {
        "clause": "Mutual Structure",
        "keywords": ["mutual", "both parties", "each party"],
        "description": "Agreement must be mutual — both parties disclose and receive.",
        "severity_if_missing": "RED",
        "redline": "This Agreement shall be mutual. Both parties may disclose and receive Confidential Information.",
    },
    {
        "clause": "Confidentiality Survival",
        "keywords": ["5 years", "five years", "survival", "survives"],
        "description": "Confidentiality obligations must survive at least 5 years after termination.",
        "severity_if_missing": "YELLOW",
        "redline": "Obligations of confidentiality shall survive termination or expiration of this Agreement for a period of five (5) years.",
    },
    {
        "clause": "Governing Law — California",
        "keywords": ["california", "governing law"],
        "description": "Governing law should be California (flag if different jurisdiction found).",
        "severity_if_missing": "YELLOW",
        "redline": "This Agreement shall be governed by the laws of the State of California.",
    },
    {
        "clause": "Injunctive Relief",
        "keywords": ["injunctive", "equitable relief", "specific performance", "irreparable"],
        "description": "Injunctive relief must be expressly available to both parties.",
        "severity_if_missing": "RED",
        "redline": "Each party acknowledges that a breach may cause irreparable harm and that injunctive or other equitable relief shall be available without bond.",
    },
    {
        "clause": "No License / No JV",
        "keywords": ["no license", "no joint venture", "does not grant", "no rights are granted"],
        "description": "No license, joint venture, or partnership should be created.",
        "severity_if_missing": "YELLOW",
        "redline": "Nothing in this Agreement shall be construed to grant any license or create any joint venture, partnership, or agency relationship.",
    },
    {
        "clause": "Return / Deletion Obligation",
        "keywords": ["return", "destroy", "delete", "deletion", "certif"],
        "description": "Recipient must return or destroy Confidential Information upon request or termination.",
        "severity_if_missing": "YELLOW",
        "redline": "Upon request or termination, Recipient shall promptly return or destroy all Confidential Information and certify compliance in writing.",
    },
    {
        "clause": "Purpose Defined",
        "keywords": ["purpose", "business opportunity", "potential", "evaluating"],
        "description": "Purpose must be narrowly defined — evaluating a potential business opportunity.",
        "severity_if_missing": "YELLOW",
        "redline": "The parties may use Confidential Information solely for the purpose of evaluating a potential business or commercial opportunity between them ('Purpose').",
    },
    {
        "clause": "Need-to-Know Disclosure",
        "keywords": ["need to know", "need-to-know", "employees", "representatives", "consultants"],
        "description": "Disclosure permitted only to employees/consultants on strict need-to-know basis.",
        "severity_if_missing": "YELLOW",
        "redline": "Recipient may disclose Confidential Information only to its employees and consultants who have a need to know and are bound by confidentiality obligations no less restrictive than this Agreement.",
    },
    {
        "clause": "Compelled Disclosure Notice",
        "keywords": ["compelled", "legal process", "court order", "subpoena", "prior notice", "prompt notice"],
        "description": "Compelled disclosure permitted only with prompt prior written notice to disclosing party.",
        "severity_if_missing": "YELLOW",
        "redline": "If Recipient is compelled to disclose Confidential Information by law, it shall provide prompt prior written notice to the disclosing party to the extent permitted by law.",
    },
    {
        "clause": "Assignment Restriction",
        "keywords": ["assign", "transfer", "without consent", "prior written consent"],
        "description": "No assignment without prior written consent of the other party.",
        "severity_if_missing": "YELLOW",
        "redline": "Neither party may assign this Agreement without the prior written consent of the other party.",
    },
]


def review_with_keywords(text: str, counterparty: str = "") -> ReviewResult:
    """Run the keyword/heuristic review. Returns a ReviewResult."""
    text_lower = text.lower()
    findings = []

    for check in PLAYBOOK_CHECKS:
        found = any(kw in text_lower for kw in check["keywords"])
        status = "GREEN" if found else check["severity_if_missing"]
        deviation = "" if found else f"Not found in document — '{check['keywords'][0]}' and related terms absent."
        redline = "" if found else check["redline"]

        findings.append(Finding(
            clause=check["clause"],
            status=status,
            description=check["description"],
            deviation=deviation,
            redline=redline,
        ))

    return _build_result(counterparty, findings, "keywords")


# ---------------------------------------------------------------------------
# Claude AI review
# ---------------------------------------------------------------------------

CLAUDE_REVIEW_PROMPT = """\
You are a legal operations assistant reviewing an incoming Mutual Non-Disclosure Agreement (MNDA).

Review the document against the following standard positions and respond ONLY with a valid JSON object — no markdown, no explanation, just JSON.

Standard positions to check:
1. Mutual Structure — both parties disclose and receive
2. Confidentiality Survival — at least 5 years post-termination
3. Governing Law — California preferred (flag other jurisdictions)
4. Injunctive Relief — expressly available
5. No License / No JV — no license or joint venture created
6. Return / Deletion Obligation — required on request or termination
7. Purpose Defined — narrowly scoped to evaluating a business opportunity
8. Need-to-Know Disclosure — employees/consultants only, strictly
9. Compelled Disclosure Notice — prior written notice required
10. Assignment Restriction — no assignment without written consent

Respond with this JSON schema exactly:
{
  "counterparty_name": "Legal entity name or [COUNTERPARTY NAME] if not found",
  "findings": [
    {
      "clause": "Clause name",
      "status": "GREEN | YELLOW | RED",
      "description": "What the standard position requires",
      "deviation": "What the document says that differs, or empty string if compliant",
      "redline": "Suggested replacement language if deviation exists, or empty string"
    }
  ],
  "summary": "One-sentence plain-English summary of the overall risk level"
}

Status definitions:
- GREEN: Compliant with or exceeds standard position
- YELLOW: Deviates but fixable with specific redline language
- RED: Violates a non-negotiable term — escalate to legal

Document to review:
---
{document}
---
"""


def review_with_claude(text: str, config) -> ReviewResult:
    """
    Send the MNDA text to Claude for AI-powered review.
    Returns a ReviewResult parsed from Claude's JSON response.
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("Install anthropic: pip install anthropic")

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    prompt = CLAUDE_REVIEW_PROMPT.replace("{document}", text[:25000])  # Token limit guard

    logger.info("Sending MNDA to Claude (%s)...", config.anthropic_model)
    message = client.messages.create(
        model=config.anthropic_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_response = message.content[0].text.strip()

    # Extract JSON even if Claude adds any surrounding text
    json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if not json_match:
        raise ValueError("Claude response did not contain valid JSON.")

    data = json.loads(json_match.group())

    counterparty = data.get("counterparty_name", "[COUNTERPARTY NAME]")
    findings = []
    for f in data.get("findings", []):
        findings.append(Finding(
            clause=f.get("clause", ""),
            status=f.get("status", "YELLOW"),
            description=f.get("description", ""),
            deviation=f.get("deviation", ""),
            redline=f.get("redline", ""),
        ))

    return _build_result(counterparty, findings, "claude-ai")


# ---------------------------------------------------------------------------
# Combined entry point
# ---------------------------------------------------------------------------

def review_mnda(text: str, config, counterparty_hint: str = "") -> ReviewResult:
    """
    Review an MNDA. Mode controlled by config.review_mode:
      - 'claude'   → Claude AI only
      - 'keywords' → keyword matching only
      - 'both'     → try Claude, fall back to keywords on failure
    """
    mode = config.review_mode.lower()

    if mode == "claude":
        return review_with_claude(text, config)

    if mode == "keywords":
        result = review_with_keywords(text, counterparty_hint)
        return result

    # both — try Claude first
    try:
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set — using keyword fallback.")
        result = review_with_claude(text, config)
        logger.info("Claude review completed.")
        return result
    except Exception as e:
        logger.warning("Claude review failed (%s) — falling back to keyword matching.", e)
        result = review_with_keywords(text, counterparty_hint)
        return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_result(counterparty: str, findings: List[Finding], engine: str) -> ReviewResult:
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


def format_slack_message(result: ReviewResult) -> str:
    """Format a ReviewResult as a Slack-ready message string."""
    status_emoji = {
        "APPROVED": ":white_check_mark:",
        "REVISIONS_REQUIRED": ":warning:",
        "FLAGGED_FOR_LEGAL": ":red_circle:",
    }
    status_label = {
        "APPROVED": "Approved",
        "REVISIONS_REQUIRED": "Revisions Required",
        "FLAGGED_FOR_LEGAL": "Flagged for Legal Review",
    }

    emoji = status_emoji.get(result.overall_status, ":question:")
    label = status_label.get(result.overall_status, result.overall_status)

    deviations = [f for f in result.findings if f.status != "GREEN"]
    dev_lines = "\n".join(
        f"  • [{f.status}] *{f.clause}* — {f.deviation}" for f in deviations
    ) or "  None — all standard positions found."

    redlines = [f for f in deviations if f.redline]
    redline_lines = "\n".join(
        f"  • *{f.clause}*: _{f.redline}_" for f in redlines
    ) or "  No redlines required."

    next_step = {
        "APPROVED": "Ready for signature workflow.",
        "REVISIONS_REQUIRED": "Review deviations and return redlines to counterparty.",
        "FLAGGED_FOR_LEGAL": "Escalate to legal counsel before signing.",
    }.get(result.overall_status, "")

    return f"""{emoji} *MNDA Review — {result.counterparty}*

*Status:* {label}
*Counterparty:* {result.counterparty}
*Reviewed:* {result.review_date}  |  *Engine:* {result.review_engine}

*Key Deviations:*
{dev_lines}

*Proposed Redlines:*
{redline_lines}

*Suggested Filename:*
  `{result.suggested_filename}`

*Next Step:* {next_step}"""


def format_email_body(result: ReviewResult) -> str:
    """Format a ReviewResult as an HTML email body."""
    status_color = {
        "APPROVED": "#16a34a",
        "REVISIONS_REQUIRED": "#d97706",
        "FLAGGED_FOR_LEGAL": "#dc2626",
    }.get(result.overall_status, "#374151")

    status_label = {
        "APPROVED": "✅ Approved",
        "REVISIONS_REQUIRED": "⚠️ Revisions Required",
        "FLAGGED_FOR_LEGAL": "🔴 Flagged for Legal Review",
    }.get(result.overall_status, result.overall_status)

    rows = ""
    for f in result.findings:
        color = {"GREEN": "#16a34a", "YELLOW": "#d97706", "RED": "#dc2626"}.get(f.status, "#374151")
        rows += f"""
        <tr>
          <td style="padding:8px;border:1px solid #e5e7eb;">{f.clause}</td>
          <td style="padding:8px;border:1px solid #e5e7eb;color:{color};font-weight:bold;">{f.status}</td>
          <td style="padding:8px;border:1px solid #e5e7eb;">{f.deviation or "Compliant"}</td>
        </tr>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;">
      <h2 style="color:#111827;">MNDA Review — {result.counterparty}</h2>
      <p><strong>Status:</strong> <span style="color:{status_color};font-weight:bold;">{status_label}</span></p>
      <p><strong>Counterparty:</strong> {result.counterparty}</p>
      <p><strong>Reviewed:</strong> {result.review_date} &nbsp;|&nbsp; <strong>Engine:</strong> {result.review_engine}</p>

      <h3>Review Findings</h3>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <thead>
          <tr style="background:#f3f4f6;">
            <th style="padding:8px;border:1px solid #e5e7eb;text-align:left;">Clause</th>
            <th style="padding:8px;border:1px solid #e5e7eb;text-align:left;">Status</th>
            <th style="padding:8px;border:1px solid #e5e7eb;text-align:left;">Notes</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>

      <h3>Suggested Filename</h3>
      <code style="background:#f3f4f6;padding:4px 8px;border-radius:4px;">{result.suggested_filename}</code>

      <p style="margin-top:24px;color:#6b7280;font-size:12px;">
        Generated by MNDA Automation &mdash; review engine: {result.review_engine}
      </p>
    </body></html>"""
