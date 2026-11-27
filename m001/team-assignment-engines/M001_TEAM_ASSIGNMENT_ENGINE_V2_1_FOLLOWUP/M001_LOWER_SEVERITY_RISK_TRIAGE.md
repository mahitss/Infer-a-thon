# M001 V2.1 — Lower-Severity Risk Triage

**Mission:** M001-TEAM-007  
**Source:** unchanged `V2_REAUDIT/M001_FINAL_DEFECT_REGISTER.json`  
**Evidence:** `analysis/lower_severity_triage.json`, `reports/TRIAGE_AGENT_NOTES.md`

All 24 carried-forward findings (17 MEDIUM, 7 LOW) were examined. Original severities were
preserved; no finding was automatically closed. Only S-03 was independently verified closed
(incidentally by the N-15 fix); it remains listed at its original severity.

## Classification summary

| Class | Meaning | Count | IDs |
|---|---|---|---|
| A | Must fix before Stage B readiness | 4 | N-04, N-08, N-11, N-12 |
| B | Must fix before recruitment authorization | 0 | — |
| C | Must fix before field validation | 0 | — |
| D | Acceptable residual with documented rationale | 14 | N-05, N-06, S-01, S-03, S-04, S-05, S-06, S-07, N-16, N-17, N-18, N-19, N-20, N-21 |
| E | Still requires investigation | 6 | N-07, N-09, N-10, N-13, N-14, S-02 |

## Complete finding mapping

| ID | Sev | Component | V2.1 behaviour | Reproduced | Stage B? | Confidentiality/authorization? | Class | Blocks ops? |
|---|---|---|---|---|---|---|---|---|
| N-04 | MEDIUM | engine/validator.py (onboarding readiness gate); schemas/team_assignment.schema.json (esca… | Unchanged from V2. engine/validator.py:475-476 still tests `if not rec.get('escalation',{}).get('contact')`, so any non-empty string, including '   ',… | reproduced | yes — a role with no substantive escalation contact is reported Stage B ready (independent probe: ready=True, … | authorization integrity yes (a readiness claim is emitted without the required contact); confidentiality no. | A | yes |
| N-05 | MEDIUM | engine/validator.py (pair_key, combination approval map); schemas/team_assignment.schema.j… | Unchanged. pair_key() at validator.py:256-257 uses '+'.join(sorted(set(roles))), so ['RESEARCH_OWNER','CONTINUE_STOP_OWNER','CONTINUE_STOP_OWNER'] col… | reproduced | yes technically (ready=True) but not materially: set semantics mean the exact two-role combination is still ap… | no — the effective approval is bound to the same exact role pair; this is record hygiene, not an authorization… | D | no |
| N-06 | MEDIUM | engine/validator.py (evidence_check vs fail/dimension bookkeeping) | Unchanged. evidence_check() (validator.py:260-300) appends Issue objects directly via issues.append(), bypassing fail() at 368-371 which is the only p… | reproduced | no — the blocking error still forces stage_b_role_ready=False; only the per-dimension display is wrong. | no — readiness and both authorization flags stay fail-closed; the impact is misdiagnosis/triage error, not an … | D | no |
| N-07 | MEDIUM | engine/validator.py (evidence_check hash regex; registry loop); schemas/team_assignment.sc… | Unchanged. validator.py:296-299 only checks re.fullmatch(r'[0-9a-fA-F]{64}', str(h)) for referenced evidence; there is no recomputation from source_re… | reproduced | yes — both mutations returned ready=True; a referenced hash that does not correspond to its source cannot be d… | authorization integrity conditional yes — if content_hash is intended as an authenticity anchor, forged eviden… | E | yes |
| N-08 | MEDIUM | engine/validator.py (evidence registry, evidence_check, acceptance decision_ref guard) | Partially addressed only for CANDIDATE_ACCEPTANCE. V2.1 added decision_ref plus a cross-appointment reuse guard at validator.py:325-335 and ID/key con… | reproduced | yes — independent probes produced stage_b_role_ready=True with one underlying approval/onboarding artifact reu… | authorization integrity yes — distinct per-role evidence can be simulated by copying one record, weakening the… | A | yes |
| N-09 | MEDIUM | engine/validator.py (evidence_check timestamp validity); schemas/team_assignment.schema.js… | Unchanged in substance. validator.py:290-292 only calls valid_timestamp() (240-247: ISO parse plus timezone awareness); there is no comparison with th… | reproduced | yes — 1999 evidence satisfies a 2026 appointment and readiness stays True. | authorization integrity conditional yes — backdated evidence can support a decision it could not have informed… | E | yes |
| N-10 | MEDIUM | engine/validator.py (role timestamp checks and ordering); policy/role_constraints.json (no… | Unchanged. validator.py:456-464 validates presence/timezone-awareness and ordering ts_a <= ts_p <= ts_f, but has no maximum age or expiry concept; com… | reproduced | yes — arbitrarily stale acceptance/approval timestamps still produce ready=True. | authorization integrity conditional yes — an obsolete consent or approval can be presented as current; require… | E | yes |
| N-11 | MEDIUM | engine/validator.py (role decision vs combination decision timestamps) | Incidentally untouched by the N-15 fix. validator.py:463-464 does enforce ts_a <= ts_p <= ts_f for per-role timestamps, but the combination decision_t… | reproduced | yes — an internally contradictory sequence (approval before acceptance) is reported Stage B ready. | authorization integrity yes — the multi-role approval can predate the consent it depends on; this is derivable… | A | yes |
| N-12 | MEDIUM | engine/validator.py (candidate_registry_check; evidence reference gate) | Unchanged for candidate references. validator.py:344-346 checks `ref != key or not ref`, and '   ' is truthy, so a registry entry keyed and referenced… | reproduced (with a fully consistent mutation; the shipped ha… | yes — a role can be reported ready against a candidate identity consisting only of whitespace. | authorization integrity yes — the identity gate is satisfiable without a real candidate identifier; confidenti… | A | yes |
| N-13 | MEDIUM | engine/validator.py (candidate_registry_check); policy/role_constraints.json (no identity … | Unchanged and explicitly declared OPEN_LIMITATION in the register. candidate_registry_check (validator.py:338-352) detects only exact duplicate candid… | reproduced (code-level limitation; harness ID-07 is blocked … | yes in principle — distinct aliases for one human can evade the multi-role combination approval and hard-incom… | authorization integrity yes — role-compatibility/combination-approval gates can be bypassed by alias splitting… | E | yes |
| N-14 | MEDIUM | engine/validator.py (evidence_check revocation); schemas/team_assignment.schema.json (evid… | Partially improved by the N-03 fix. V2.1 schema lines 70-71 declare evidence.revoked/revoked_at and validator.py:278-280 emits E-EVIDENCE-REVOKED when… | partially reproduced — evidence-level revocation is now hand… | no for the residual part — unsupported fields are rejected, so no revoked decision currently produces ready=Tr… | authorization integrity partial — a formally revoked role decision cannot be represented or evaluated, so a su… | E | yes |
| S-01 | MEDIUM | schemas/team_assignment.schema.json; engine/validator.py (schema construction, valid_times… | Unchanged. Schema lines 64, 79, 89, 99, 107, 141 still declare timestamp fields as ['string','null'] with no format/pattern; $id remains relative (lin… | reproduced | no — the naive value used in the probe is in an ungated field; all readiness-relevant timestamps are still req… | no — no false readiness and both authorization flags remain NO; the impact is schema-level diagnostic fidelity… | D | no |
| S-02 | MEDIUM | schemas/team_assignment.schema.json (content_hash); engine/validator.py (evidence_check vs… | Unchanged and overlapping N-07. Schema line 62 types content_hash as ['string','null'] with no pattern. The 64-hex regex exists only in evidence_check… | reproduced | yes technically — an unreferenced record with a malformed hash does not block readiness; however unreferenced … | authorization integrity conditional yes for the referenced-hash facet (see N-07); no additional impact for the… | E | yes |
| S-03 | MEDIUM | engine/validator.py (structural_schema_errors, schema exception tuple, terminal schema han… | Incidentally fixed by the N-15 remediation and independently verified here. validator.py:24-40 builds _SCHEMA_EXCEPTION_TYPES including referencing Po… | verified_closed | no — the failure is now fail-closed with readiness NO; pre-fix it crashed without ever producing a positive re… | no — no positive authorization can be inferred from a schema error before or after the fix; confidentiality no… | D | no |
| S-04 | MEDIUM | engine/validator.py (validate_schema fallback; structural_schema_errors path selection) | Source unchanged. validate_schema (validator.py:144-209) still supports only $ref, type, required, properties, additionalProperties, enum and items. D… | reproduced (latent — direct calls to the fallback reproduce … | no in the current environment — full Draft 2020-12 validation is active for every CLI/validator call; readines… | no currently; authorization integrity would be at risk only if the engine were deployed without jsonschema; co… | D | no |
| S-05 | LOW | engine/validator.py (evidence_check vs evidence registry loop) | Partially fixed by N-03. validator.py:275-277 now emits E-EVIDENCE-ID-MISMATCH when a referenced record's evidence_id field differs from the registry … | partially reproduced — original E06 unreferenced mismatch st… | no for the residual part — an unreferenced inconsistent record cannot support any appointment; referenced inco… | no — no false readiness path remains for referenced evidence; confidentiality no. | D | no |
| S-06 | LOW | schemas/team_assignment.schema.json (line 3) | Unchanged: $id is still the bare token 'm001-team-assignment-state-v2'. All $refs are local '#/$defs/...' strings resolved by validator.py:152-160 (su… | reproduced (static property; local-only resolution confirmed… | no — no reference resolution depends on an absolute base URI in the shipped schema. | no — no external fetch or identity/authorization effect; confidentiality no. | D | no |
| S-07 | LOW | schemas/team_assignment.schema.json (lines 42-43, 131); engine/validator.py (appointment d… | Partially improved. Appointment duplicates are now explicitly rejected by validator.py:479-489 (E-CANDIDATE-DUPLICATE), which was already present in V… | partially reproduced — combination-approval duplicates still… | yes technically (ready=True with a duplicated approval) but not materially — the duplicate carries identical d… | no — no false approval is produced by the duplicate itself; confidentiality no. | D | no |
| N-16 | MEDIUM | cli/validate.py (exception tuple); engine/validator.py (load_json_strict) | Unchanged. cli/validate.py:38-49 catches only (DuplicateKeyError, ValueError); engine/validator.py:110-133 calls json.loads at line 129 with no depth … | reproduced | no — the process fails closed with no readiness claim; the defect is output/exception handling only. | no — no data is written and no authorization is inferred; availability of diagnostics is degraded; confidentia… | D | no |
| N-17 | MEDIUM | cli/validate.py (print path); engine/validator.py (human_report, json_result, loader) | Unchanged. cli/validate.py:57 prints the raw human report; human_report (validator.py:568-585) interpolates unescaped field values; json_result (588-5… | reproduced | no — fails closed before any readiness claim reaches stdout; the structured --json-only path is unaffected. | no — no authorization effect; the raw value originates in caller-supplied input; confidentiality no (no new di… | D | no |
| N-18 | LOW | cli/validate.py (path resolution); engine/validator.py (load_json_strict) | Unchanged apart from ROOT now pointing at V2.1. cli/validate.py:8-9, 33-36 resolve a relative --state as ROOT / state_path and report only state_path.… | reproduced (documented read-only limitation) | no — path anchoring does not change validation logic; the outside-root state still failed validation normally. | no — read-only, deterministic, basename-only echo; no write or authorization effect; confidentiality no. | D | no |
| N-19 | LOW | engine/validator.py (load_json_strict OSError handler); cli/validate.py (code mapping) | Unchanged. validator.py:113-116 catches every OSError and raises ValueError('E-FILE-NOT-FOUND: %s' % exc.__class__.__name__); cli/validate.py:46-49 de… | reproduced | no — clean exit 2 with readiness NO for all these input errors. | no — diagnostic message quality only; confidentiality no. | D | no |
| N-20 | LOW | engine/validator.py (no_dupes object_pairs_hook) | Unchanged. validator.py:121-126 raises DuplicateKeyError('E-DUPLICATE-JSON-KEY: %s' % k) with only the key name; no loc/path is threaded through json.… | reproduced | no — duplicate keys are still rejected cleanly with exit 2 and readiness NO. | no — triage/diagnostic quality only; confidentiality no. | D | no |
| N-21 | LOW | policy/role_constraints.json; engine/validator.py | Partially improved but reproduced. V2.1 consumes roles, appointment_states, formal_appointment_states, evidence_types, verification_statuses, stage_b_… | reproduced | no — the unused fields are declarative; all corresponding behavior is enforced by equivalent hardcoded conditi… | no — no authorization path is altered; the risk is drift between documented policy and enforced policy; confid… | D | no |

## A-class findings (block Stage B readiness)

### N-04 — Whitespace-only escalation contact accepted

- Severity: MEDIUM (unchanged)
- Component: engine/validator.py (onboarding readiness gate); schemas/team_assignment.schema.json (escalation.contact)
- Reproduction: reproduced
- Stage B impact: yes — a role with no substantive escalation contact is reported Stage B ready (independent probe: ready=True, 0 issues); this misstates the onboarding dimension and the aggregate readiness flag.
- Recommended resolution: Apply meaningful_text() to escalation.contact in validator.py:475-476 (emit E-ESCALATION-CONTACT for whitespace/non-string), add minLength/pattern or a dedicated format to schema line 119, and add a regression case equivalent to harness ST-10.

### N-08 — Duplicate evidence records under different IDs are not detected

- Severity: MEDIUM (unchanged)
- Component: engine/validator.py (evidence registry, evidence_check, acceptance decision_ref guard)
- Reproduction: reproduced
- Stage B impact: yes — independent probes produced stage_b_role_ready=True with one underlying approval/onboarding artifact reused for two roles.
- Recommended resolution: Add registry-level duplicate detection over the semantic tuple (evidence_type, source_ref, recording_authority, timestamp, subject, content_hash) and emit E-EVIDENCE-DUPLICATE; extend role binding (subject/evidence fields) to PRODUCT_OWNER_APPROVAL, FORMAL_APPOINTMENT and ONBOARDING, not only CANDIDATE_ACCEPTANCE.

### N-11 — Combination decision timestamp is not ordered against candidate acceptance

- Severity: MEDIUM (unchanged)
- Component: engine/validator.py (role decision vs combination decision timestamps)
- Reproduction: reproduced
- Stage B impact: yes — an internally contradictory sequence (approval before acceptance) is reported Stage B ready.
- Recommended resolution: Extend the ordering check to compare each combination approval decision_timestamp with max(candidate_accepted_at) for every held role, emitting E-COMBINATION-APPROVAL-TIMESTAMP-ORDER, and add ST-03 to the regression suite.

### N-12 — Whitespace-only candidate reference accepted

- Severity: MEDIUM (unchanged)
- Component: engine/validator.py (candidate_registry_check; evidence reference gate)
- Reproduction: reproduced (with a fully consistent mutation; the shipped harness mutation is blocked only incidentally by N-03 evidence binding)
- Stage B impact: yes — a role can be reported ready against a candidate identity consisting only of whitespace.
- Recommended resolution: Apply meaningful_text() to candidate_ref in candidate_registry_check (validator.py:344-346) and to role/appointment/combination_approvals candidate_ref, emitting E-CANDIDATE-REF-INVALID, plus a schema minLength/pattern; add the fully consistent mutation as a regression case.

## Verified closure / incidental improvements

- Verified closed: S-03
- Incidental partial improvements (not closure): N-14, S-05, S-07, N-21, N-12 (harness mutation only)
- All findings kept open except S-03: True

## New follow-up finding

- F-007 (MEDIUM, class A): invisible Unicode format characters (U+200B, U+200E, U+2060)
  satisfy `meaningful_text()` because `str.strip()` does not remove them. Independently
  reproduced on V2.1: approval basis of repeated U+200B yields Stage B YES with zero issues.
  Recommended: require at least one visible/alphanumeric character (reject Unicode categories
  Cc/Cf/Zs/Zl/Zp-only strings) in `meaningful_text()` and combine with `strip()`.

