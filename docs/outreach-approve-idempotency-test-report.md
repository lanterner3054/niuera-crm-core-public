# Outreach Approval Idempotency Test Report

Date: 2026-05-13  
Scope: sanitized manual proof-of-concept report for an inactive n8n test workflow copy.

## Scope

This public report records a sanitized manual idempotency proof-of-concept for an inactive test copy. It does not include production secrets, webhook URLs, server IPs, app IDs, table IDs, workflow IDs, record IDs, customer names, contact names, email addresses, raw payloads, or full workflow JSON.

## Environment Boundary

- Test workflow copy: inactive test copy only.
- Active production workflow: not modified.
- Test data: dummy or sanitized records only.
- Email path: dry-run send node used for the validated chain.
- Final production SMTP rollout: not confirmed in this report.

## Sanitized Tested Flow

```text
Receive approval callback
  -> Get token
  -> Read prospect/company record
  -> Read primary contact
  -> Determine action type
  -> Extract primary contact
  -> Lock Decision
  -> IF Should Attempt Lock
      True -> Update record to sending / followup-sending
            -> Re-read record
            -> Verify Lock
            -> IF Lock Confirmed
                True -> Dry Run Send
                      -> Write send log
                      -> Update company/prospect final status
                      -> Update contact final status
                False -> No-op Response
      False -> No-op Response
```

## Manual POC Results

| Test case | Expected result | Result |
|---|---|---|
| First-email normal approve | Lock confirmed, dry-run send path runs once, writeback path continues | PASS |
| Repeated first-email approve | Duplicate path reaches no-op; no send/writeback bypass | PASS |
| Simulated lock confirmation failure | Lock false branch reaches no-op; no send/writeback | PASS |
| Follow-up normal approve | Follow-up lock confirmed and dry-run send path runs | PASS |
| Follow-up approve when record is already replied / terminal | Terminal state is blocked and routed to no-op | PASS |

## Not Yet Tested / Not Yet Released

- Real SMTP send has not been confirmed as the final release path.
- Production rollout has not started.
- Active production workflow has not been modified.
- Full failure-path coverage for real email provider failure still needs a production-readiness review.
- Post-send writeback failure reconciliation still needs a human-approved operating procedure before rollout.
- Sanitized exported workflow JSON still requires sanitizer and structural checks before reviewer use.

## Release Gate Before Production

Production rollout should not proceed until all items below are satisfied:

- Final v2 workflow export is sanitized and reviewed.
- Offline checker passes against local exported workflow JSON, or WARN items are explicitly accepted by a human.
- Claude reviews only the public PR/diff or sanitized review pack.
- A human approves importing only into an inactive n8n test workflow.
- Dummy testing passes after import.
- A human approves production rollout.
- Production workflow backup/export is created under the normal release process.
- Real SMTP behavior and failure handling are reviewed separately from the dry-run POC.

## Safety Notes

- Do not commit raw n8n workflow JSON.
- Do not paste raw payloads or production identifiers into review packs.
- Do not use MCP for this GitHub/review-pack review.
- Do not enable any inactive test workflow for production without human approval.
