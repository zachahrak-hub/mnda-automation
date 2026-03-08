#!/usr/bin/env python3
"""
review_mnda.py
--------------
MNDA Automation Pipeline for incoming Mutual Non-Disclosure Agreements.

Workflow:
  1. Receive MNDA text (from email/Slack via webhook or manual paste)
  2. Extract counterparty details
  3. Review each clause against the legal playbook
  4. Generate a Slack-formatted summary
  5. Suggest a standardized filename

Usage:
  python review_mnda.py --file path/to/mnda.txt
  python review_mnda.py --text "paste mnda text here"

Environment variables required:
  SLACK_WEBHOOK_URL   - Incoming webhook URL to post review summaries
  ANTHROPIC_API_KEY   - API key for Claude review (optional if using manual mode)
"""

import os
import sys
import json
import argparse
import datetime
import re

try:
    import requests
except ImportError:
    requests = None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COMPANY_NAME = os.getenv("COMPANY_NAME", "[COMPANY NAME]")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "nda@company.com")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Playbook — key positions that must be present in any accepted MNDA
PLAYBOOK = {
    "mutual_structure": {
        "description": "Agreement must be mutual (both parties disclose and receive)",
        "keywords": ["mutual", "both parties", "each party"],
        "severity": "RED",
    },
    "survival_period": {
        "description": "Confidentiality obligations must survive for at least 5 years",
        "keywords": ["5 years", "five years", "survival"],
        "severity": "YELLOW",
    },
    "governing_law": {
        "description": "Governing law should be California (flag if different)",
        "keywords": ["california", "governing law"],
        "severity": "YELLOW",
    },
    "injunctive_relief": {
        "description": "Injunctive relief must be expressly available",
        "keywords": ["injunctive", "equitable relief", "specific performance"],
        "severity": "RED",
    },
    "no_license": {
        "description": "No license or joint venture should be created",
        "keywords": ["no license", "no joint venture", "does not grant"],
        "severity": "YELLOW",
    },
    "return_deletion": {
        "description": "Return or deletion of confidential information must be required",
        "keywords": ["return", "destroy", "delete", "deletion"],
        "severity": "YELLOW",
    },
    "purpose_defined": {
        "description": "Purpose must be narrowly defined (evaluating a business opportunity)",
        "keywords": ["purpose", "business opportunity", "potential"],
        "severity": "YELLOW",
    },
}


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_mnda_text(args):
    """Load MNDA text from file or direct input."""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    elif args.text:
        return args.text
    else:
        print("Reading MNDA from stdin... (Ctrl+D to end)")
        return sys.stdin.read()


def extract_counterparty(text):
    """
    Attempt to extract the counterparty name from the MNDA text.
    Returns a dict with name and any other found details.
    """
    counterparty = {"name": "[COUNTERPARTY NAME]", "address": "[ADDRESS]", "jurisdiction": "[JURISDICTION]"}

    # Simple heuristics — replace with Claude API call for production
    lines = text.split("\n")
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if "between" in line_lower and COMPANY_NAME.lower() in line_lower:
            # Next line may contain counterparty name
            if i + 1 < len(lines):
                counterparty["name"] = lines[i + 1].strip().strip(",").strip(".")
                break
        if "counterparty" in line_lower or ("and" in line_lower and "inc" in line_lower):
            match = re.search(r'([A-Z][A-Za-z\s,\.]+(?:Inc|LLC|Ltd|Corp|Limited)[\.\,]?)', line)
            if match:
                counterparty["name"] = match.group(1).strip()

    return counterparty


def review_against_playbook(text):
    """
    Run the MNDA text against each playbook check.
    Returns a list of findings: {check, status, description, found}
    """
    findings = []
    text_lower = text.lower()

    for check_name, check in PLAYBOOK.items():
        found = any(kw in text_lower for kw in check["keywords"])
        if found:
            status = "GREEN"
        else:
            status = check["severity"]

        findings.append({
            "check": check_name,
            "status": status,
            "description": check["description"],
            "found": found,
        })

    return findings


def format_slack_message(counterparty, findings, filename):
    """Format the review result as a Slack message."""
    has_red = any(f["status"] == "RED" for f in findings)
    has_yellow = any(f["status"] == "YELLOW" and not f["found"] for f in findings)

    if has_red:
        overall = ":red_circle: *Flagged for Legal Review*"
    elif has_yellow:
        overall = ":warning: *Revisions Required*"
    else:
        overall = ":white_check_mark: *Approved*"

    deviations = [f for f in findings if not f["found"]]
    deviation_lines = "\n".join(
        f"  • [{f['status']}] {f['description']}" for f in deviations
    ) or "  None — all standard positions found."

    message = f"""*MNDA Review — {counterparty['name']}*

*Status:* {overall}
*Counterparty:* {counterparty['name']}
*Reviewed on:* {datetime.date.today().isoformat()}

*Key Deviations:*
{deviation_lines}

*Suggested Filename:*
  `{filename}`

*Next Step:* {"Escalate to legal counsel before signing." if has_red else "Review deviations and return redlines to counterparty." if has_yellow else "Ready for signature workflow."}
"""
    return message


def build_filename(counterparty, findings):
    """Generate a standardized filename."""
    has_red = any(f["status"] == "RED" for f in findings)
    has_yellow = any(f["status"] == "YELLOW" and not f["found"] for f in findings)

    if has_red:
        status = "FlaggedForLegal"
    elif has_yellow:
        status = "RevisionRequired"
    else:
        status = "Approved"

    safe_name = re.sub(r'[^A-Za-z0-9]', '_', counterparty['name'])
    date_str = datetime.date.today().isoformat()
    return f"{date_str}_MNDA_{safe_name}_{status}.docx"


def post_to_slack(message):
    """Post the review summary to Slack via webhook."""
    if not SLACK_WEBHOOK_URL:
        print("\n[Slack] No webhook configured. Message would be:\n")
        print(message)
        return

    if requests is None:
        print("Install 'requests' to post to Slack: pip install requests")
        return

    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
    if response.status_code == 200:
        print("[Slack] Review posted successfully.")
    else:
        print(f"[Slack] Failed to post: {response.status_code} {response.text}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Review an incoming MNDA against the legal playbook.")
    parser.add_argument("--file", help="Path to MNDA text file")
    parser.add_argument("--text", help="MNDA text as a string")
    parser.add_argument("--no-slack", action="store_true", help="Skip posting to Slack")
    args = parser.parse_args()

    print("Loading MNDA...")
    mnda_text = load_mnda_text(args)

    print("Extracting counterparty details...")
    counterparty = extract_counterparty(mnda_text)
    print(f"  Counterparty: {counterparty['name']}")

    print("Reviewing against playbook...")
    findings = review_against_playbook(mnda_text)

    filename = build_filename(counterparty, findings)
    message = format_slack_message(counterparty, findings, filename)

    print("\n" + "="*60)
    print(message)
    print("="*60)

    if not args.no_slack:
        post_to_slack(message)

    # Save findings as JSON for downstream processing
    output = {
        "counterparty": counterparty,
        "findings": findings,
        "suggested_filename": filename,
        "reviewed_at": datetime.datetime.utcnow().isoformat(),
    }
    out_path = filename.replace(".docx", "_findings.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nFindings saved to: {out_path}")


if __name__ == "__main__":
    main()
