# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. Plugins are tool-agnostic — they describe workflows in terms of categories rather than specific products.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options |
|----------|-------------|-----------------|---------------|
| Chat | `~~chat` | Slack | Microsoft Teams, Discord |
| Email | `~~email` | Gmail | Outlook, any IMAP client |
| Storage | `~~storage` | Google Drive | Dropbox, OneDrive |

## How to connect

To enable Slack notifications after a review, connect Slack via the Cowork connectors panel. Once connected, ask Claude: "Send this review to Slack."

To enable email monitoring, connect Gmail via the Cowork connectors panel. Once connected, ask Claude: "Watch my inbox for incoming NDAs."
