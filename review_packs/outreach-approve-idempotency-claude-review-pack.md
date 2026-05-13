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
  - Reports PASS / WARN / FAIL.
  - Checks required lock/verification/no-op nodes.
  - Checks for send-path bypass around `IF Lock Confirmed`.
  - Checks that no-op branches do not reach send/writeback nodes.
  - Checks for potential sensitive residue without printing values.

- `scripts/sanitize_n8n_workflow.py`
  - Offline-only sanitizer for local n8n workflow JSON exports.
  - Removes credentials and execution data.
  - Redacts sensitive keys and sensitive-looking strings.
  - Does not print matched secret values.

- `docs/outreach-approve-idempotency-test-report.md`
  - Sanitized record of manual POC results.
  - Clearly distinguishes passed manual POC cases from not-yet-released production rollout.

- `review_packs/outreach-approve-idempotency-claude-review-pack.md`
  - This sanitized review pack.
  - No raw workflow JSON or production identifiers.

## Required Idempotency Properties

Claude should verify that the engineering assets support these properties:

1. A send-equivalent node must be reachable only through the `IF Lock Confirmed` true branch.
2. The blocked/no-op path must not reach any send node or writeback/send-log node.
3. Repeated approval callbacks should stop safely instead of sending again.
4. Follow-up sends should remain possible only through the intended lock path.
5. Terminal states must not be allowed to send.
6. Sanitizer/checker must not call production services.
7. Scripts must not require real workflow IDs, table IDs, webhook URLs, customer data, or credentials.
8. Any detected sensitive residue should be summarized by category/count only, not printed as full values.

## Known Limitations

- Static graph checks cannot prove all runtime conditions in n8n expressions.
- n8n branch semantics can vary by node type; the checker assumes IF-style output index `0` is the true branch.
- Writeback failure reconciliation after a real accepted email remains a release-process question, not fully solved by this script.
- Current validated send path used dry-run. Real SMTP is a separate release gate.

## Review Questions

1. Are the offline checker rules sufficient to catch obvious bypass paths?
2. Are the sanitizer rules conservative enough for Claude review packs?
3. Are the docs clear that production workflow changes remain human-controlled?
4. Are any additional static checks needed before importing into an inactive n8n test workflow?
5. Are there any unsafe assumptions about n8n connection graph semantics?
6. Is the distinction between dry-run POC and production rollout clear enough?

## Expected Review Output

Please return:

1. Approval Status
2. Critical Risks
3. Required Changes
4. Nice-to-have Improvements
5. Rollout Notes
6. Final Recommendation
