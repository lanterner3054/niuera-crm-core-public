# n8n Workflow Export and Sanitization Architecture

## 1. Purpose

NIUERA needs a controlled workflow export and sanitization pipeline so that n8n workflow designs can be reviewed, documented, and improved without exposing private infrastructure or customer information. n8n workflow JSON can contain credentials references, webhook paths, endpoint URLs, table identifiers, application identifiers, headers, sample payloads, and other values that are not safe for public repositories or broad review contexts.

Production workflow JSON must never be committed directly to the public repository. Any workflow content copied into this repository, shared with external AI review tools, or included in a public review pack must first pass through an explicit sanitization process and a human review.

## 2. Goals

- Export n8n workflows from the private environment using a repeatable private-repo workflow.
- Remove or replace credentials, tokens, webhook identifiers, production URLs, server IP addresses, table IDs, app IDs, customer data, contact data, and other sensitive values.
- Save sanitized workflow JSON for AI review, documentation, architecture review, and safe examples.
- Keep raw production workflow exports inside the private repository or private review packs only.
- Preserve enough high-level workflow structure to support review of node sequencing, branching, error handling, and integration boundaries.

## 3. Non-goals

- Do not deploy workflows.
- Do not modify production n8n.
- Do not write to Feishu.
- Do not send email.
- Do not expose real workflow credentials, endpoints, webhook paths, table identifiers, customer information, or internal network details.
- Do not replace production change management, incident response, or access-control procedures.

## 4. Proposed Data Flow

1. A private repository script reads `N8N_BASE_URL` and `N8N_API_KEY` from environment variables.
2. The script fetches workflow metadata and workflow JSON from the private n8n environment.
3. Raw workflow exports are stored only in a private, ignored location when explicitly requested.
4. A sanitizer walks the workflow JSON and removes or replaces sensitive fields.
5. Sanitized output is written to a local output directory.
6. A security scan runs against the exported and sanitized output.
7. A human reviewer inspects the diff and scan results before deciding whether sanitized files may be copied into the public repository or a sanitized review pack.

The intended boundary is simple: private systems may produce raw exports, but only sanitized artifacts may cross into the public repository or public review materials.

## 5. Sanitization Rules

The sanitizer should use conservative defaults. If a value is uncertain, it should be redacted.

Required rules:

- Remove `credentials` objects and credential references from all nodes.
- Redact authorization headers and any header values that may contain bearer tokens, API keys, session identifiers, or signatures.
- Redact fields whose names indicate secrets or sensitive identifiers, including names containing `password`, `secret`, `token`, `api_key`, `apikey`, `app_secret`, `webhook`, `url`, `host`, `email`, `table_id`, `tableId`, `app_token`, or `appToken`.
- Redact IP address values, internal hostnames, and production hostnames.
- Replace real webhook paths with `PLACEHOLDER_WEBHOOK_PATH`.
- Replace production URLs with `https://example.invalid`.
- Replace workflow IDs, node IDs, or execution identifiers when they are sensitive or can be correlated with production systems.
- Remove customer names, contact names, phone numbers, email addresses, addresses, message bodies, and sample payloads that contain business or personal data.
- Keep node names, node types, graph connections, high-level branching, retry configuration, and non-sensitive control-flow metadata where safe.
- Prefer stable placeholders such as `PLACEHOLDER_TOKEN`, `PLACEHOLDER_TABLE_ID`, `PLACEHOLDER_APP_ID`, and `PLACEHOLDER_CUSTOMER_VALUE` when preserving the shape of a field helps review.

## 6. Suggested File Structure

The implementation should live in the private repository first. Suggested layout:

```text
scripts/export_n8n_workflows.py
n8n/workflows-private/
n8n/workflows-sanitized/
review_packs/private/
review_packs/public/
```

Recommended ownership and git behavior:

- `scripts/export_n8n_workflows.py`: private-repo export and sanitization script.
- `n8n/workflows-private/`: raw exports; ignored by git; never copied to the public repository.
- `n8n/workflows-sanitized/`: sanitized workflow JSON intended for review.
- `review_packs/private/`: private review bundles; ignored by git; may include raw or restricted context.
- `review_packs/public/`: sanitized examples only; safe for public documentation after human approval.

## 7. Safety Controls

The export tool should be safe by default:

- Run in dry-run mode unless `--execute` is provided.
- Require `--execute` before writing any files.
- Never overwrite existing files unless `--overwrite` is provided.
- Print planned reads, planned writes, target directories, and workflow counts before writing.
- Never print full secret values, full authorization headers, full webhook paths, full production URLs, or full payload samples.
- Mask any diagnostic value that could contain a secret, showing only a short prefix or a hash when needed for troubleshooting.
- Run `security_scan.py` after export and before any publishing step.
- Fail closed when the sanitizer encounters an unknown field pattern that may contain sensitive data.
- Keep raw export directories git-ignored and outside public review packs.
- Require human diff review before copying sanitized outputs into this public repository.

## 8. Review Workflow

Recommended collaboration model:

- Codex may implement and update the private export script with strict repository boundaries and without accessing production data directly unless explicitly authorized in the private environment.
- Claude should review only sanitized output, public review packs, or architecture documents that do not include secrets or production identifiers.
- ChatGPT should guide commands, troubleshooting, review checklists, and safe operating procedures without receiving raw production workflow JSON.
- A human reviewer decides what, if anything, is copied from private sanitized outputs into the public repository.
- Any public pull request should include only documentation, sanitized examples, or tooling that has passed security scanning and human review.

## 9. Future Implementation Checklist

- Add the private export script at `scripts/export_n8n_workflows.py` in the private repository.
- Add sanitizer unit tests covering credentials, headers, webhook paths, URLs, IP addresses, app IDs, table IDs, email addresses, and representative nested node parameters.
- Add a sample sanitized workflow that uses placeholders only.
- Add documentation for manual review, including a reviewer checklist and approval criteria.
- Add a CI scan for sanitized outputs before they can be published or packaged.
- Add a release checklist for public review packs that confirms no raw exports are included.
