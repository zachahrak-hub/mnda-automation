"""Google Drive integration for MNDA Automation."""

import os
import re
from pathlib import Path
from datetime import date

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    DRIVE_AVAILABLE = True
except ImportError:
    DRIVE_AVAILABLE = False

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_drive_service():
    """Build Google Drive service from service account credentials."""
    if not DRIVE_AVAILABLE:
        raise ImportError(
            "Google Drive dependencies not installed.\n"
            "Run: pip install google-auth google-auth-oauthlib google-api-python-client"
        )
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not creds_path:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not set in .env")
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)


def extract_counterparty_name(mnda_text: str) -> str:
    """Extract the counterparty company name from MNDA text."""
    patterns = [
        r'(?:between|by and between)\s+(?:Coralogix[^,\n]*?(?:,|and|&)\s*)([A-Z][A-Za-z0-9\s,\.]+?(?:Inc|LLC|Ltd|Corp|Corporation|Limited|GmbH|BV|SAS|AG)\.?)',
        r'(?:and|&)\s+([A-Z][A-Za-z0-9\s]+?(?:Inc|LLC|Ltd|Corp|Corporation|Limited|GmbH|BV|SAS|AG)\.?)\s*[,\(]',
        r'([A-Z][A-Za-z0-9\s]+?(?:Inc|LLC|Ltd|Corp|Corporation|Limited)\.?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, mnda_text[:3000])
        if match:
            name = match.group(1).strip().rstrip(',.')
            if len(name) > 3 and name.lower() not in ['the', 'and', 'inc', 'llc']:
                return name
    return "Unknown Counterparty"


def create_mnda_folder(counterparty_name: str, parent_folder_id: str = None):
    """Create a Google Drive folder for this MNDA. Returns (folder_id, folder_link)."""
    service = get_drive_service()
    today = date.today().strftime("%Y-%m-%d")
    folder_name = f"MNDA - {counterparty_name} - {today}"

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]

    folder = service.files().create(
        body=file_metadata, fields='id,name,webViewLink'
    ).execute()

    print(f"✅ Created Drive folder: {folder['name']}")
    print(f"   🔗 {folder['webViewLink']}")
    return folder['id'], folder['webViewLink']


def upload_to_drive(file_path: str, folder_id: str, mime_type: str = None) -> str:
    """Upload a file to a Google Drive folder. Returns the file link."""
    service = get_drive_service()
    file_path = Path(file_path)

    if not mime_type:
        mime_map = {
            '.pdf':  'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt':  'text/plain',
            '.md':   'text/markdown',
            '.json': 'application/json',
        }
        mime_type = mime_map.get(file_path.suffix.lower(), 'application/octet-stream')

    file_metadata = {'name': file_path.name, 'parents': [folder_id]}
    media = MediaFileUpload(str(file_path), mimetype=mime_type)
    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields='id,name,webViewLink'
    ).execute()

    print(f"   📄 Uploaded: {uploaded['name']}")
    return uploaded['webViewLink']


def save_mnda_to_drive(mnda_path: str, review_text: str, redlines_text: str, mnda_text: str) -> dict:
    """
    Full workflow:
      1. Extract counterparty name from MNDA text
      2. Create a Drive folder: "MNDA - {Counterparty} - {Date}"
      3. Upload original MNDA
      4. Upload review report as "{Counterparty} - MNDA Review - {Date}.txt"
      5. Upload redlines as "{Counterparty} - MNDA Redlines - {Date}.txt"

    Returns dict with counterparty, folder_link, and list of uploaded files.
    """
    parent_folder_id = os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID")
    today = date.today().strftime("%Y-%m-%d")

    # Step 1 - identify counterparty
    counterparty = extract_counterparty_name(mnda_text)
    print(f"\n📋 Counterparty identified: {counterparty}")

    # Step 2 - create folder
    folder_id, folder_link = create_mnda_folder(counterparty, parent_folder_id)

    results = {
        "counterparty": counterparty,
        "folder_link": folder_link,
        "files": [],
    }

    # Step 3 - upload original MNDA
    if mnda_path and Path(mnda_path).exists():
        link = upload_to_drive(mnda_path, folder_id)
        results["files"].append({"name": Path(mnda_path).name, "link": link})

    # Step 4 - upload review report
    review_filename = f"{counterparty} - MNDA Review - {today}.txt"
    review_tmp = Path(f"/tmp/{review_filename}")
    review_tmp.write_text(review_text, encoding="utf-8")
    link = upload_to_drive(str(review_tmp), folder_id, mime_type="text/plain")
    results["files"].append({"name": review_filename, "link": link})

    # Step 5 - upload redlines with company name + date
    redlines_filename = f"{counterparty} - MNDA Redlines - {today}.txt"
    redlines_tmp = Path(f"/tmp/{redlines_filename}")
    redlines_tmp.write_text(redlines_text, encoding="utf-8")
    link = upload_to_drive(str(redlines_tmp), folder_id, mime_type="text/plain")
    results["files"].append({"name": redlines_filename, "link": link})

    return results
