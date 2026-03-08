#!/usr/bin/env python3
"""
run.py
------
MNDA Automation — main entry point.

Commands:
  review     Review a single MNDA file (manual / CLI mode)
  watch-email  Start the email inbox watcher daemon
  watch-slack  Start the Slack bot listener daemon

Examples:
  python run.py review --file path/to/nda.pdf
  python run.py review --file nda.docx --reply-to sender@example.com
  python run.py watch-email
  python run.py watch-slack
"""

import logging
import sys
import click

from mnda_automation.config import get_config
from mnda_automation.pipeline import run_pipeline


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """MNDA Automation — review, route, and store incoming NDAs automatically."""
    pass


@cli.command()
@click.option("--file", "-f", required=True, help="Path to the MNDA file (PDF, DOCX, or TXT).")
@click.option("--reply-to", "-r", default=None, help="Email address to send the review summary to.")
@click.option("--no-slack", is_flag=True, default=False, help="Skip posting to Slack.")
@click.option("--no-email", is_flag=True, default=False, help="Skip sending email reply.")
@click.option("--no-save", is_flag=True, default=False, help="Skip saving to Drive/local storage.")
def review(file, reply_to, no_slack, no_email, no_save):
    """Review a single MNDA file and route the result."""
    config = get_config()
    setup_logging(config.log_level)

    click.echo(f"Reviewing: {file}")

    # Temporarily override config if flags are set
    if no_slack:
        config.slack_webhook_url = ""
    if no_email:
        reply_to = None
    if no_save:
        config.google_drive_parent_folder_id = ""
        config.local_storage_path = ""

    try:
        result = run_pipeline(
            config=config,
            file_path=file,
            reply_to=reply_to,
        )
        click.echo(f"\nStatus       : {result.overall_status}")
        click.echo(f"Counterparty : {result.counterparty}")
        click.echo(f"Engine       : {result.review_engine}")
        click.echo(f"Filename     : {result.suggested_filename}")
        click.echo(f"\nFindings ({len(result.findings)}):")
        for f in result.findings:
            icon = {"GREEN": "✅", "YELLOW": "⚠️ ", "RED": "❌"}.get(f.status, "  ")
            click.echo(f"  {icon} [{f.status}] {f.clause}")
            if f.deviation:
                click.echo(f"       → {f.deviation}")
        click.echo("")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("watch-email")
def watch_email():
    """Start the email inbox watcher. Polls for new MNDA emails continuously."""
    config = get_config()
    setup_logging(config.log_level)

    if not config.email_user or not config.email_password:
        click.echo("Error: EMAIL_USER and EMAIL_PASSWORD must be set in .env", err=True)
        sys.exit(1)

    from mnda_automation.integrations import EmailWatcher

    def on_mnda_received(file_bytes: bytes, filename: str, sender_email: str):
        click.echo(f"New MNDA from {sender_email}: {filename}")
        try:
            result = run_pipeline(
                config=config,
                file_bytes=file_bytes,
                filename=filename,
                reply_to=sender_email,
            )
            click.echo(f"  → {result.overall_status} | {result.counterparty}")
        except Exception as e:
            click.echo(f"  Pipeline error: {e}", err=True)

    watcher = EmailWatcher(config, on_mnda_received)
    click.echo(f"Watching inbox: {config.email_user} (keyword: '{config.email_mnda_keyword}')")
    watcher.start()


@cli.command("watch-slack")
def watch_slack():
    """Start the Slack bot listener. Monitors channels for uploaded MNDA files."""
    config = get_config()
    setup_logging(config.log_level)

    if not config.slack_bot_token or not config.slack_app_token:
        click.echo("Error: SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in .env", err=True)
        sys.exit(1)

    from mnda_automation.integrations import SlackBotIntake

    def on_file_received(file_bytes: bytes, filename: str):
        click.echo(f"New Slack file: {filename}")
        try:
            result = run_pipeline(
                config=config,
                file_bytes=file_bytes,
                filename=filename,
            )
            click.echo(f"  → {result.overall_status} | {result.counterparty}")
        except Exception as e:
            click.echo(f"  Pipeline error: {e}", err=True)

    bot = SlackBotIntake(config, on_file_received)
    click.echo("Slack bot listening for MNDA files...")
    bot.start()


if __name__ == "__main__":
    cli()
