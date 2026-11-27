# M001 V2.2 — Remaining Finding Triage

**Mission:** M001-TEAM-009  
**Evidence:** `analysis/remaining_findings.json`

No finding was silently closed or downgraded. Original identifiers and severities are preserved. N-04, N-08, N-11 and N-12 are independently verified closed in V2.2; S-03 was previously closed by the N-15 remediation. All other findings remain open.

| ID | Sev | Still reproducible | Identity/evidence integrity | Confidentiality | Operational readiness | Fix before Stage B | Residual OK | Investigate | Status |
|---|---|---|---|---|---|---|---|---|---|
| N-04 | MEDIUM | no | no | no | no | no | yes | no | verified_closed |
| N-05 | MEDIUM | yes | no | no | no | no | yes | no | open |
| N-06 | MEDIUM | yes | yes | no | no | no | yes | no | open |
| N-07 | MEDIUM | yes | yes | no | no | no | no | yes | open |
| N-08 | MEDIUM | no | yes | no | no | no | yes | no | verified_closed |
| N-09 | MEDIUM | yes | yes | no | no | no | no | yes | open |
| N-10 | MEDIUM | yes | no | no | no | no | no | yes | open |
| N-11 | MEDIUM | no | no | no | no | no | yes | no | verified_closed |
| N-12 | MEDIUM | no | yes | no | no | no | yes | no | verified_closed |
| N-13 | MEDIUM | yes | yes | no | no | no | no | yes | open |
| N-14 | MEDIUM | no | yes | no | no | no | no | yes | open |
| S-01 | MEDIUM | yes | no | no | no | no | yes | no | open |
| S-02 | MEDIUM | yes | yes | no | no | no | no | yes | open |
| S-03 | MEDIUM | no | no | no | no | no | yes | no | verified_closed |
| S-04 | MEDIUM | yes | no | no | no | no | yes | no | open |
| S-05 | LOW | no | yes | no | no | no | yes | no | open |
| S-06 | LOW | yes | no | no | no | no | yes | no | open |
| S-07 | LOW | no | yes | no | no | no | yes | no | open |
| N-16 | MEDIUM | yes | no | no | no | no | yes | no | open |
| N-17 | MEDIUM | yes | no | no | no | no | yes | no | open |
| N-18 | LOW | yes | no | no | no | no | yes | no | open |
| N-19 | LOW | yes | no | no | no | no | yes | no | open |
| N-20 | LOW | yes | no | no | no | no | yes | no | open |
| N-21 | LOW | yes | no | no | no | no | yes | no | open |
| CORPUS-COMB-03 | MEDIUM | no | no | no | no | no | yes | no | open |
| CORPUS-COMB-12 | MEDIUM | no | no | no | no | no | yes | no | open |
| CORPUS-EVID-03 | MEDIUM | yes | yes | no | yes | yes | no | no | open |
| CORPUS-EVID-06 | MEDIUM | yes | yes | no | yes | yes | no | no | open |
| CORPUS-ST-02 | MEDIUM | no | no | no | yes | no | yes | no | open |
| CORPUS-ID-02 | MEDIUM | yes | yes | no | yes | yes | no | no | open |
| CORPUS-ID-07 | MEDIUM | yes | yes | no | yes | no | no | yes | open |
| D-01 | MEDIUM | yes | yes | no | yes | yes | no | no | open |
| D-02 | MEDIUM | yes | no | no | yes | yes | no | no | open |
| D-03 | MEDIUM | yes | yes | no | yes | yes | no | no | open |

## Summary

- Total tracked: 34
- Still open: 29
- Verified closed: 5
- Require remediation before Stage B: 6

The seven corpus residuals were individually reproduced and classified, not automatically accepted or rejected. None of the remaining findings directly changes recruitment or field-validation authorization; both flags remain hard-coded NO.

