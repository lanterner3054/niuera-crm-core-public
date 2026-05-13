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

## Repository purpose

This repository is a public, sanitized collaboration repo for AI-assisted code review, documentation review, example scripts, and sanitized review packs.

This repository is not a production deployment repo. Production systems and production data stay outside this public repository.

## Private production repository

The production repository remains private. This public repository is a sanitized mirror for review and discussion only.

## Recommended AI workflow

- **Codex**: make small, scoped code changes, documentation updates, test scripts, and pull requests in this GitHub repository.
- **Claude**: review pull requests and diffs, with focus on security review, architecture review, and risk review.
- **ChatGPT**: explain operating steps, commands, troubleshooting options, and implementation plans.
- **GitHub**: act as the only collaboration center for public sanitized changes, reviews, and pull requests.
- **Production server**: sync only reviewed, stable versions through the approved human-controlled release process.

## Safe task boundaries

AI assistants working with this repository must follow these boundaries:

- Only change code and documentation inside the GitHub repository and only within the files allowed by the task.
- Do not connect directly to any production server.
- Do not access production data from Feishu, n8n, Dify, MCP Server, email systems, or related integrations.
- Do not generate, request, paste, or commit real secrets, tokens, webhook URLs, server IPs, table IDs, customer names, or contact names.
- Do not modify `.env` or any real configuration file.
- Do not use `force push` or rewrite Git history unless a human explicitly decides to do so.

## Example Codex task prompt

```text
You are working in the NIUERA CRM Core public sanitized repository.

Task:
Update README.md to document the local development workflow, or add a small sanitized helper script.

Allowed files:
- README.md
- scripts/example_helper.py

Forbidden actions:
- Do not modify .env or real configuration files.
- Do not connect to production servers.
- Do not access Feishu, n8n, Dify, MCP Server, email, or production data.
- Do not add real secrets, tokens, webhook URLs, server IPs, table IDs, customer names, or contact names.
- Do not force push or rewrite Git history.

Validation requirements:
- Run the relevant local syntax or test command.
- Run python3 scripts/security_scan.py if available.
- Report any findings without automatically deleting unrelated content.
```

## Review checklist before merge

Before merging any pull request, verify that:

- Only the files allowed by the task were changed.
- No secrets, tokens, webhook URLs, production IDs, server IPs, or credentials were added.
- No real customer data, customer names, contact names, or production records were added.
- Local checks and relevant validation commands passed, or any limitations are clearly documented.
- The full pull request diff has been reviewed by a human.
