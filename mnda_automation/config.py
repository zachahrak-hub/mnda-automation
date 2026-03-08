"""
config.py
---------
Load and validate all environment variables.
Call `get_config()` anywhere in the project to access settings.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


@dataclass
class Config:
    # Company
    company_name: str = ""
    company_address: str = ""
    company_notice_email: str = ""
    company_governing_law: str = "California"
    company_venue: str = "Santa Clara, California"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # Slack
    slack_webhook_url: str = ""
    slack_review_channel: str = "#legal-ndas"
    slack_bot_token: str = ""
    slack_app_token: str = ""

    # Email intake (IMAP)
    email_host: str = "imap.gmail.com"
    email_port: int = 993
    email_user: str = ""
    email_password: str = ""
    email_inbox_folder: str = "INBOX"
    email_mnda_keyword: str = "NDA"

    # SMTP sending
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "Legal Operations"

    # Google Drive
    google_drive_credentials_path: str = "credentials/google_service_account.json"
    google_drive_parent_folder_id: str = ""

    # Local storage fallback
    local_storage_path: str = "./reviews"

    # Automation
    email_poll_interval: int = 60
    review_mode: str = "both"   # claude | keywords | both
    log_level: str = "INFO"


def get_config() -> Config:
    """Return a Config object populated from environment variables."""
    return Config(
        company_name=os.getenv("COMPANY_NAME", ""),
        company_address=os.getenv("COMPANY_ADDRESS", ""),
        company_notice_email=os.getenv("COMPANY_NOTICE_EMAIL", ""),
        company_governing_law=os.getenv("COMPANY_GOVERNING_LAW", "California"),
        company_venue=os.getenv("COMPANY_VENUE", "Santa Clara, California"),

        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),

        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        slack_review_channel=os.getenv("SLACK_REVIEW_CHANNEL", "#legal-ndas"),
        slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
        slack_app_token=os.getenv("SLACK_APP_TOKEN", ""),

        email_host=os.getenv("EMAIL_HOST", "imap.gmail.com"),
        email_port=int(os.getenv("EMAIL_PORT", "993")),
        email_user=os.getenv("EMAIL_USER", ""),
        email_password=os.getenv("EMAIL_PASSWORD", ""),
        email_inbox_folder=os.getenv("EMAIL_INBOX_FOLDER", "INBOX"),
        email_mnda_keyword=os.getenv("EMAIL_MNDA_SUBJECT_KEYWORD", "NDA"),

        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_from_name=os.getenv("SMTP_FROM_NAME", "Legal Operations"),

        google_drive_credentials_path=os.getenv(
            "GOOGLE_DRIVE_CREDENTIALS_PATH", "credentials/google_service_account.json"
        ),
        google_drive_parent_folder_id=os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", ""),

        local_storage_path=os.getenv("LOCAL_STORAGE_PATH", "./reviews"),

        email_poll_interval=int(os.getenv("EMAIL_POLL_INTERVAL_SECONDS", "60")),
        review_mode=os.getenv("REVIEW_MODE", "both"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
