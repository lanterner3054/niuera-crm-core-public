# Contributing

This is a public sanitized collaboration repository.

## Contribution rules

1. Do not commit production secrets.
2. Do not commit real customer data.
3. Do not commit real Feishu app tokens, table IDs, API keys, webhook URLs, or server IP addresses.
4. Do not copy private repository Git history into this repository.
5. Keep all runtime values in environment variables.
6. Use example records only.

## Review workflow

1. Make changes in this public repository or prepare a sanitized review pack.
2. Ask Claude or another reviewer to review only GitHub public content or the sanitized pack.
3. Do not allow MCP, server, Feishu, n8n, Dify, or production access during public code review.
4. Apply approved patterns manually to the private production repository.

## Commit message style

Use short action-oriented messages, for example:

- Add sanitized review checklist
- Update public MCP skeleton
- Improve outreach cleanup dry-run docs
