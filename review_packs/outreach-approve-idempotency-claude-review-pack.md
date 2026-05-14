# Claude Review Pack: Outreach Approval Idempotency Engineering

Date: 2026-05-13  
Audience: Claude Code / architecture reviewer  
Review mode: public GitHub PR diff or this sanitized review pack only.

## Reviewer Restrictions

Claude must not:

- call MCP tools,
- read server files,
- access n8n, Feishu, Dify, SMTP, IMAP, MCP Server, `.env`, or production data,
- inspect raw workflow JSON,
- request or print real IDs, tokens, webhook URLs, server IPs, customer names, contact names, emails, or full payloads.

Claude should review only:

- this public GitHub PR diff,
- sanitized documentation,
- sanitized local-check script behavior,
- sanitized test report.

## Change Intent

A manual UI proof-of-concept for the Outreach approval callback idempotency patch was completed in an inactive test copy. This public review package exposes only sanitized engineering assets for external AI review.

Desired future workflow:

```text
Codex scripts/docs/review pack
  -> public GitHub PR for Claude review
  -> Claude reviews diff or sanitized review pack
  -> Human approval
  -> private repo / inactive n8n test workflow application
  -> Dummy testing
  -> Human production rollout approval
```

## Proposed Files for Review

- `scripts/check_n8n_outreach_idempotency.py`
  - Offline-only checker for a local exported n8n workflow JSON file.
  - No network access.
  - Reports PASS / WARN / FAIL, with optional `--strict` to make WARN return non-zero.
  - Uses public generic required node names by default, with `--required-node` overrides for private workflow naming.
  - Supports multiple lock-confirmed gates through `--lock-gate-pattern`.
  - Requires lock-attempt and lock-confirmed gates to be native n8n IF nodes before assuming output index `0` is the true branch.
  - Checks for send/writeback bypass around confirmed-lock true branches.
  - Checks that no-op and blocked branches do not reach send/writeback nodes.
  - Checks for potential sensitive residue without printing values.

- `scripts/sanitize_n8n_workflow.py`
  - Offline-only sanitizer for local n8n workflow JSON exports.
  - Removes credentials and execution data.
  - Redacts sensitive keys and sensitive-looking strings.
  - Preserves generic workflow/node `name` fields so the sanitized output remains structurally reviewable.
  - Provides `--summary-format aggregate` to avoid printing redacted key names.
  - Does not print matched secret values.
  - Sanitized JSON is intended for human/AI review and offline structural checks, not direct production import.

- `docs/outreach-approve-idempotency-test-report.md`
  - Sanitized record of manual POC results.
  - Marks POC passes as `PASS (dry-run)`.
  - Clearly distinguishes passed manual POC cases from not-yet-released production rollout.
  - Calls out repeated follow-up callback idempotency and private `Verify Lock` semantics as pre-rollout requirements.

- `review_packs/outreach-approve-idempotency-claude-review-pack.md`
  - This sanitized review pack.
  - No raw workflow JSON or production identifiers.

## Required Idempotency Properties

Claude should verify that the engineering assets support these properties:

1. A send-equivalent node must be reachable only through a native IF lock-confirmed true branch.
2. The blocked/no-op path must not reach any send node or writeback/send-log node.
3. Repeated approval callbacks should stop safely instead of sending again.
4. Follow-up sends should remain possible only through the intended lock path.
5. Terminal states must not be allowed to send.
6. Sanitizer/checker must not call production services.
7. Scripts must not require real workflow IDs, table IDs, webhook URLs, customer data, or credentials.
8. Any detected sensitive residue should be summarized by category/count only, not printed as full values.

## Known Limitations

- Static graph checks cannot prove all runtime conditions in n8n expressions.
- The checker now validates native IF node type before applying IF output-index semantics, but non-IF Switch/custom gate designs still require manual review or explicit checker extension.
- Sanitized JSON is not intended for direct production import, especially because opaque IDs may be redacted.
- Writeback failure reconciliation after a real accepted email remains a release-process question, not fully solved by this script.
- Current validated send path used dry-run. Real SMTP is a separate release gate.
- Private release notes still need to define the production `Verify Lock` semantics without exposing those details publicly.

## Review Questions

1. Are the offline checker rules sufficient to catch obvious bypass paths?
2. Are multiple lock-confirmed gates handled safely enough for first-email and follow-up designs?
3. Are the sanitizer rules conservative enough while preserving node names for review/checker use?
4. Are the docs clear that production workflow changes remain human-controlled?
5. Are any additional static checks needed before importing into an inactive n8n test workflow?
6. Is the distinction between dry-run POC and production rollout clear enough?

## Expected Review Output

Please return:

1. Approval Status
2. Critical Risks
3. Required Changes
4. Nice-to-have Improvements
5. Rollout Notes
6. Final Recommendation
