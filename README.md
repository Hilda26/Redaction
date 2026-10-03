# RedactionBounty

RedactionBounty is a GenLayer Intelligent Contract for privacy-preserving data
release workflows. A sponsor escrows a reward for a useful redaction of a fixed
sensitive document. Submitters propose redacted versions, and GenLayer validator
consensus decides whether a candidate removes the sensitive information required
by the policy while preserving the non-sensitive context the sponsor still needs.

## Why this needs GenLayer

Good redaction is semantic, not just syntactic. A deterministic script can match
known patterns like SSNs, but it cannot reliably decide whether a paraphrased
identifier remains identifying, whether an API key is disguised, or whether the
redaction destroyed the context that made the document useful. RedactionBounty
uses GenLayer where the judgment belongs: validators evaluate the same original
text, same policy, and same proposed redaction, then agree on a finite verdict.

## What makes it distinct

This is not a sealed-bid auction, milestone escrow, prediction market, web
oracle, drift monitor, or dispute arbiter. It is a privacy/workflow primitive:
the contract pays for the first candidate that satisfies a semantic redaction
policy. The judged result answers a bounded question about one submitted
redaction, and the deterministic half handles escrow, submission caps, replay
prevention, payout routing, retryable malformed rounds, and refund after expiry.

## Review-conscious design

- Untrusted original text, policy, and candidate text are JSON-encoded into the
  prompt as evidence-only data.
- The LLM cannot choose who gets paid or how much. It only returns a finite
  `accepted` boolean and finite `reason_code`; payout uses the stored submitter
  and escrowed reward.
- The equivalence principle binds both `accepted` and `reason_code`, avoiding an
  unbound-payload gap.
- Malformed or inconsistent verdicts mark only that submission as `ERRORED`, so
  the same candidate can be retried without locking the bounty.
- A permissionless `cancel_expired_bounty` refunds the sponsor after the fixed
  refund deadline if no acceptable redaction is awarded.
- Settlement revalidates bounty and submission state after the judged round,
  preventing stale consensus from acting over a terminal state.
- The accepted consensus timestamp is parsed and checked so it cannot precede
  bounty creation.

## Main methods

- `create_bounty(original_text, redaction_policy, reward, submit_window_seconds, refund_grace_seconds)`
- `submit_redaction(bounty_id, redacted_text)`
- `review_submission(submission_id)`
- `cancel_expired_bounty(bounty_id)`
- `get_bounty(bounty_id)`
- `get_submission(submission_id)`
- `list_submissions_for_bounty(bounty_id)`

## Verification

```powershell
genvm-lint check contracts\redaction_bounty.py --json
pytest tests\direct\ -v
```

Current local result:

- GenVM lint: passed.
- Direct tests: 13 passed.

## Deployment

- StudioNet contract address: `0x8E4876D04379A4a2D30fd045793f851A9924A152`
- Deployment transaction: `0x1db634f8dc8572ad1d3c78b1558f4f75695e6141c6436847819fe3e19abb7edc`
- Deployment receipt: `FINALIZED`, `MAJORITY_AGREE`, leader execution `SUCCESS`,
  `stderr=""`, `raw_error=null`.
- `genlayer schema 0x8E4876D04379A4a2D30fd045793f851A9924A152` succeeded.
- `genlayer code 0x8E4876D04379A4a2D30fd045793f851A9924A152` returned the
  deployed source.
- `genlayer call 0x8E4876D04379A4a2D30fd045793f851A9924A152 bounty_count`
  returned `0`.
- `genlayer call 0x8E4876D04379A4a2D30fd045793f851A9924A152 submission_count_total`
  returned `0`.
