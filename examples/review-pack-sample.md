# Sanitized Review Pack Sample

This is an example format for sharing private repository changes with an external AI reviewer. It is a public-safe template only and must not contain production data.

Use this template by replacing each example item with sanitized excerpts from the public repository or with placeholders. The reviewer should not need access to production servers, MCP resources, private automation tools, or private datasets to complete the review.

## Review scope

Review the sanitized materials for:

- Security risks in the proposed code or documentation changes.
- Unsafe write operations, especially actions that could affect external systems.
- Missing validation, confirmation gates, or dry-run safeguards.
- Overbroad file, network, or environment access.
- Documentation clarity for safe operator and reviewer behavior.

Out of scope:

- Reading production servers, private MCP resources, Feishu, n8n, Dify, email systems, or other live infrastructure.
- Validating real customer, prospect, lead, contact, or campaign data.
- Checking real secrets, tokens, webhook URLs, app IDs, table IDs, or server addresses.
- Reconstructing private Git history or private operational context.

## Context summary

This pack describes a sanitized review scenario for the public NIUERA CRM Core repository. The reviewer should assume the pack contains only public-safe excerpts, placeholders, and fake examples.

- No production credentials are included.
- No real customer or prospect data is included.
- No real contact names, company names, webhook URLs, server IPs, table IDs, or app IDs are included.
- Any operational examples are illustrative and must not be treated as live system instructions.

## Files included

Example changed files in a sanitized pack may look like this:

- `scripts/example_check.py` — example validation logic with fake inputs.
- `docs/example-operator-note.md` — public-safe operator guidance excerpt.
- `examples/example_payload.json` — placeholder payload with fake IDs and names.
- `src/example_module.py` — representative code excerpt with all secrets and live endpoints removed.

Use fake paths or public repository paths only. Do not include private absolute paths, production host paths, or private repository locations.

## Sanitization notes

Before sharing a review pack, confirm that:

- Secrets, API keys, access tokens, session cookies, passwords, and private keys are removed or replaced with `REDACTED`.
- Endpoints, webhook URLs, production hostnames, and server IPs are removed or replaced with placeholders such as `WEBHOOK_URL_PLACEHOLDER`.
- Customer, prospect, lead, company, and contact names are replaced with placeholders such as `Example Company`, `Example Contact`, or `Customer A`.
- Table IDs, app IDs, database IDs, campaign IDs, record IDs, and internal workflow IDs are replaced with placeholders such as `TABLE_ID_PLACEHOLDER`, `APP_ID_PLACEHOLDER`, or `RECORD_ID_PLACEHOLDER`.
- Private Git history, private issue links, internal chat excerpts, and operational incident details are not included.

## Questions for reviewer

Please review the included sanitized materials and answer:

1. Are there security risks, secret-handling issues, or unsafe assumptions?
2. Could any write operation run without an explicit dry run, confirmation gate, or scoped target?
3. Is input validation missing or too weak for files, environment variables, IDs, URLs, or user-provided values?
4. Does any code or instruction allow overbroad file access, network access, environment access, or repository access?
5. Is the documentation clear enough for a reviewer to avoid production systems and use only sanitized materials?

For each finding, include the file path or excerpt label, the risk level, the reason it matters, and a suggested public-safe remediation. If no issue is found, say so explicitly.

## Reviewer restrictions

- Do not use MCP, private tools, or private resources.
- Do not access production systems, servers, Feishu, n8n, Dify, email, databases, webhooks, or private infrastructure.
- Do not infer, reconstruct, or guess private customer data, prospect data, credentials, endpoints, IDs, or operational details.
- Base the review only on this review pack and public repository content.
- If information is missing because it was sanitized, state the limitation instead of seeking private data.
