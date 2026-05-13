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

## security_scan.py

Runs a lightweight local scan for common sensitive information patterns before committing to the public repository.

The scanner recursively checks text files in the repository, skipping `.git`, `node_modules`, `__pycache__`, `.venv`, `dist`, and `build`. It reports only the file path, line number, and risk type so that suspected values are not printed to the terminal.

Example command:

```bash
python3 scripts/security_scan.py
```

Exit codes:

- `0`: no suspected sensitive information found
- `1`: one or more suspected risks found
