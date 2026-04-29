# Scripts

## check_email.py

Reads unread mailbox messages and forwards parsed email content to a configured webhook.

Configuration is loaded from environment variables:

- NIUERA_IMAP_HOST
- NIUERA_IMAP_PORT
- NIUERA_IMAP_USER
- NIUERA_IMAP_PASS
- NIUERA_EMAIL_WEBHOOK_URL
- NIUERA_PROCESSED_EMAILS_FILE

## outreach_cleanup.py

Prints or executes planned cleanup updates for Outreach prospect records.

Default mode is dry-run. It does not write to Feishu unless run with execute mode.

Example execute command:

python3 scripts/outreach_cleanup.py --execute

Execution mode also requires typed confirmation.
