"""
test_review.py
--------------
Basic unit tests for the review engine.
Run with: pytest tests/
"""

import pytest
from mnda_automation.review import review_with_keywords, ReviewResult
from mnda_automation.parser import extract_counterparty_name


# ---------------------------------------------------------------------------
# Sample MNDA text fixtures
# ---------------------------------------------------------------------------

COMPLIANT_MNDA = """
MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is entered into as of March 1, 2026,
between Acme Corp Inc., a Delaware corporation ("Acme"), and TestCo Inc., a California
corporation ("Company").

1. PURPOSE. This Agreement is for evaluating a potential business or commercial opportunity.

2. MUTUAL DISCLOSURE. This Agreement shall be mutual. Both parties may disclose and
   receive Confidential Information under this Agreement.

3. CONFIDENTIAL INFORMATION. Each party may disclose non-public information to the other.
   Employees and consultants with a strict need-to-know basis may receive such information.

4. GOVERNING LAW. This Agreement shall be governed by the laws of the State of California.
   Venue shall be Santa Clara, California.

5. SURVIVAL. Confidentiality obligations shall survive expiration or termination for 5 years.

6. RETURN/DELETION. Upon request or termination, Recipient shall return or destroy all
   Confidential Information and certify compliance.

7. INJUNCTIVE RELIEF. Each party acknowledges that a breach may cause irreparable harm
   and that injunctive or equitable relief shall be available.

8. NO LICENSE. Nothing herein shall be construed to grant any license or create any
   joint venture, partnership, or agency relationship.

9. COMPELLED DISCLOSURE. Recipient shall provide prompt prior written notice if compelled
   to disclose by court order or legal process.

10. ASSIGNMENT. Neither party may assign this Agreement without the prior written consent
    of the other party.
"""

NONCOMPLIANT_MNDA = """
CONFIDENTIALITY AGREEMENT

This Agreement is entered into between BigVendor LLC ("Vendor") and the receiving party.

1. CONFIDENTIALITY. Vendor shall keep all information provided by Vendor confidential.
   This is a one-way agreement only.

2. TERM. This Agreement remains in effect for one (1) year.

3. JURISDICTION. This Agreement shall be governed by the laws of Delaware.

4. GENERAL. No other provisions apply beyond what is stated here.
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestKeywordReview:

    def test_compliant_mnda_returns_approved(self):
        result = review_with_keywords(COMPLIANT_MNDA, counterparty="Acme Corp Inc.")
        assert result.overall_status == "APPROVED"
        assert result.counterparty == "Acme Corp Inc."
        assert result.review_engine == "keywords"

    def test_compliant_mnda_has_no_red(self):
        result = review_with_keywords(COMPLIANT_MNDA)
        assert not result.has_red()

    def test_noncompliant_mnda_flags_issues(self):
        result = review_with_keywords(NONCOMPLIANT_MNDA)
        assert result.overall_status in ("REVISIONS_REQUIRED", "FLAGGED_FOR_LEGAL")
        assert result.has_red() or result.has_yellow()

    def test_noncompliant_mnda_flags_missing_mutual(self):
        result = review_with_keywords(NONCOMPLIANT_MNDA)
        mutual_finding = next(f for f in result.findings if f.clause == "Mutual Structure")
        assert mutual_finding.status == "RED"

    def test_noncompliant_mnda_flags_survival_period(self):
        result = review_with_keywords(NONCOMPLIANT_MNDA)
        survival = next(f for f in result.findings if "Survival" in f.clause)
        assert survival.status != "GREEN"

    def test_findings_count(self):
        result = review_with_keywords(COMPLIANT_MNDA)
        assert len(result.findings) == 10   # One per playbook check

    def test_suggested_filename_format(self):
        result = review_with_keywords(COMPLIANT_MNDA, counterparty="Acme Corp")
        assert result.suggested_filename.endswith(".docx")
        assert "MNDA" in result.suggested_filename
        assert "Acme" in result.suggested_filename

    def test_redlines_provided_for_deviations(self):
        result = review_with_keywords(NONCOMPLIANT_MNDA)
        for f in result.findings:
            if f.status != "GREEN":
                assert f.redline, f"Missing redline for {f.clause}"


class TestCounterpartyExtraction:

    def test_extract_from_compliant_mnda(self):
        name = extract_counterparty_name(COMPLIANT_MNDA, company_name="TestCo Inc.")
        assert name != "[COUNTERPARTY NAME]"

    def test_returns_placeholder_when_not_found(self):
        name = extract_counterparty_name("This is a short document with no party names.")
        assert name == "[COUNTERPARTY NAME]"


class TestResultFormatting:

    def test_format_slack_message(self):
        from mnda_automation.review import format_slack_message
        result = review_with_keywords(NONCOMPLIANT_MNDA, counterparty="BigVendor LLC")
        msg = format_slack_message(result)
        assert "BigVendor LLC" in msg
        assert "Status" in msg
        assert "Next Step" in msg

    def test_format_email_body(self):
        from mnda_automation.review import format_email_body
        result = review_with_keywords(COMPLIANT_MNDA, counterparty="Acme Corp")
        html = format_email_body(result)
        assert "<html>" in html
        assert "Acme Corp" in html
        assert "GREEN" in html
