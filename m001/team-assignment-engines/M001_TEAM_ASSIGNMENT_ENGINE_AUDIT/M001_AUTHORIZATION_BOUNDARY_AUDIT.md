# M001 Authorization Boundary Audit

**Governance:** M001 OPEN; M002 UNAUTHORIZED; recruitment UNAUTHORIZED; field validation NOT STARTED; Research Owner ACCEPTED IN CONVERSATION; other five roles UNASSIGNED. Independent audit only: original implementation untouched, no repository/register/ADR change, no appointment, contact, storage configuration or implementation authorization.

| Outcome | Engine treatment | Independent verdict |
|---|---|---|
| Structural topology validity | topology status warning; synthetic models validated | PARTIAL: unapproved topology can pass (F-12) |
| Role-assignment completeness | missing appointment errors | PASS for current state |
| Human acceptance | candidate_accepted checked for selected states | PARTIAL: PROPOSED bypass (F-08), unknown identities pass (F-07) |
| Formal appointment | FORMALLY_APPOINTED state with requirements | PARTIAL: formal flag mismatch passes (F-09) |
| Product Owner authorization | product_owner_approved boolean | PARTIAL: empty basis passes (F-10) |
| Stage B readiness | not emitted explicitly | UNSUPPORTED; topology warning only |
| Recruitment authorization | governance enum UNAUTHORIZED; no positive grant | PASS: engine cannot grant |
| Field-validation authorization | governance enum NOT_STARTED; no positive grant | PASS: engine cannot grant |

A structurally valid synthetic topology never becomes an actual appointment or authorization in the engine. However, role-completeness output can currently be produced for states that governance would not accept. The engine output must not be treated as Stage B sign-off.

