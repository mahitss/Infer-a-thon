# M001 Recommended Patch Plan

**Governance:** M001 OPEN; M002 UNAUTHORIZED; recruitment UNAUTHORIZED; field validation NOT STARTED; Research Owner ACCEPTED IN CONVERSATION; other five roles UNASSIGNED. Independent audit only: original implementation untouched, no repository/register/ADR change, no appointment, contact, storage configuration or implementation authorization.

No patch was applied to the original engine. Recommended corrections:

1. Add `E-PO-COMBINATION-REVIEW` blocking errors for unresolved discouraged combinations; require dated PO approval evidence.
2. Replace boolean-only conditional evidence with structured references (`evidence_id`, `source`, `created_at`, `approved_by`) and validate them non-empty.
3. Require explicit PO combination approval for every person holding more than one role, not only listed pairs.
4. Add `PROPOSED` to missing appointment states or require `FORMALLY_APPOINTED` for validation-complete output.
5. Require `approval.formal=true` when state is `FORMALLY_APPOINTED`; reject contradictions.
6. Validate candidate identifier uniqueness and identity against an authoritative roster; if no roster exists, keep roles UNASSIGNED.
7. Require non-empty approval basis with evidence reference and timestamps.
8. Add timestamp fields to schema and state requirements.
9. Emit explicit stage outcomes; topology PROPOSED must block Stage B readiness.
10. Detect duplicate JSON keys; catch JSON/encoding/file errors with stable codes and no tracebacks.
11. Expand independent tests to include all 16 failed adversarial checks in the original suite.
12. Re-run mutation testing after correction, including mutants for the new rules.

Priority: CRITICAL F-05 and F-08 first, then HIGH F-01–F-04, F-06, F-07, F-09, F-10, then MEDIUM/LOW.

