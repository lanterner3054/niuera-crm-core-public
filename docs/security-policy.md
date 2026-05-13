# Security Policy

## Public repository rule

This repository is public and sanitized. It must not contain production secrets, real customer data, production endpoints, or operational credentials.

## Never commit

Never commit any of the following content to this repository:

- API keys
- passwords
- tokens
- webhook URLs
- server IPs
- Feishu app IDs, table IDs, app tokens, or app secrets
- n8n, Dify, MCP, SMTP, or IMAP credentials
- real customer, prospect, contact, or company data
- private keys or SSH keys
- `.env` files
- private Git history

## Allowed content

The following content is allowed when it is safe for a public repository:

- placeholder values
- sanitized examples
- public documentation
- skeleton code without production logic
- scripts that read configuration from environment variables

## Secret handling

All runtime values must be loaded from environment variables. Do not hard-code credentials, endpoints, or production identifiers in tracked files.

## If a secret is found

If a suspected secret or sensitive value is found:

- do not print the full secret in issues, PR comments, logs, screenshots, or review notes
- remove it from the working tree
- rotate the affected credential if it was pushed
- consider rewriting public Git history only if sensitive content was published
- document the incident without repeating the secret value

## Git history rule

This repository starts from a clean public history. It must not be created by pushing the private repository history.

## AI collaboration safety

AI-assisted work must stay within public-repository boundaries:

- Codex must not access production systems
- Claude reviews should use PR diffs, public repository content, or sanitized review packs only
- MCP or production access must not be used for public repository review

## Review pack rule

If a diff references removed secrets, it must be sanitized before being shared with external reviewers.

## Required scan

Run the following command before merging:

```bash
python3 scripts/security_scan.py
```

Merge only if it reports:

```text
No potential sensitive information found.
```
