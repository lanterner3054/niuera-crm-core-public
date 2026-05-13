# Repository Layout

This public repository is intentionally small and sanitized. It is designed to help humans and AI coding assistants understand the public NIUERA CRM Core structure without exposing production systems, credentials, customer data, or private implementation details.

## Top level

README.md
Project overview and public repository purpose. Documentation updates may mention this file only when a task explicitly allows it.

.env.example
Non-secret environment variable template. It must contain placeholders only, never real keys, tokens, webhook URLs, table IDs, server IPs, customer names, or contact names.

CONTRIBUTING.md
Rules for public collaboration.

LICENSE
Open-source license for this sanitized public repository.

## docs

Public documentation only. This directory may describe the sanitized architecture, AI collaboration rules, security policy, repository layout, and sanitization checklist.

architecture-public.md
High-level architecture without production identifiers.

ai-collaboration.md
Rules for ChatGPT, Codex, and Claude collaboration.

security-policy.md
Public repository security boundaries.

claude-review-prompt.md
Prompt template for Claude reviews.

sanitization-checklist.md
Checklist before publishing code or review packs.

repo-layout.md
This file.

## scripts

Sanitized helper scripts only. Scripts must not contain production credentials, production endpoints, real customer data, or private integration details.

Scripts must use environment variables for configurable values. When a script can perform write operations, destructive operations, or external updates, it must default to dry-run behavior unless a human explicitly enables writes.

check_email.py
Sanitized example of email ingestion logic using environment variables.

outreach_cleanup.py
Sanitized example of dry-run-first cleanup logic using fictional records.

security_scan.py
Local public-repo safety scan for obvious secrets or unsafe placeholders.

## mcp-server

Public MCP skeleton only. The production MCP implementation is not included in this repository.

This directory must not contain production tool logic, production credentials, private server details, real webhook URLs, or access to production systems.

## examples

Sanitized review pack examples only. Files in this directory must not include real customer names, prospect names, endpoint URLs, credentials, webhook URLs, table IDs, server IPs, or contact details.

review-pack-sample.md
Fictional review pack sample for public review workflows.

## What Codex may modify

- Documentation tasks: `docs/` or `README.md`, only when the user request explicitly allows those files.
- Script tasks: `scripts/` only when the user request explicitly allows script changes.
- MCP tasks: `mcp-server/` only when the user request explicitly allows MCP skeleton changes.

## What Codex must not modify without explicit human approval

- `.env` or any file containing real environment values.
- Deployment files or infrastructure configuration.
- Authentication, authorization, or security-sensitive logic.
- Production integration logic for Feishu, n8n, Dify, MCP Server, email, or other external systems.
- Git history, including rebases, resets that discard work, force pushes, or history rewrites.
