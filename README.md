# NIUERA CRM Core Public

This is the public, sanitized collaboration repository for the NIUERA CRM Core project.

It contains:
- public architecture notes
- sanitized scripts
- AI collaboration rules
- non-secret environment templates
- review packs and examples

It does not contain:
- production secrets
- real customer data
- real Feishu app tokens or table IDs
- real n8n webhook URLs
- real Dify API keys
- real server IPs
- private Git history

## Purpose

This repository is used for AI-assisted code review and collaboration between ChatGPT, Codex, and Claude without exposing production credentials or business-sensitive data.

## Private production repository

The production repository remains private. This public repository is a sanitized mirror for review and discussion only.

## AI collaboration workflow

### Repository purpose

- This is a public sanitized collaboration repo.
- It is not the production deployment repo.

### Recommended AI workflow

- Codex: small code edits, documentation updates, helper scripts, and pull requests.
- Claude: pull request and diff review, security review, and architecture review.
- ChatGPT: step-by-step operational guidance, command explanation, and troubleshooting.
- GitHub: the collaboration center for issues, branches, reviews, and pull requests.
- Production server: only sync reviewed stable changes.

### Safe task boundaries

- AI should only modify GitHub repo code.
- AI must not connect to production servers.
- AI must not access Feishu, n8n, Dify, MCP Server, email, or production data.
- AI must not generate or commit real secrets.
- AI must not modify `.env`.
- AI must not force push unless a human explicitly decides.

### Review checklist before merge

- Only allowed files changed.
- No secrets.
- No real customer or prospect data.
- Local checks passed.
- PR diff was reviewed by a human.
