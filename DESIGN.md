# RedactionBounty Design Notes

## Core flow

1. The sponsor creates a bounty and escrows the full reward.
2. The sponsor publishes a non-sensitive evidence brief, a fixed redaction
   policy, and a source commitment instead of the protected source text.
3. Submitters provide redacted versions derived from the committed source.
4. Anyone may call `review_submission` on a pending or errored submission.
5. A single GenLayer judged round decides whether that candidate satisfies the
   fixed redaction policy.
6. If accepted, the contract pays the stored submitter the stored reward and
   moves the bounty to `AWARDED`.
7. If rejected, the candidate is marked `REJECTED` and the bounty stays open.
8. If the bounty never awards, anyone may trigger sponsor refund after the fixed
   refund deadline.

## Equivalence principle

The judged output is deliberately small:

```json
{"accepted": true, "reason_code": "POLICY_SATISFIED"}
```

or

```json
{"accepted": false, "reason_code": "<finite rejection code>"}
```

Validators compare both fields exactly. The reason is not free-form prose; it is
a finite code from:

- `POLICY_SATISFIED`
- `LEAKS_SENSITIVE_INFO`
- `LOSES_REQUIRED_CONTEXT`
- `NOT_MEANINGFULLY_REDACTED`
- `MALFORMED_REDACTION`

This avoids the class of review issue where validators agree on a top-level
verdict but store or act on an associated payload that was not equivalence-bound.

## Consequence boundary

The model cannot set an address, amount, bounty id, or submission id. The only
state transition driven by consensus is accepted versus rejected for the
already-selected submission. If accepted, payout uses:

- `submission.submitter`
- `bounty.reward`

Both are committed on-chain before the judged round begins.

## Protected source handling

The raw protected source is deliberately not a contract input and is never saved
or returned by any view method. The sponsor publishes:

- `evidence_brief`: non-sensitive facts/classes/required context sufficient for
  validators to assess candidates under the fixed policy.
- `source_commitment`: a compact public commitment, such as a SHA-256 digest of
  the protected source or source package, binding the bounty to the off-chain
  material without disclosing it.
- `redaction_policy`: the fixed policy validators apply to every candidate.

The evidence brief, policy, commitment, and candidate redaction are still
adversarial input. They may contain instructions, JSON-looking snippets, or
attempts to tell the model what to return. The contract serializes them with
`json.dumps(..., sort_keys=True)` into an evidence object and tells validators
that every field value is data, not instructions.

## Failure and exit behavior

Malformed or inconsistent model output does not pay anyone and does not terminally
break the bounty. It marks the submission `ERRORED`, allowing a retry. If no
candidate is accepted, `cancel_expired_bounty` refunds the sponsor after the
immutable refund deadline. The refund is permissionless to trigger but always
paid to the original sponsor.

## Corrections carried forward

- Finite, equivalence-bound verdict payload.
- State revalidation after the judged round.
- Consensus timestamp parsing and creation-time lower bound.
- Prompt-injection-resistant treatment of untrusted text as evidence.
- No raw protected source in public storage, public getters, or bounty creation
  calldata.
- No model-controlled payout amount or recipient.
- Bounded sponsor exit if consensus cannot produce an accepted redaction.
