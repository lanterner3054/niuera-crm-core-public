## Summary

- [ ] What changed?
- [ ] Why is this needed?

## Scope checklist

- [ ] Only intended files changed
- [ ] No unrelated rewrites
- [ ] No generated cache files
- [ ] No `.env` or backup files

## Security checklist

- [ ] No API keys, passwords, tokens, or webhook URLs
- [ ] No server IPs or production endpoints
- [ ] No Feishu / n8n / Dify / MCP credentials or IDs
- [ ] No real customer, prospect, contact, company, email, or phone data

## Validation

- [ ] `python3 scripts/security_scan.py`
- [ ] Expected output: `No potential sensitive information found`

## Change type

- [ ] Documentation only
- [ ] Script/helper change
- [ ] MCP skeleton change
- [ ] Security-related change
- [ ] Production-related change

## Review notes

- [ ] Documentation-only PRs may be merged quickly if scope and scan are clean.
- [ ] Script changes require careful review.
- [ ] Auth, deployment, email, Feishu, n8n, Dify, MCP, or production-related changes require human review.
