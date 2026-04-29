# AI Collaboration Rules

## Roles

- ChatGPT / Codex: implementation guidance, code edits, command generation.
- Claude: code review, architecture review, risk review.
- GitHub: shared source of truth for public sanitized collaboration.
- Production server: not modified directly by AI.

## Claude review mode

When asking Claude to review this repository:

1. Do not allow MCP access.
2. Do not allow server file reads.
3. Do not allow Feishu, n8n, Dify, or production access.
4. Review only GitHub commits, pull requests, or pasted sanitized review packs.
5. If context is missing, ask for pasted context instead of calling tools.

## Production safety rule

This public repo is not a production deployment source. Any production change must be reviewed and manually applied to the private production repository first.
