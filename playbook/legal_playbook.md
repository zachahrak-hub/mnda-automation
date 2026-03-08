# MNDA Legal Playbook

> This playbook governs the review of all incoming Mutual Non-Disclosure Agreements (MNDAs). Use it as the baseline against which any third-party draft is evaluated.

---

## 1. Company Profile (Fixed Defaults)

| Field | Value |
|---|---|
| Legal Entity | [COMPANY NAME] |
| Jurisdiction | Delaware |
| Registered Office | [COMPANY ADDRESS] |
| Notice Email | nda@company.com |
| Governing Law (default) | California |
| Venue (default) | Santa Clara, California |

**Do not change these defaults** unless explicitly approved by legal.

---

## 2. Counterparty Placeholders — Must Be Completed Before Any Draft Is Finalized

- [ ] Effective Date
- [ ] Counterparty legal name
- [ ] Counterparty jurisdiction of formation
- [ ] Counterparty registered office / address
- [ ] Counterparty notice address
- [ ] Counterparty notice email
- [ ] Signatory name(s)
- [ ] Signatory title(s)
- [ ] Signature date(s)

---

## 3. Non-Negotiable / Preferred Positions

| Clause | Standard Position |
|---|---|
| Structure | Mutual disclosure (both parties are disclosing and receiving) |
| Scope of CI | All non-public information disclosed before or after the Effective Date |
| Use Limitation | Solely for the defined Purpose (evaluating a potential business/commercial opportunity) |
| Permitted Disclosees | Employees and consultants on strict need-to-know basis only |
| Liability for Disclosees | Recipient remains liable for employees and consultants acts/omissions |
| Standard of Care | At least the same degree as own similar confidential information; minimum: reasonable care |
| Compelled Disclosure | Permitted with prompt prior written notice to disclosing party |
| No License / JV | Expressly excluded |
| Information Warranty | Provided AS IS |
| Return / Deletion | Required upon termination or written request |
| Injunctive Relief | Expressly preserved |
| Agreement Term | Terminable on 30 days prior written notice |
| Confidentiality Survival | 5 years after expiration or termination |
| Assignment | No assignment without prior written consent |

---

## 4. Confidential Information Exclusions (Standard)

1. Information that is or becomes publicly available through no fault of the recipient.
2. Information already in the recipient's possession prior to disclosure, as evidenced by written records.
3. Information lawfully received from a third party with the right to disclose it.
4. Information independently developed by the recipient without use of or reference to the disclosing party's CI.

> **Flag** if a counterparty adds additional exclusions (e.g., residuals clause, reverse-engineering carve-out).

---

## 5. Data Protection Position

- Each party represents it will comply with applicable data privacy and data protection laws.
- If the company will process personal data on the counterparty's behalf going forward, the parties will work in good faith to enter a separate DPA.
- **Do not** expand this into a full DPA within the MNDA unless specifically instructed.

---

## 6. Review Classification Framework

| Symbol | Status | Meaning |
|---|---|---|
| GREEN | Compliant | Meets or exceeds standard position |
| YELLOW | Needs Revision | Deviates from the playbook but fixable with specific redline language |
| RED | Critical Issue | Violates a non-negotiable term — must be escalated before execution |

---

## 7. Review Priorities (In Order)

1. Party names, addresses, and signature blocks
2. Governing law and venue
3. Confidentiality survival period
4. Return / deletion obligations and certification timing
5. Affiliate scope
6. Residuals / compelled disclosure / compelled retention issues
7. Whether consultants remain included or are excluded
8. Whether the counterparty seeks broader use rights, indefinite term, or narrower injunctive relief
9. Consistency of section cross-references and internal numbering
10. Whether "Purpose" is too broad for the company's risk tolerance

---

## 8. Workflow

### Incoming Third-Party Draft

Step 1: Extract counterparty details (name, address, jurisdiction)
Step 2: Auto-fill company details if missing
Step 3: Review each clause against this playbook
Step 4: Classify each clause (GREEN / YELLOW / RED)
Step 5: Generate Slack summary (see Section 9)
Step 6: Suggest standardized filename (see Section 10)

---

## 9. Slack Summary Output Format

*MNDA Review — [Counterparty Name]*

*Status:* [Approved / Revisions Required / Flagged for Legal]
*Counterparty:* [Legal Entity Name]
*Effective Date:* [Date or TBD]

*Key Deviations:*
- [Clause] — [Issue] — Playbook requires: [Standard position]

*Proposed Redlines:*
- [Clause X]: Replace [counterparty language] with [standard language]

*Next Step:* [Approve / Revise and return / Escalate to legal]

---

## 10. File Naming Convention

YYYY-MM-DD_MNDA_[Counterparty Name]_[Status].docx

Examples:
- 2026-03-08_MNDA_Acme_Corp_Approved.docx
- 2026-03-08_MNDA_GlobalVendorInc_RevisionRequired.docx

---

## 11. Drafting Rules

- Preserve existing structure and tone unless a restatement is explicitly requested
- Use concise legal drafting language
- Do not silently change risk allocation
- When making edits, list the exact clauses changed
- When suggesting redlines, explain the business/legal impact in plain English first
- Flag ambiguous or missing placeholders immediately — do not invent facts
- Keep defined terms consistent and capitalized throughout
- If information is missing, use a visible [BRACKET PLACEHOLDER]

---

*Last updated: 2026-03-08 | Maintained by: Legal Operations*
