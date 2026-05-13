# Contributing

This is a public sanitized collaboration repository.

## Contribution rules

1. Do not commit production secrets.
2. Do not commit real customer data.
3. Do not commit real Feishu app tokens, table IDs, API keys, webhook URLs, or server IP addresses.
4. Do not copy private repository Git history into this repository.
5. Keep all runtime values in environment variables.
6. Use example records only.

## Pull request scope

1. Each pull request should have one clear goal.
2. Prefer small pull requests with 1-3 changed files.
3. Avoid unrelated rewrites, broad refactors, or formatting-only changes.
4. Confirm the pull request only changes files that are allowed for the task.

## Required checks before merge

Before merging any pull request:

1. Confirm only allowed files changed.
2. Confirm the diff contains no secrets, tokens, webhook URLs, server IPs, table IDs, customer names, or prospect names.
3. Run:

   ```bash
   python3 scripts/security_scan.py
   ```

4. Confirm the output says:

   ```text
   No potential sensitive information found.
   ```

If the scan reports potential sensitive information, stop and resolve the issue before merge.

## Merge rules by change type

1. Documentation-only pull requests may be merged quickly if the scope is clear and the security scan is clean.
2. Script changes require more careful review before merge.
3. Changes related to the MCP server, auth, email, Feishu, n8n, Dify, or production systems require human review before merge.
4. Any change touching secrets handling, credentials, deployment, or write operations must not be auto-merged.

## Codex usage rules

Codex tasks must specify:

1. Allowed files.
2. Forbidden files.
3. Validation requirements.
4. Output requirements.

Codex must not:

1. Access production systems.
2. Modify `.env` files.
3. Force push or rewrite Git history.

## Review workflow

1. Make changes in this public repository or prepare a sanitized review pack.
2. Ask Claude or another reviewer to review only GitHub public content, the pull request diff, or the sanitized pack.
3. Do not allow MCP, server, Feishu, n8n, Dify, or production access during public code review.
4. Claude must not use MCP or production access for public repository review.
5. Apply approved patterns manually to the private production repository.

## Commit message style

Use short action-oriented messages, for example:

- Add sanitized review checklist
- Update public MCP skeleton
- Improve outreach cleanup dry-run docs
