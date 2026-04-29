# Security Policy

This public repository must never contain:

- production passwords
- API keys
- Feishu APP_SECRET
- Feishu app_token or table_id values from production
- n8n webhook IDs
- Dify app keys
- SMTP credentials
- real customer data
- server IP addresses
- private Git history

## Secret handling

All runtime values must be loaded from environment variables.

## Git history rule

This repository starts from a clean public history. It must not be created by pushing the private repository history.

## Review pack rule

If a diff references removed secrets, it must be sanitized before being shared with external reviewers.
