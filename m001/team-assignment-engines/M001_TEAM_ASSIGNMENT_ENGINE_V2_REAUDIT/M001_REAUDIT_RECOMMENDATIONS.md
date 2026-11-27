# M001 Independent Re-Audit Recommendations

**Mission:** M001-TEAM-005  
**Date:** 2026-11-27  
**Status:** recommendations only — this audit did not modify V1, V2, the previous audit, the repository, registers, ADRs, candidate records or governance statuses.

## Required before V2 may be treated as a trustworthy governance control

1. **Reject whitespace-substantive approvals (HIGH, N-01/N-02).** Replace `if not appr.get('basis')` (`validator.py:351`) and `if not ca.get('rationale')` (`:414`) with a check that requires at least one non-whitespace character, e.g. `isinstance(v, str) and bool(v.strip())`. Add regression cases for `"   "`, `"\t\n"` and Unicode whitespace.
2. **Bind evidence to the role it supports (HIGH, N-03).** Change the `subject` convention for `CANDIDATE_ACCEPTANCE`, `PRODUCT_OWNER_APPROVAL`, `FORMAL_APPOINTMENT` and `ONBOARDING` evidence to `<candidate_ref>:<role>` (or add an explicit `role` field and schema-require it), and verify that every role's evidence reference resolves to that role's subject. Re-test the two-role candidate currently served by one record.
3. **Fail closed on evidence that cannot be verified (MEDIUM, N-07–N-09).** Require `content_hash` for records with a content-bearing `source_ref`; verify the hash against an authoritative content source outside the state document; reject evidence whose timestamp predates its source or the decision it supports; reject duplicate evidence content under multiple IDs.
4. **Add temporal coherence (MEDIUM, N-10/N-11).** Define and enforce freshness/expiry policy for acceptance, approval, combination decision and formal appointment, and require `candidate_accepted_at <= combination.decision_timestamp <= formal_appointed_at` for multi-role appointments.
5. **Correct dimension reporting (MEDIUM, N-06).** Route every `evidence_check()` issue through the same `fail()` helper used by the global evidence loop so `evidence_integrity` is `FAIL` whenever an evidence error exists. Add a regression asserting dimension/status consistency for unknown IDs and subject mismatches.
6. **Reject malformed identity references (MEDIUM, N-12).** Require candidate refs to be non-empty after trimming, to match a stable canonical form, and to reject case-only or Unicode-normalization-equivalent duplicates. Decide whether a canonical identity linkage/alias model is needed so one human cannot be split into several refs to evade combination approval (N-13).
7. **Harden schema semantics (MEDIUM, schema findings).** Declare `pattern` for `content_hash`, `minLength`/pattern for basis/rationale/contact, and `uniqueItems` for `combination_approvals.roles`; supply a `FormatChecker` and add `format: date-time` only if a date-time checker is installed (otherwise keep lexical validation in the engine and document it). Catch reference-resolution exceptions, not only `SchemaError` (S-03). Treat the fallback subset as documentation-only, or implement the missing keywords before relying on it (S-04).
8. **Define revocation/history semantics (MEDIUM, N-14).** Add explicit `revoked`, `revoked_at` and append-only decision history to the schema and enforce them, rather than silently rejecting such properties as unknown.

## Governance recommendations

- Keep M001 OPEN, M002 UNAUTHORIZED, recruitment UNAUTHORIZED and field validation NOT STARTED. Nothing in this audit changes those statuses.
- Keep Research Owner `ACCEPTED_IN_CONVERSATION`; do not promote without formal evidence; do not infer Continue/Stop authority; do not invent identities.
- Do not treat any synthetic fixture as evidence of an actual appointment.
- Require a fresh independent re-audit after remediation. V2's own green test suite is not sufficient evidence.

## Acceptance criteria for the next audit

- All HIGH findings above closed with source-level changes and independently reproduced tests.
- All MEDIUM findings either closed or explicitly accepted by the Product Owner with a written risk decision and a compensating control outside the engine.
- Independent mutation testing shows no surviving security mutation, including mutations that specifically disable the newly added checks.
- Current-state validation still reports Stage B NOT READY and both authorizations NO.
- V1, the previous audit and the repository remain unchanged.
