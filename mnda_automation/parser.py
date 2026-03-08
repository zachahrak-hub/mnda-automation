"""
parser.py
---------
Extract plain text from MNDA documents in various formats.
Supported: PDF, DOCX, TXT, email body (plain text / HTML).
"""

import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def parse_file(file_path: str) -> str:
    """
    Auto-detect file type and extract text.

    Args:
        file_path: Absolute or relative path to the document.

    Returns:
        Extracted plain text.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return parse_pdf(file_path)
    elif suffix in (".docx", ".doc"):
        return parse_docx(file_path)
    elif suffix in (".txt", ".md"):
        return parse_text(file_path)
    else:
        logger.warning("Unknown file type %s — attempting plain text read.", suffix)
        return parse_text(file_path)


def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("Install pdfplumber: pip install pdfplumber")

    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def parse_docx(file_path: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("Install python-docx: pip install python-docx")

    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def parse_text(file_path: str) -> str:
    """Read a plain-text or Markdown file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_email_body(raw_body: str) -> str:
    """
    Strip HTML tags from an email body and return clean plain text.
    Falls through gracefully if the body is already plain text.
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", raw_body)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_counterparty_name(text: str, company_name: str = "") -> str:
    """
    Heuristically extract the counterparty's legal name from the MNDA text.
    Returns a cleaned name or '[COUNTERPARTY NAME]' if not found.
    """
    # Patterns: "between X and Y", "AGREEMENT between X and Y"
    patterns = [
        r"between\s+(.+?)\s+(?:and|&)\s+" + re.escape(company_name),
        r"between\s+" + re.escape(company_name) + r"\s+(?:and|&)\s+(.+?)[\.,\n]",
        r"(?:counterparty|vendor|customer|partner)[:\s]+([A-Z][A-Za-z\s,\.]+(?:Inc|LLC|Ltd|Corp|Limited|GmbH|AG|BV|SAS|SRL)?[\.,]?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip().rstrip(".,;")
            if len(name) > 3:
                return name

    # Fallback: look for capitalized entity names near MNDA/NDA keywords
    entity_pattern = r"\b([A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)*\s+(?:Inc|LLC|Ltd|Corp|Limited|GmbH|AG|BV|SAS|SRL)[\.,]?)\b"
    matches = re.findall(entity_pattern, text)
    for m in matches:
        clean = m.strip().rstrip(".,")
        if company_name and company_name.lower() not in clean.lower():
            return clean

    return "[COUNTERPARTY NAME]"
