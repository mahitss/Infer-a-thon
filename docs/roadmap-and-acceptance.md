# Roadmap, Milestones & Acceptance Gates

**Rule:** Do not advance a milestone until each exit criterion has evidence and a reviewer records the actual result.

## M001 — Product Discovery & Technical Foundation

**Status:** Draft documentation package; awaiting Product Owner review and official problem-statement fit.

Deliverables: PRD, competitive/prior-art review, proposed architecture, ADR, risk assessment, cost/SIE feasibility and official brief fit review.

Exit criteria:
- [ ] Primary user/problem and main workflow approved.
- [ ] Differentiation hypothesis accepted with competitor caveats.
- [ ] MVP scope and exclusions approved.
- [ ] Architecture and ADR approved.
- [ ] SIE model/hosting path verified or explicitly blocked.
- [ ] Security, data-handling and retention constraints approved.
- [ ] Official brief fit confirmed (2026-12-05).
- [ ] Product Owner approves implementation start.

## M002 — Engineering Foundation

Deliverables: repo standards, env/secrets policy, approved Next.js/FastAPI/Postgres baseline, Docker Compose, migrations, health/readiness endpoints, CI (lint/type/unit/backend/build), SIE adapter and real inference smoke test.

Exit criteria: fresh clone setup works; CI passes; no secrets committed; migration policy verified; SIE model/capability and real inference call recorded.

## M003 — Evidence Ingestion & Provenance

Deliverables: deal workspace; secure upload/import; SHA-256 and immutable source storage; verified chat/document/audio parsing; source-fragment indexing and job state.

Exit criteria: supported files ingest; malformed/oversized inputs fail safely; retries are idempotent; every fragment maps to exact source location; unauthorized users cannot retrieve assets.

## M004 — Negotiation State & Reconciliation

Deliverables: SIE extraction/encoding/reranking; assertion/event schema; deterministic state reducer; evidence search; PO/invoice/delivery comparisons; conflict/uncertainty UI.

Exit criteria: labelled proposal, counteroffer, acceptance, rejection, revision, acknowledgement, silence, conflict and supersession tests; silence/acknowledgement cannot become acceptance; every conclusion has evidence; conflicting/missing states remain explicit; fixed-corpus evaluation metrics recorded.

## M005 — Agentic Investigation & Human Review

Deliverables: bounded investigation loop, allowlisted tools, clarification draft, human review/correction UI and append-only audit trail.

Exit criteria: only allowlisted tools; schema validation; budgets/timeouts; evidence prompt injection cannot change policy or invoke prohibited tools; human edits auditable; no external side effects.

## M006 — End-to-End Demo, Evaluation & Delivery

Deliverables: report export, deterministic synthetic demo, E2E journey, security/accessibility/performance review, demo script and submission docs.

Exit criteria: clean setup replays demo; full journey passes; lint/type/tests/build pass; auth/security cases pass; evaluation and limitations disclosed; deployment status accurate; no mock feature presented as real.

## Required milestone verification report

Record commit SHA and file list; criterion-to-evidence mapping; commands and actual exit codes; test counts/failures; production build result; real user journey result; security findings; incomplete/mocked/blocked items; documentation updates. Report statuses separately: `IMPLEMENTED`, `TESTED`, `VERIFIED`, `DEPLOYED`, `PRODUCTION-READY`.

If the 2026-12-05 official brief materially changes the problem or scoring, stop and update PRD/ADR before affected implementation.
