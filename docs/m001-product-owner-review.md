# M001 Product Owner Review & Discovery Closure Package

**Project:** Infer-a-Thon — Cross-Channel Deal Evidence Agent (provisional title)
**Version:** 0.1 — decision package for Product Owner review
**Date:** 2026-11-21
**Branch:** `research/m001-product-review`
**Starting commit:** `0823860a853b16488aaa0f5816e48ff1f86b0731`
**Status:** All recommendations **PROPOSED**; M001 remains open; implementation is not authorized.

> This package prepares an informed product decision. It does not record any
> Product Owner approval, customer validation, market demand, or working
> software. No application code, database, Docker container, model download or
> inference was produced for this milestone.

## 1. Executive summary

The proposed product reconstructs the negotiated state of one Indian B2B
transaction from original communication evidence and reconciles that state
against purchase orders, delivery records and invoices. Its core promise is
**evidence-first, deterministic, human-reviewed reconstruction** — not an ERP,
legal-advice system, collections tool or autonomous procurement agent.

The discovery work is documented but **not validated**. SIE local feasibility is
**BLOCKED**: observed available RAM was ~1.0–1.6 GB against an internal 8 GB
safety policy, the Docker Linux engine was unavailable, and no inference was
executed. The competitive scan found close adjacency (not a proven gap). The
official problem brief is not yet released (expected 2026-12-05).

Recommendation: keep all eight M001 exit gates open, approve only a **text-first,
single-deal, evidence-provenance MVP** if the Product Owner chooses to proceed,
defer audio/OCR/multilingual claims, simplify the proposed architecture before
implementation, and run a structured user-validation and evaluation programme
before fixing any numeric quality thresholds.

## 2. Problem and user analysis

### Evidence classification (explicit)

| Class | Statements |
|---|---|
| **Verified facts** | Repository baseline and documentation commits exist on `research/*` branches; `main` remains at `8d7f506…`. SIE feasibility experiments were not run; the local CPU gate is BLOCKED with observed RAM ~1.0–1.6 GB, no NVIDIA GPU, Docker engine unavailable (M001.3.x reports). Competitor pages and the IJCAI survey page returned HTTP 200 on 2026-11-21; keyword checks confirmed the capability claims summarized below. |
| **Research-supported observations** | Public product pages describe quote comparison with human supplier choice (Redrawn), commitment/promise tracking with PO/goods-receipt comparison (Kinnow), invoice dispute evidence packs (TextMine), and WhatsApp/document forensic investigation with provenance (Kendraa). Academic prior art covers agreement detection and one-to-many negotiation (IJCAI 2025 survey). These are targeted public-web observations, not exhaustive diligence or product testing. |
| **Product hypotheses** | (H1) A distinct workflow exists: reconstructing the *sequence and status* of negotiation terms from mixed-channel evidence, then reconciling against later artifacts. (H2) Users will assemble and upload a bounded evidence packet for one deal. (H3) Explicit uncertainty and human review increase trust versus a single automated verdict. (H4) Field-level provenance is a judge-visible differentiator. |
| **Unvalidated assumptions** | Required languages (Hindi/Hinglish/English) are unconfirmed. Availability and legal usability of real evidence is unconfirmed. No customer interviews were conducted. No demand exists in evidence. SIE model quality, multilingual retrieval, OCR and transcription are untested. Official brief fit and judging rubric are unknown until 2026-12-05. ₹0 feasibility for the full workflow is unproven. |

### Primary user and painful workflow

**Proposed primary user (hypothesis):** owner, operations manager or accounts/procurement operator at a small distributor, wholesaler or manufacturer handling repeat B2B transactions.
**Secondary user:** finance/audit reviewer needing to understand why a term was marked confirmed, disputed or unresolved.

**Painful workflow to validate:** terms are negotiated across WhatsApp messages, voice notes, calls, quotations and documents; later POs, invoices and delivery records may not reflect the latest mutually accepted term. The operator manually reconstructs "what was actually agreed", usually from scattered artifacts, with no reliable provenance.

**Existing alternatives:** manual chat/document reading and spreadsheets; ERP modules for PO/invoice records (not negotiation lineage); generic AI assistants; adjacent products listed in section 3. **Consequences of getting terms wrong:** disputed price/quantity/payment/delivery commitments, payment delays, incorrect invoicing, and untraceable decisions. These are plausible business consequences, not measured outcomes in this discovery.

### Practical problem-validation plan (not yet executed)

1. Recruit 5–8 operators/finance reviewers through Product Owner contacts; no claims of access yet.
2. Use consented, redacted historical deal packets or synthetic analogues; obtain explicit data-processing consent before using real evidence.
3. Task-based interviews: ask participants to reconstruct one deal's current terms from a packet, then show where their evidence came from and how they would resolve a deliberate conflict.
4. Record observed steps, time, error types, and which artifacts were trusted. Compare with a baseline manual process.
5. Test the H1/H3 hypotheses with a paper prototype of the timeline, provenance view and uncertainty states; ask participants to mark any term they would not trust.
6. Stop criteria: proceed only if the problem recurs across participants, the proposed workflow reduces effort or error, and data can be used lawfully. Record results as evidence; do not pre-declare success.

## 3. Competitive differentiation

Claims below were checked against primary sources on **2026-11-21**; status reflects page accessibility and keyword-level confirmation, not hands-on product testing.

| Product | Category | Primary source (checked 2026-11-21) | Capability evidenced | Overlap with proposal |
|---|---|---|---|---|
| Kinnow Contract Intelligence | Direct / closest adjacency | https://kinnow.ai/agents/contract-intelligence.html — HTTP 200; terms `commitment`, `promise`, `purchase order`, `goods receipt`, `contract` present | Commitment/promise tracking and comparison with PO/goods-receipt performance | **High** — strongest adjacent product; differentiation must be negotiation lineage from original conversations, not generic commitment tracking |
| Redrawn Procurement | Adjacent | https://redrawn.ai/solutions/procurement — HTTP 200; page states voice/photo indents, quote comparison, drafted counter-offers, humans choose supplier | Quote comparison workflow | Do not differentiate on quote comparison or voice-to-indent |
| TextMine | Adjacent / substitute | https://textmine.com/learn/how-to-build-invoice-dispute-evidence-packs — HTTP 200; `invoice`, `purchase order`, `delivery`, `contract`, `evidence pack`, `correspondence` present | Invoice dispute evidence packs | Generic dispute dossier creation is not unique |
| Kendraa | Adjacent / forensic substitute | https://kendraa.co.in/ — HTTP 200; `WhatsApp`, `forensic`, `provenance`, `evidence`, `investigation` present | WhatsApp/document forensic investigation workspace | Generic WhatsApp forensic ingestion with provenance is not unique |
| Riffit | Workflow substitute | https://www.riffit.in/ — HTTP 200; "WhatsApp Invoicing for Indian Freelancers", quotes/invoices from WhatsApp, contracts on dashboard | WhatsApp quote-to-invoice workflow | Do not build basic WhatsApp quote-to-invoice |
| IJCAI 2025 survey | Prior art (academic) | https://ijcai.org/proceedings/2025/1159 — HTTP 200, DOI 10.24963/ijcai.2025/1159 | Survey of one-to-many negotiation, taxonomy of interdependency | Agreement detection is established research, not novel by itself |

Additional sources from the original scan (Uttos, Munshi, Tagaada, Marker Invoice, BinaxPay, BrokWin ERP, UdyamNX, name collisions, the Rajya Sabha report and MSME Samadhaan dashboard) are listed in `docs/research-sources.md`; they were **not re-verified in this milestone** and must retain that limitation. The Rajya Sabha figures remain cited-by-document, not independently validated.

**Proposed differentiation:** (1) negotiation event ledger, (2) evidence-first deterministic state reducer, (3) cross-artifact reconciliation, (4) field-level provenance, (5) uncertainty as an explicit state, (6) bounded read-only agent with human approval.

**Weak or unproven points:** no hands-on competitor testing; no evidence the combined workflow is unserved; Kinnow's described commitment/PO comparison overlaps substantially; differentiation depends on model extraction quality that has not been benchmarked; provenance UI is a design idea, not validated user value. **No uniqueness claim is made.**

## 4. Recommended MVP

**Essential (recommended for v1):**
- One deal per investigation; bounded evidence packet with file type/size limits.
- Text chat export plus born-digital PDF/office/tabular files that can be parsed locally and verified.
- SHA-256 of originals, immutable storage, provenance record.
- Negotiation timeline with proposal / counteroffer / acceptance / rejection / revision / acknowledgement / unknown events.
- Deterministic, versioned state transitions; silence and generic acknowledgement never imply acceptance.
- PO / invoice / delivery reconciliation with explicit MATCH / CONFLICT / MISSING / AMBIGUOUS states and source citations.
- Human review with append-only corrections and reasons.
- Exportable evidence report (timeline, discrepancies, source index, open questions) clearly labelled as an analytical aid, not legal advice.

**Optional / defer:** audio transcription; scanned-document OCR and image OCR; multilingual extraction beyond what verified models support; semantic reranking; agentic investigation loop; multi-workspace SaaS guarantees; live WhatsApp integration; ERP write-back; autonomous messaging; payment initiation; legal filing.

**Audio/OCR/multilingual assessment:** all three should be **excluded from the first MVP** because SIE feasibility is BLOCKED, no OCR/transcription model was tested, and CPU-only support for dedicated OCR VLMs and Whisper is unverified. Including them would risk presenting untested capability as working. Add only after a real local inference gate passes and language coverage is verified against the brief.

## 5. Architecture recommendation

Review of `docs/architecture.md` and `docs/ADR-001.md`:

| Proposed element | Assessment | Recommendation |
|---|---|---|
| Modular monolith | Appropriate for one-deal, seven-day build; consistent with ADR-001 | **Retain**, with explicit module boundaries |
| Next.js + TypeScript web | Plausible but adds a second runtime/toolchain | **Defer approval**; choose one web stack after brief and team skills are confirmed |
| Python + FastAPI | Justified only if SIE Python SDK is actually used | **Conditional**; keep SIE behind a typed adapter, no direct SDK calls in domain code |
| PostgreSQL system of record | Free locally but setup/ops cost; justified for transactions/constraints | **Conditional**; use a repository interface so SQLite or Postgres can be swapped; do not approve until local feasibility is shown |
| pgvector | Unverified; unnecessary for a small corpus | **Defer**; lexical/baseline retrieval first, hide behind repository interface |
| SIE adapter | Correct in principle; SIE local path BLOCKED | **Retain the adapter abstraction**, not the SIE dependency; no unverified model capability in architecture |
| Private evidence storage | Essential | **Retain**; files outside web root, generated keys, SHA-256, no public URLs |
| Database-backed jobs | Reasonable for idempotent retries | **Simplify**: single in-process worker with persisted job state for MVP |
| Deterministic state engine | Core correctness asset | **Retain and prioritise**; versioned rules, append-only history |
| Bounded agent orchestrator | High complexity, untested, risk of hidden side effects | **Defer**; implement allowlisted, auditable tools only if MVP evaluation shows a need |
| 12 modules / 16 entities | Larger than a one-deal demo requires | **Trim** MVP schema to the minimum supporting provenance, events, reconciliation and review |

Unnecessary complexity to remove initially: pgvector, agent loop, multi-role workspace management, object-store adapter, multi-GPU/vector deployment, graph DB (already deferred in ADR-001). No technology is approved merely because it appears in the proposal.

## 6. Threat model and data handling

| Threat | MVP control | Additional production requirement |
|---|---|---|
| Malicious / oversized uploads | Allowlisted formats, size/count limits, parser timeouts, reject archives | Sandboxed parsing, AV scanning, resource quotas |
| MIME spoofing / parser attacks | Content sniffing, extension+content validation, generated storage keys | Fuzzing, isolated parser workers |
| Tenant/workspace isolation | Defer multi-tenant; single-deal local demo | Server-derived workspace scope, cross-tenant IDOR tests |
| Unauthorized evidence access | Auth on every route; local-only demo accounts; no public URLs | RBAC, signed short-lived URLs, per-object access checks |
| Prompt injection in evidence | Treat all imported content as untrusted data; no instructions from evidence; tool allowlist | Adversarial eval suite, output schema validation, human confirmation |
| Sensitive info in logs | Structured logs with IDs only; no raw document text or secrets | Log redaction pipeline, access-controlled log storage |
| Model/API data egress | No hosted inference in MVP; synthetic/public data only | DPA, explicit data-processing approval, egress allowlist |
| Secrets management | Env vars, `.env.example`, no committed secrets, startup validation | Managed secret store, rotation, audit |
| Retention / deletion | Synthetic data only; document retention policy before real data | Legal retention schedule, verified deletion, backups |
| Audit-history integrity | Append-only review events and reasons | Tamper-evident logging, signature/hash chains |
| Human approval boundaries | No external side effects; human confirms/corrects findings | Segregation of duties, approval workflow, fallback review |

## 7. ₹0 feasibility assessment

| Item | Classification | Notes |
|---|---|---|
| Local source code, tests, SQLite, local HTTP server | **Free and genuinely local** | No payment method required |
| PostgreSQL installed locally | **Free and genuinely local (setup cost)** | Not assumed free as a hosted service |
| SIE self-hosted CPU image | **Free license, but UNVERIFIED on this laptop** | Gate BLOCKED; no pull or inference performed |
| SIE Serverless / hosted model APIs | **Usage-priced** | Must not be assumed free; requires payment method |
| Hosted Postgres / object storage / deployment | **Free-tier with restrictions or payment method required** | Not authorized; terms must be verified before use |
| Local Ollama (already installed) | **Free/local license, currently UNUSABLE here** | 4B models present; RAM gate blocks loading; not tested |
| GPU-based OCR / generation images | **Requires hardware we lack** | No NVIDIA GPU; ₹0 path not available on this machine |

**Realistic local-demo fallback:** a deterministic, text-only, synthetic-data demo using local parsing, provenance and rule-based state transitions, with every inferred field labelled as provisional and model-derived where applicable. If no model runs, the demo must state that extraction is rule-based/limited rather than presenting mock inference as real. This fallback is a product decision requiring Product Owner approval.

## 8. Evaluation strategy

Datasets: (a) labelled synthetic message threads with proposals, counteroffers, acceptances, rejections, acknowledgements and silence; (b) paired PO/invoice/delivery artifacts with known conflicts; (c) adversarial prompt-injection content inside evidence; (d) ambiguous/negated statements. Annotation must record span locations, event labels, term values, supporting/conflicting evidence, and reviewer agreement.

Metrics by area: extraction span accuracy and field-level exact match; event classification precision/recall per label; state reconstruction correctness against ground-truth timelines; conflict detection precision/recall; source-location accuracy; retrieval top-1/top-k on labelled claims; abstention rate on ambiguous items and false-acceptance rate; reconciliation correctness; agent tool-policy violation count. Failure cases: missing evidence, contradictory evidence, silence, generic acknowledgement, negated acceptance, OCR/parse failure, and timeout.

No numeric model-quality thresholds are set until a sufficiently labelled corpus exists and inter-annotator agreement is measured. Mocked harness tests are not evidence of model quality.

## 9. Risks and unresolved questions

- Official brief (2026-12-05) may invalidate scope or scoring.
- No user validation or demand evidence.
- Close Kinnow adjacency may erase differentiation.
- SIE local path BLOCKED; ₹0 full workflow unproven.
- Language requirements unknown.
- No labelled evaluation corpus; thresholds cannot be fixed.
- Audio/OCR/multilingual capability untested.
- Seven-day feasibility depends on exact deliverables and rubric.

## 10. Product Owner decision register

All decisions below are **PROPOSED** and require Mahit's explicit approval. Status values: PROPOSED / APPROVED / REJECTED / DEFERRED.

| ID | Question | Options | Recommendation | Rationale | Status |
|---|---|---|---|---|---|
| D-PO-01 | Approve problem statement and primary workflow? | Approve / revise / reject | Approve as hypothesis only | PRD defines coherent workflow but no validation | PROPOSED |
| D-PO-02 | Confirm primary user? | Ops manager / finance reviewer / other | Ops manager primary, finance secondary | PRD hypothesis; needs interviews | PROPOSED |
| D-PO-03 | Accept differentiation hypothesis? | Accept / reject / revise | Accept with competitor caveats; no uniqueness claim | Kinnow adjacency is strong | PROPOSED |
| D-PO-04 | Approve MVP scope? | Full PRD / text-first reduced / defer | Text-first reduced MVP | SIE blocked; time constraint | PROPOSED |
| D-PO-05 | Include audio in MVP? | Include / defer | Defer | No verified transcription capability | PROPOSED |
| D-PO-06 | Include OCR in MVP? | Include / defer | Defer (born-digital only) | Dedicated OCR VLMs need GPU bundles; docling untested | PROPOSED |
| D-PO-07 | Multilingual scope? | EN / EN+HI+Hinglish / TBD | Decide after brief and corpus | Languages unconfirmed; SIE blocked | PROPOSED |
| D-PO-08 | Approve web/backend stack? | Next.js+FastAPI / single stack / defer | Defer approval; keep SIE adapter | No technology approved by default | PROPOSED |
| D-PO-09 | Approve Postgres + pgvector? | Postgres / SQLite / pgvector later | Repository interface; defer pgvector | pgvector unverified, small corpus | PROPOSED |
| D-PO-10 | Accept SIE path as blocked? | Accept blocked / retry later / paid | Accept as blocked for now | Live gate BLOCKED; no inference | PROPOSED |
| D-PO-11 | Approve security/data-handling controls? | Approve / revise | Approve MVP controls, production gap noted | Threat model section 6 | PROPOSED |
| D-PO-12 | Confirm strict ₹0 constraint and fallback? | Strict / allow paid | Strict ₹0 with labelled deterministic fallback | Budget rule in README | PROPOSED |
| D-PO-13 | Approve evaluation approach? | Approve / revise | Approve plan; no thresholds yet | No labelled corpus | PROPOSED |
| D-PO-14 | Re-evaluate after official brief? | Yes / no | Yes, on 2026-12-05 | Competition constraint | PROPOSED |
| D-PO-15 | Authorize implementation start? | Authorize / defer | **DEFER** until all above gates close | M001 explicitly open | PROPOSED |

**Every Product Owner decision remains PROPOSED until Mahit explicitly approves it.**
