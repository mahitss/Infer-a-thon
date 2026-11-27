# M001 Independent Original Finding Closure Matrix

**Mission:** M001-TEAM-005  
**Date:** 2026-11-27  
**Independent result:** **16 CLOSED / 0 PARTIAL / 0 NOT CLOSED**  
**Evidence:** `tests/results/finding_closure_results.json`, `reports/CLOSURE_AGENT_NOTES.md`

## Method

V2's remediation matrix was read but **not** used as proof. The closure stream imported V2's
validator from its read-only path, built a schema-valid six-candidate baseline in memory
(all roles `FORMALLY_APPOINTED`, topology `APPROVED`, exact combination approvals,
timezone-aware timestamps), confirmed `stage_b_role_ready=true` with all eight dimensions
PASS, then applied one targeted mutation per finding. V1's original defects were confirmed by
running V1's validator on its own adversarial fixtures. CLI parser findings were exercised via
the real V2 CLI with `--json-only`.

## Matrix

| Finding | Severity | V1 reproduced defect | V2 source control | V2 observed result | Independent status |
|---|---|---|---|---|---|
| F-01 | HIGH | `valid=True`, warning only for RO+MODERATOR | `validator.py:421-434`; policy L13 `NOT_RECOMMENDED`, blocking `E-DISCOURAGED-RO-MODERATOR` | `E-COMBINATION-APPROVAL-MISSING`, `E-DISCOURAGED-RO-MODERATOR`; dimensions FAIL; ready=False | CLOSED |
| F-02 | HIGH | `valid=True`, warning only for DC+ANALYST | same lines; `E-DISCOURAGED-CUSTODIAN-ANALYST` | both errors; ready=False | CLOSED |
| F-03 | HIGH | boolean evidence flag accepted | `validator.py:438-445` requires verified `EVIDENCE_SEPARATION` record with exact subject | `E-COND-EVIDENCE-SEPARATION`; legacy boolean also yields `E-SCHEMA`; ready=False | CLOSED |
| F-04 | HIGH | explicit Continue/Stop boolean accepted | `validator.py:446-448` requires formal CS appointment plus exact approval | `E-COND-EXPLICIT-CS` in two independent mutations; ready=False | CLOSED |
| F-05 | CRITICAL | multi-role with no PO approval accepted | `validator.py:402-428` exact `(candidate, sorted role set)` approval map | 2 × `E-COMBINATION-APPROVAL-MISSING`; `product_owner_combination_approval` FAIL; ready=False | CLOSED |
| F-06 | HIGH | duplicate candidate identifier accepted | `validator.py:249-263`, `:386-388`, `:429-431` | `E-CANDIDATE-DUPLICATE` for registry/appointment duplicates; hard pair still `E-HARD-MODERATOR-ANALYST`; ready=False | CLOSED |
| F-07 | HIGH | unknown human reference accepted | `validator.py:333-335`, `:389-390`, `:261-262` | `E-CANDIDATE-UNKNOWN`, `E-EVIDENCE-SUBJECT`; ready=False | CLOSED |
| F-08 | CRITICAL | PROPOSED treated as appointed | policy L5-7 `formal_appointment_states=[FORMALLY_APPOINTED]`; `validator.py:327-330`, `:393-394` | `E-APPOINTMENT-MISSING`, `E-UNAPPROVED-APPOINTMENT`; ready=False | CLOSED |
| F-09 | HIGH | formal state with `approval.formal=false` | `validator.py:349-350` | `E-FORMAL-APPROVAL-MISMATCH`; ready=False | CLOSED |
| F-10 | HIGH | empty PO decision basis accepted | `validator.py:351-352`, `:343-344`, `:218-221` | `E-DECISION-EVIDENCE-EMPTY`; ready=False | CLOSED |
| F-11 | MEDIUM | no structured timestamps | `validator.py:197-210`, `:355-363`; policy L23 | `E-TIMESTAMP-MISSING`/`ORDER`/`INVALID`; ready=False | CLOSED |
| F-12 | MEDIUM | PROPOSED topology did not block Stage B | `validator.py:296-298`, `:450-452`; policy L24 | `E-TOPOLOGY-UNAPPROVED`; ready=False | CLOSED |
| F-13 | MEDIUM | duplicate JSON keys last-wins | `validator.py:25-26`, `:74-97`; CLI `:38-49` | `E-DUPLICATE-JSON-KEY`; CLI exit 2, stderr empty | CLOSED |
| F-14 | LOW | malformed JSON traceback | `validator.py:96-97` | `E-JSON-INVALID`; CLI exit 2, stderr empty | CLOSED |
| F-15 | LOW | missing file traceback | `validator.py:76-80` | `E-FILE-NOT-FOUND`; CLI exit 2, stderr empty | CLOSED |
| F-16 | LOW | invalid UTF-8 traceback | `validator.py:81-84` | `E-ENCODING-INVALID`; CLI exit 2, stderr empty | CLOSED |

## Hard incompatibilities (positive check)

With a **fully valid** exact PO approval, `MOD+ANALYST` produces `E-HARD-MODERATOR-ANALYST`
and `MOD+DATA_CUSTODIAN` produces `E-HARD-MODERATOR-CUSTODIAN`; the approval variable is not
consulted at `validator.py:429-431`. No override/waiver field exists in policy or schema.

## Policy-source versions and newly introduced interpretations

- V1 policy: version `1.0`, source = the decision pack and staffing pack; `DISCOURAGED` with
  warning codes; `accepted_formal_states` included conversation and candidate-accepted states.
- V2 policy: version `2.0`, source additionally cites the **audit defect register**;
  `NOT_RECOMMENDED` with blocking codes; `formal_appointment_states=[FORMALLY_APPOINTED]`; new
  `evidence_types`, `verification_statuses`, `timestamp_fields`, topology/combination flags.
- Authoritative charter lines 20–25 and staffing models lines 13–18, 32 use "Not recommended",
  "Unacceptable" and require explicit PO documentation. V2's `NOT_RECOMMENDED` label matches
  the source better than V1's `DISCOURAGED`; the blocking treatment is derived from the audit
  corrections, not directly from the planning packs.
- **Newly introduced interpretation (not reopening a finding):** the exact machine definition of
  a valid "Product Owner combination review" — sorted role set key, `outcome=APPROVED`, PO flag,
  non-empty rationale, timezone-aware decision timestamp, and `COMBINATION_REVIEW` evidence with
  `VERIFIED` status, 64-hex hash and `candidate:PAIRKEY` subject — is not specified by the
  authoritative packs. It is a reasonable encoding of "explicitly documented", but should be
  formally approved before being treated as governance policy. No general override mechanism
  was invented.

## Residuals (do not reopen F-01…F-16, but are recorded)

- **R-1 = N-06 (MEDIUM):** `evidence_check()` emits errors without calling `fail()`, so
  `evidence_integrity` stays PASS for forged IDs/hashes/subject mismatches.
- **R-2 (LOW):** V2 policy fields `missing_appointment_states`,
  `require_combination_approval_for_multi_role`, `evidence_fields`, `timestamp_fields` and
  `review_requirement` are declared but never read by the validator; policy `source` is partly
  self-referential.
- **R-3 (LOW):** a `REJECTED` approval suppresses the discouraged code, though
  `E-COMBINATION-APPROVAL-REJECTED` still blocks.
- **R-4 (INFO):** hard incompatibilities confirmed genuinely unoverridable.
