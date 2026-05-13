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

## Writing safe Codex tasks

Use small, explicit Codex tasks that are easy to review and safe for a public repository.

- Give each Codex task one clear goal.
- Prefer small tasks with only 1-3 allowed files.
- Always specify allowed files and forbidden files.
- Always forbid production access, secrets, `.env` changes, force push, and unrelated rewrites.
- Documentation-only tasks may be merged quickly if only allowed files changed and the security scan passes.
- Script changes should be reviewed more carefully.
- Production-related changes must require human review before merge.

Example good Codex task prompt:

```text
Task goal:
Update the public AI collaboration guide with safe task-writing rules.

Allowed files:
- docs/ai-collaboration.md

Forbidden actions:
- Do not modify README.md, scripts/, configuration files, or any other files.
- Do not access production servers, external tools, private data, or secrets.
- Do not edit .env files, add tokens, rewrite unrelated content, force push, or rewrite Git history.

Validation requirements:
- Run python3 scripts/security_scan.py.
- Confirm that only the allowed file changed.

Output requirements:
- Summarize the documentation change.
- List validation commands and results.
- Suggest a commit message.
```
