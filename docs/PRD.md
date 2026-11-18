# Product Requirements Document

**Project:** Infer-a-Thon — Cross-Channel Deal Evidence Agent  
**Version:** 0.1 · Provisional discovery draft  
**Date:** 2026-11-19  
**Status:** For Product Owner review; not approved for implementation

## 1. Problem

Indian B2B SMEs may negotiate and revise commercial terms across chat messages, voice notes, calls, quotations and documents. A subsequent purchase order, invoice or delivery record may not reflect the latest mutually accepted terms. Existing products already cover parts of procurement automation, quote comparison, payment follow-up, commitment tracking and invoice dispute evidence. This proposal focuses on reconstructing the sequence and status of negotiation terms from original communication evidence and checking downstream artifacts against that reconstructed state.

The system must not assume a message is acceptance, silence implies consent, or the newest document automatically supersedes prior evidence.

## 2. Users and jobs

**Primary user:** owner, operations manager or accounts/procurement operator at a small distributor, wholesaler or manufacturer handling repeat B2B transactions.

**Secondary user:** finance/audit reviewer who needs to understand why a term was marked confirmed, disputed or unresolved.

Jobs to be done:
1. Assemble all available evidence for one transaction.
2. See which terms were proposed, countered, accepted, rejected, revised or left ambiguous.
3. Find differences between the evidenced deal state and PO, invoice or delivery records.
4. Inspect exact source material behind every extracted claim.
5. Resolve ambiguity with targeted human clarification.
6. Export a human-reviewable timeline and discrepancy report.

## 3. Value proposition

Turn scattered negotiation evidence into a traceable, reviewable deal record—without pretending an AI model can determine legal agreement from ambiguous messages.

## 4. Core user journey

1. User creates a deal and enters parties/reference.
2. User uploads a bounded evidence packet: WhatsApp text export, quotation/PO/invoice PDF, CSV/XLSX and/or audio.
3. System validates actual file type and size, hashes the original, and records provenance.
4. Parsing and selected SIE tasks produce source fragments and candidate structured claims.
5. Every claim links to a source span (message/time, PDF page, spreadsheet cell/row or audio timecode).
6. Retrieval and reranking find supporting and conflicting evidence for each candidate term.
7. A deterministic state reducer calculates candidate term status; the model cannot unilaterally finalize agreement state.
8. A bounded agent investigates unresolved issues using allowlisted read-only tools.
9. A reviewer confirms, rejects or corrects proposed findings; decisions are audited.
10. System exports a timeline and field-level reconciliation report with sources and unresolved questions.

## 5. Functional requirements

### FR-01 Deal workspace
- Create, view, update and archive a deal.
- Store parties, reference, currency and optional business context.
- Enforce workspace/tenant isolation on every operation.

### FR-02 Evidence ingestion
- Initial candidates: WhatsApp exported text, PDF, DOCX, CSV/XLSX and audio formats supported by a verified SIE transcription model.
- Validate content type, not only extension; enforce upload/count limits and parser timeouts.
- Compute SHA-256; preserve original bytes unchanged; store derivatives separately.
- Reject encrypted, malformed, oversized and unsupported files with actionable errors.

### FR-03 Structured extraction
- Extract candidate parties, product/service, quantity/unit, unit price/currency, payment terms/due date, delivery date, freight and tax.
- Store source location, extractor/model version, schema/prompt version and confidence.
- Distinguish unknown from missing; do not fill unsupported values.

### FR-04 Negotiation-event classification
Candidate event labels: `PROPOSAL`, `COUNTEROFFER`, `ACCEPTANCE`, `REJECTION`, `REVISION`, `ACKNOWLEDGEMENT`, `CLARIFICATION`, `WITHDRAWAL`, `UNKNOWN`.

Retain actor, addressee, communicated timestamp and referenced prior offer where known. Ambiguity must remain `UNKNOWN` / `NEEDS_REVIEW`.

### FR-05 Deal-state reconstruction
- Keep a versioned event history; never overwrite original evidence or extracted assertions.
- Derive candidate current terms using explicit, deterministic, versioned transition rules.
- Silence never implies acceptance.
- Generic “okay”, “seen”, “noted” or delivery acknowledgement is not automatically acceptance.
- A later document is evidence, not automatic proof of mutual agreement.
- Preserve superseded terms in history.

### FR-06 Evidence retrieval
- Retrieve semantically relevant fragments for a claim/issue.
- Filter by authorized workspace, deal, party, source, time and term.
- Use SIE reranking to order candidate evidence where quality tests support it.
- Separate supporting, contradictory and merely contextual evidence.

### FR-07 Reconciliation
Compare candidate reconstructed terms with PO, invoice and delivery/receipt artifacts. Per-field statuses: `MATCH`, `CONFLICT`, `MISSING`, `AMBIGUOUS`, `NOT_APPLICABLE`. Show both values, chronology, source links and deterministic rule.

### FR-08 Agent investigation
- Bounded, observable tool loop.
- Allowlisted tools: search authorized evidence, fetch source excerpt, compare values, inspect event history, draft clarification, generate report.
- No external messages, business-system writes, payment approvals or legal filings.
- Enforce step/time/output budgets; persist tool traces.

### FR-09 Human review
- Reviewer may confirm, reject or correct a proposed assertion/state.
- Require a reason for overrides.
- Preserve model suggestion and human decision separately.
- Record actor, timestamp, prior and new state.

### FR-10 Reporting
Export a readable timeline, field reconciliation, source index, discrepancies and open questions. Clearly state that it is an analytical aid, not legal advice or a guarantee of admissibility/recovery.

## 6. Non-functional requirements

- **Correctness:** no accepted-term status without traceable evidence plus deterministic rule/human review.
- **Provenance:** every AI-derived claim links to exact source location or is marked unsupported.
- **Security:** server-side authorization per endpoint; tenant-scoped queries; secrets only in environment/secret manager.
- **Privacy:** synthetic/public data by default; disclose hosted inference data egress.
- **Reliability:** idempotent ingestion/retry and visible partial failures.
- **Observability:** structured logs with request/deal IDs; no raw sensitive document content or secrets in normal logs.
- **Accessibility:** keyboard-operable primary journey, labelled controls and readable statuses.
- **Performance:** establish baselines on a fixed corpus; no unmeasured latency claims.
- **Maintainability:** modular monolith, typed contracts, migrations and automated tests.

## 7. MVP scope

**In scope:** one deal at a time; file import (no live WhatsApp integration); text chat export, PDF/office/tabular files and audio only after supported model verification; initial four term groups (quantity, unit price, payment term/due date, delivery commitment); evidence timeline/source viewer; deterministic state machine; PO/invoice/delivery reconciliation; clarification draft; human review; exportable report; labelled synthetic evaluation corpus.

**Out of scope:** WhatsApp Business API/phone integration; ERP write-back; autonomous sending; supplier selection/order placement; payment collection/initiation or credit underwriting; legal advice/enforceability determination or automated MSME Samadhaan filing; production multi-tenant SaaS guarantees unless required by brief; blockchain; custom model training during sprint.

## 8. User stories

- As an operations manager, I upload a chat export and related documents to reconstruct one deal.
- As a reviewer, I inspect original evidence behind each extracted term.
- As a buyer/supplier, I see supported, contradicted and unresolved terms.
- As a finance reviewer, I identify invoice/PO differences against the reconstructed state.
- As an operator, I correct a mistaken extraction without erasing the original output.
- As a judge, I replay a deterministic scenario and inspect evaluation results.

## 9. Provisional acceptance criteria

- Each supported source has a SHA-256 and immutable original reference.
- Every extracted claim includes exact source location and processing metadata.
- Labelled proposal/counteroffer/acceptance/rejection cases produce expected deterministic transitions.
- Silence and generic acknowledgement never become acceptance.
- Conflicts remain unresolved until adequate evidence or human review.
- Search cannot cross workspace/deal authorization boundaries.
- Every discrepancy displays compared values and source citations.
- Human corrections are append-only and auditable.
- Agent cannot invoke tools outside allowlist or create external side effects.
- Identical input/state yields reproducible report content.
- Tests cover malformed input, unauthorized/cross-tenant access, prompt injection, ambiguous evidence and inference failure.

Numeric model-quality thresholds must be fixed only after the evaluation corpus is labelled.

## 10. Open questions

1. Does the official 2026-12-05 brief fit this workflow and reward it?
2. Which languages are required (Hindi, Hinglish, English or others)?
3. Are SIE credits available, or is self-hosted SIE required?
4. What compute is available during the seven-day sprint?
5. Can we obtain consented realistic samples, or must all demo data be synthetic?
6. What exact deliverables and judging rubric will apply?
