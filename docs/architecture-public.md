# Public Architecture Overview

NIUERA CRM Core is a lightweight CRM automation system for EV charging infrastructure export workflows. This document describes the sanitized public architecture context so ChatGPT, Codex, Claude, and human reviewers can discuss the system without access to production servers, MCP, Feishu, n8n, Dify, email accounts, or operational data.

## Repository Role

This public repository is a sanitized collaboration layer. It is not the production deployment repository.

It may contain:

- Public architecture and collaboration documentation.
- Skeleton code used to explain interfaces and review expectations.
- Sanitized helper scripts that do not include live credentials or endpoints.
- Review templates and guardrails for public pull requests.

It must not contain production identifiers, credentials, customer records, private workflow exports, live endpoints, server IP addresses, table IDs, tokens, webhooks, contact names, or customer names.

## High-Level System Map

- **Feishu Bitable**: Business data source and CRM table layer.
- **n8n**: Automation workflow layer for controlled business processes.
- **Dify**: AI workflow and agent layer used for generation, classification, or analysis tasks.
- **MCP Server**: Read-only context bridge and tooling layer for controlled private environments.
- **Email scripts**: Inbound and outbound email automation helpers.
- **GitHub**: Collaboration, review, CI, and AI handoff center.
- **Production server**: Runtime environment for the stable private implementation only.

## Data Flow Overview

- Customer and prospect data is stored in Feishu Bitable in the private operating environment.
- n8n reads from and writes to Feishu through controlled workflows.
- n8n calls Dify when AI generation, classification, or analysis is required.
- Email scripts forward sanitized events into automation workflows and support outbound automation tasks.
- MCP tools provide controlled context access in private environments only.
- GitHub is used for review, documentation, and sanitized collaboration artifacts.
- This public repository must never contain production data, live endpoints, credentials, customer records, or private workflow exports.

## Public vs Private Boundary

The public repository may contain:

- Sanitized examples and placeholder configuration patterns.
- Public documentation for architecture, collaboration, and review process.
- CI and pull request guardrails that can run safely without production access.
- Skeleton MCP tools and helper scripts that demonstrate structure without exposing private implementation details.

The private implementation may contain:

- Production scripts and real workflow exports.
- Deployment details and runtime configuration.
- Credentials stored outside git in approved secret-management locations.
- Operational data, internal identifiers, and private integration details.

The production server syncs only reviewed, stable private changes. Public repository content should be treated as documentation and collaboration context, not as deployable production code.

## Module Boundaries

- **docs/**: Public architecture, collaboration, security, sanitization, and review documentation.
- **scripts/**: Sanitized helper scripts only; no production secrets, live endpoints, or operational data.
- **mcp-server/**: Skeleton placeholder for public review only; not a live production MCP server.
- **examples/**: Sanitized review pack examples and placeholder artifacts.
- **.github/**: Public CI workflows, pull request templates, and repository guardrails.

## Architecture Review Rules

- Claude should review public repository content, pull request diffs, or sanitized review packs only.
- Codex should work in small, scoped tasks with clear file boundaries and explicit validation steps.
- ChatGPT should guide operations, explain commands, and help reason about architecture using sanitized context.
- No AI tool should access production systems, production data, Feishu, n8n, Dify, MCP Server, email accounts, or live infrastructure when reviewing this public repository.
- Reviews should flag any accidental inclusion of secrets, identifiers, live endpoints, customer data, or private workflow details.

## Future Architecture Work

Potential future work should preserve the public/private boundary and use sanitized artifacts for review:

- n8n workflow export and sanitization pipeline.
- Private-to-public sanitized sync process.
- MCP permission tightening and clearer read-only access rules.
- Outreach idempotency hardening for automation workflows.
- Email bounce classification improvements.
