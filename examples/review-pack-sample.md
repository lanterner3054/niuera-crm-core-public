# Sanitized Review Pack Sample

This is an example format for sharing private repository changes with an external AI reviewer.

## Rules

- Replace real secrets with REDACTED.
- Replace real customer and contact names with Example Company or Example Contact.
- Replace real IDs with PR001, C001, D001.
- Do not include production server IPs.
- Do not include real webhook URLs.
- Do not include private Git history.

## Example metadata

Commit: abc1234
Title: Example sanitized change
Scope: scripts/check_email.py, scripts/outreach_cleanup.py

## Example findings to request

Ask the reviewer to check:

1. Environment variable loading.
2. Dry-run default behavior.
3. Confirmation gates before production writes.
4. Absence of hardcoded secrets.
5. Safe documentation updates.

## Example reviewer instruction

Review only this sanitized pack. Do not call MCP. Do not read server files. Do not access Feishu, n8n, Dify, or production infrastructure.
