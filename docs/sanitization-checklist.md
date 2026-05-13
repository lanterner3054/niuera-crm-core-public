# Sanitization Checklist

Use this checklist before publishing code, diffs, review packs, or documentation.

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

## Safe replacements

- Example Company A
- Example Energy Ltd
- Example Contact A
- PR001
- C001
- D001
- imap.example.com
- https://example.com/REDACTED_CALLBACK_PATH
- REDACTED

## Required local scans

Run these before publishing:

grep for known old secrets.
grep for server IPs.
grep for webhook URL patterns.
grep for production domains.
grep for real customer names.
check git status.
check git log to confirm clean public history.
