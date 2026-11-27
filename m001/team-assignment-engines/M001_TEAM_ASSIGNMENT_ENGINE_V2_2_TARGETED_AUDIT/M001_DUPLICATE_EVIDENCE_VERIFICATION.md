# M001 V2.2 — Duplicate Evidence Independent Verification (N-08)

**Mission:** M001-TEAM-009  
**Evidence:** `tests/results/unicode_duplicate_results.json`, `reports/UNICODE_DUP_AGENT_NOTES.md`

## Algorithm inspected

`validate_state` evidence registry loop (lines 421-441) builds:

```
signature = (evidence_type, source_ref, recording_authority, timestamp,
             subject, content_hash, role, appointment_ref, decision_ref)
```

A collision emits `E-EVIDENCE-DUPLICATE` in `evidence_integrity`. The canonical finding's recommended
tuple was the first six fields; V2.2 added three role-binding fields.

## Results (18 cases: 15 OK, 3 mismatch)

| Case | Result |
|---|---|
| exact duplicate acceptance evidence under second ID | `E-EVIDENCE-DUPLICATE` — canonical N-08 fixed |
| identical content with different evidence identifiers | flagged |
| CRLF vs LF in source_ref | not flagged (exact-string semantics; no normalisation policy) |
| NFC vs NFD source_ref | not flagged (no normalisation policy; Unicode identity residual remains open) |
| whitespace-only difference in authority | not flagged (exact-string semantics) |
| different content with identical metadata | not flagged (correctly distinct) |
| genuinely distinct role-bound acceptance evidence | not flagged (no false rejection) |
| inconsistent source metadata | not flagged by duplicate check; other checks still apply |
| ambiguous `content_hash=None` | two such records collide and are flagged (conservative) |
| canonical-tuple role / decision_ref / appointment_ref tweaks | not flagged under V2.2's 9-field signature |
| reversed insertion order | deterministic — flagged |
| evidence state before/after validation | unchanged (immutability confirmed) |
| deterministic repeat | identical |

A practical SHA-256 collision was not constructible; no evidence was discarded and provenance fields
remain in state.

## Canonical N-08

The exact reproduction from the independent register (identical evidence under `e-acc-C-P1-copy`)
is rejected with `E-EVIDENCE-DUPLICATE` and readiness NO. **Canonical N-08 is verified fixed** for
that reproduction; distinct evidence is not incorrectly rejected; signatures are deterministic.

## New residual D-03 (MEDIUM) — reproduced (3 variants)

Because `role`, `appointment_ref` and `decision_ref` are only validated for CANDIDATE_ACCEPTANCE,
not for PRODUCT_OWNER_APPROVAL, FORMAL_APPOINTMENT or ONBOARDING, an attacker can clone one such
artifact under a second ID and change only the unvalidated `role` field. The signature then differs,
no duplicate error is emitted, and `stage_b_role_ready` remains YES with zero issues:

- `EXPLOIT_one_po_artifact_two_roles`
- `EXPLOIT_one_onboarding_artifact_two_roles`
- `EXPLOIT_one_formal_artifact_two_roles`

This is the canonical N-08 harm — one underlying artifact reused for two roles — still achievable
for non-acceptance evidence. It is a new MEDIUM residual (D-03), not a reopening of the canonical
reproduction. Recommended: use the canonical six-field signature, or validate the three added
fields for all evidence types.
