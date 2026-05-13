# Sanitization Checklist

Use this checklist before publishing code, diffs, review packs, or documentation.

## Before opening a PR

- Run `python3 scripts/security_scan.py`.
- Confirm only intended files changed.
- Confirm no generated cache files are included.
- Confirm no `.env` or backup files are included.

## Must remove or replace

- Real passwords
- API keys
- Access tokens
- Refresh tokens
- GitHub tokens
- Feishu APP_SECRET
- Feishu app_token
- Feishu table_id
- n8n webhook URLs
- Dify app keys
- SMTP or IMAP credentials
- Server IP addresses
- Internal domains
- Real customer names
- Real contact names
- Real prospect IDs linked to internal CRM records
- Real company classifications such as invalid, duplicate, junk, low quality
- Private Git history

## Secrets checklist

Confirm the repository, diff, review pack, and documentation contain:

- No API keys
- No passwords
- No tokens
- No webhook URLs
- No private keys
- No SMTP or IMAP credentials
- No Feishu, n8n, Dify, or MCP credentials

## Production data checklist

Confirm the repository, diff, review pack, and documentation contain:

- No real customer names
- No real prospect names
- No real contact names
- No real company data
- No real email addresses
- No real phone numbers
- No production table IDs or app IDs

## Endpoint checklist

Confirm the repository, diff, review pack, and documentation contain:

- No server IPs
- No production domains
- No webhook paths
- No internal service URLs
- Only placeholders such as `example.invalid`, `REDACTED_ENDPOINT`, or `PLACEHOLDER_ID`

## AI review checklist

- Claude reviews public repo content, PR diff, or a sanitized review pack only.
- Codex tasks must state allowed files and forbidden files.
- AI must not use MCP or production access for public repo review.

## Safe replacements

- Example Company A
- Example Energy Ltd
- Example Contact A
- PR001
- C001
- D001
- imap.example.com
- example.invalid
- REDACTED_ENDPOINT
- PLACEHOLDER_ID
- REDACTED

## Required local scans

Run these before publishing:

- grep for known old secrets.
- grep for server IPs.
- grep for webhook URL patterns.
- grep for production domains.
- grep for real customer names.
- check git status.
- check git log to confirm clean public history.

## Final merge checklist

- Files changed match the task scope.
- `security_scan.py` reports: `No potential sensitive information found`.
- Human reviewed the PR summary.
- Merge only after scope and scan are clean.
