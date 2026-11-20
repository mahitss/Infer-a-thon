# Roadmap, Milestones & Acceptance Gates

**Rule:** Do not advance a milestone until each exit criterion has evidence and a reviewer records the actual result.

## M001 — Product Discovery & Technical Foundation

**Status:** Draft documentation package; awaiting Product Owner review and official problem-statement fit. **M001 is NOT complete.**

Completed discovery documentation work (recorded, not an M001 exit):
- M001.1–M001.2: imported and audited the M001 documentation baseline on `main` (commits `d5e5e18…`, `79afabf…`, `8d7f506…`).
- M001.3–M001.3.4: SIE feasibility research and harness work on `research/m001-sie-feasibility` (commits `a90025c…`, `c5faa92…`, `a0fb64e…`, `6a91d19…`, `0823860…`). Resource gate **BLOCKED**; no inference or benchmark executed.
- M001.4: Product Owner decision package prepared on `research/m001-product-review` (`docs/m001-product-owner-review.md`); all decisions remain PROPOSED.

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

## M001.4 — Product Owner Review & Discovery Closure

**Status:** Decision package prepared; awaiting independent architectural review and Product Owner decisions. This milestone does **not** authorize implementation.

Deliverables: `docs/m001-product-owner-review.md` covering problem/user validation plan, competitive differentiation with primary-source checks (2026-11-21), recommended text-first MVP, architecture simplification, threat model, ₹0 feasibility, evaluation strategy and a Product Owner decision register with every decision `PROPOSED`.

Exit criteria:
- [ ] Product Owner records a decision for every D-PO item in the register.
- [ ] Problem and primary workflow validated with real potential users.
- [ ] Differentiation hypothesis accepted or revised with competitor caveats.
- [ ] MVP scope and audio/OCR/multilingual exclusions approved.
- [ ] Architecture/ADR changes approved after review.
- [ ] SIE path accepted as blocked or re-tested successfully.
- [ ] Security/data-handling and ₹0 fallback approved.
- [ ] Official brief fit confirmed on/after 2026-12-05.
- [ ] Explicit Product Owner authorization to begin M002.

The M001 exit criteria above all remain open; this section adds a review milestone only.

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
