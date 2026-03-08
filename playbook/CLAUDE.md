# CLAUDE.md

## Project
Mutual Confidentiality Agreement (MNDA) – company template for new counterparty

## Source Document
This project is based on the uploaded company MNDA template. Use that document as the primary source of truth for structure and legal language, and only deviate when explicitly instructed.

## Objective
Use this project to:
- prepare, customize, and review a Mutual Non-Disclosure / Mutual Confidentiality Agreement;
- fill in party details and deal-specific placeholders;
- identify drafting inconsistencies, risky provisions, and negotiation points;
- generate redlines, summaries, fallback language, and issue lists.

## Contract Type
Mutual Confidentiality Agreement between:
- **[COMPANY NAME]**, a Delaware company
- **[COUNTERPARTY]**, a counterparty to be inserted

## Known Fixed Company Details
Unless explicitly changed by approved legal instructions, keep these as default:
- Party name: **[COMPANY NAME]**
- Registered office: **[COMPANY ADDRESS]**
- Notice email: **nda@company.com**
- Governing law in current template: **California**
- Venue in current template: **Santa Clara, California**

## Placeholders To Complete
Before finalizing any draft, confirm and populate:
- Effective Date
- Counterparty legal name
- Counterparty jurisdiction of formation
- Counterparty registered office / address
- Counterparty notice address
- Counterparty notice email
- Signatory names
- Signatory titles
- Signature dates, if needed

## Business Purpose
The stated purpose in the template is:
- evaluating a potential business or commercial opportunity between the parties.

Do not broaden the purpose unless specifically requested.

## Core Commercial / Legal Positions
Preserve these positions unless instructed otherwise:
- Mutual disclosure structure
- Confidential Information includes non-public information disclosed before or after the Effective Date
- Use limitation: solely for the defined Purpose
- Disclosure permitted only to employees and consultants on a strict need-to-know basis
- Recipient remains liable for employees and consultants acts/omissions
- Standard of care: at least the same degree used for own similar confidential information, and in any event at least reasonable care
- Permitted compelled disclosure with prompt notice
- No license or joint venture created
- Information provided AS IS
- Return / deletion obligation upon termination or request
- Injunctive relief available
- Agreement term terminable on 30 days prior written notice
- Confidentiality survival: 5 years after expiration or termination
- No assignment without permission

## Review Priorities
When reviewing or revising this MNDA, prioritize:
1. party names, addresses, and signature blocks;
2. governing law and venue;
3. confidentiality survival period;
4. return / deletion obligations and certification timing;
5. affiliate scope;
6. residuals / compelled disclosure / compelled retention issues;
7. whether consultants should remain included;
8. whether the counterparty asks for broader use rights, indefinite term, or narrower injunctive relief;
9. consistency of section references and internal numbering;
10. whether "Purpose" is too broad.

## Drafting Rules For Claude
When editing this agreement:
- preserve the existing structure and tone unless a cleaner restatement is requested;
- use concise legal drafting, not business-marketing language;
- do not silently change risk allocation;
- when making edits, list the exact clauses changed;
- when suggesting redlines, explain the business/legal impact in plain English;
- flag ambiguous placeholders immediately;
- keep defined terms consistent and capitalized;
- do not invent missing party facts;
- if information is missing, leave a visible placeholder in brackets.

## Default Workflows

### If asked to prepare a clean draft
- produce a clean version with placeholders clearly marked;
- keep company defaults;
- fix obvious internal cross-references and typos.

### If asked to review counterparty redlines
- summarize all substantive changes;
- classify each as low / medium / high impact;
- suggest accept / push back / compromise positions.

### If asked for negotiation notes
For each point, provide:
- clause;
- current language summary;
- counterparty ask;
- risk to company;
- fallback option.

### If asked for a signature-ready version
Before producing it, verify:
- all placeholders are completed;
- internal references are correct;
- section numbering is correct;
- signature blocks match party names;
- notice details are complete.

## Output Preferences
When working on this project:
- prefer tables for issue lists and negotiation summaries;
- prefer clean redline explanations in bullets or side-by-side format;
- quote only the minimum necessary contract text;
- keep legal summaries in plain English first, then provide exact drafting if requested.

## Automation Workflow
### Phase 1: Extraction & Integration
1. Identify the Parties: Extract the legal name and address of the counterparty.
2. Company Details: Automatically integrate company legal details into the relevant fields.

### Phase 2: Playbook Review
Analyze the document against legal_playbook.md. For every clause, categorize it as:
- GREEN: Compliant — meets standard criteria.
- YELLOW: Needs Revision — deviates from the playbook but fixable.
- RED: Critical Issue — violates a non-negotiable term.

### Phase 3: Slack Summary
After review, generate a concise report formatted for Slack:
- Status: Approved / Revisions Required / Flagged for Legal
- Counterparty: [Name]
- Key Deviations: bulleted list citing the playbook
- Proposed Redlines: specific text to swap in

### Phase 4: File Organization
Standardized filename: YYYY-MM-DD_MNDA_[Counterparty Name]_[Status].docx
