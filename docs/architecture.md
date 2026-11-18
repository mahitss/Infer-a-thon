# Proposed System Architecture

**Status:** Proposal for approval; no application code exists.  
**Design:** Modular monolith, evidence-first data model, deterministic state transitions and bounded agent loop.

## 1. System context

The application processes a single B2B deal dossier. Users provide negotiation artifacts and transaction documents. The system extracts candidate claims, links them to original source locations, builds a negotiation event history, retrieves corroborating/contradictory evidence, compares later transaction artifacts and presents unresolved issues for human review.

## 2. Proposed stack (provisional)

| Layer | Proposal | Caveat |
|---|---|---|
| Web | Next.js + TypeScript | Evidence workspace, timeline and review screens |
| API/domain | Python + FastAPI | Typed domain/API layer and SIE Python SDK |
| System of record | PostgreSQL | Transactions, constraints, append-only event model |
| Vector search | pgvector if supported by chosen DB deployment | Verify extension and vector dimensions; otherwise hide behind repository interface |
| Inference | SIE through typed adapter | Encode, Score, Extract, Generate; speech/OCR tasks depend on actual model and endpoint support |
| Files | Private local storage adapter for hackathon; object-store adapter later | Never public upload URLs or repository-stored user evidence |
| Jobs | Database-backed job table / same-codebase worker | Avoid Redis/Celery until measured need |
| Tests | Pytest, API integration tests, Playwright E2E | Full ingestion-to-report workflow |
| Runtime | Docker Compose | Reproducible local environment |

₹0 constraint: SIE itself is open-source/self-hostable, but local model execution depends on hardware. SIE Serverless publishes per-task prices and must not be presumed free. Validate the cheapest feasible route before committing.

## 3. Modules

1. Identity/workspace and memberships.
2. Deal and counterparty management.
3. Evidence vault (immutable originals, hashes, MIME validation and access checks).
4. Ingestion adapters (WhatsApp text export, document, table, audio where verified).
5. Assertion extraction (candidate terms, actors, speech acts, timestamps and source spans).
6. Evidence retrieval (lexical/semantic search with metadata filters and SIE reranking).
7. Negotiation state engine (deterministic event reducer and versioned terms).
8. Reconciliation engine (PO/invoice/delivery comparisons).
9. Agent orchestrator (bounded investigator with allowlisted tools).
10. Human review and correction history.
11. Report builder.
12. Audit and observability.

## 4. SIE integration (verify model task support)

SIE's official documentation describes four primitives: Encode, Score, Extract and Generate. Its current model catalogue separately lists tasks/models for document OCR and speech-to-text. These are model tasks invoked via the appropriate SIE primitive/adapter; do not treat OCR or transcription as an independent fifth primitive.

- **Extract:** structured entities/terms; OCR/document-to-Markdown model; speech-to-text model where supported.
- **Encode:** vector representations of evidence fragments and issue queries.
- **Score:** rerank candidate fragments for each claim/discrepancy.
- **Generate:** draft investigation questions/clarifications, with strict schema and policy checks.
- **Classification/guardrails:** optional only after model availability, language coverage and accuracy are tested.

Pin model identifiers/configuration, schema versions and model provenance. Verify model input requirements, language coverage, file formats, context limits, timeouts and local/managed availability before implementation.

## 5. Conceptual data model

- `User`
- `Workspace`
- `WorkspaceMember` (role)
- `Counterparty`
- `Deal`
- `EvidenceAsset` (storage key, original name, SHA-256, MIME, size, uploader, timestamps)
- `EvidenceFragment` (message/page/row/cell/audio timecode, text, speaker attribution, source offsets)
- `ExtractionRun` (model/version, schema/prompt version, status, error metadata)
- `Assertion` (candidate subject/predicate/value/unit, actor/target, speech act, confidence, provenance)
- `NegotiationEvent` (event type, referenced prior event, communicated/recorded times)
- `DealTermVersion` (term, value, status, reducer version, supporting events)
- `EvidenceLink` (assertion/event/term to source fragment; SUPPORTS/CONTRADICTS/CONTEXT)
- `Discrepancy` (term, artifact value, reconstructed candidate, status, rule and evidence links)
- `HumanReview` (reviewer, decision, correction, reason and timestamps)
- `AgentRun` / `AgentToolCall` (bounded plan and trace)
- `AuditEvent` (append-only history)
- `ProcessingJob` (idempotency and retry metadata)

Represent graph relationships with relational edges and foreign keys. A dedicated graph DB is not justified for the MVP.

## 6. State semantics

Candidate speech acts: `PROPOSAL`, `COUNTEROFFER`, `ACCEPTANCE`, `REJECTION`, `REVISION`, `ACKNOWLEDGEMENT`, `CLARIFICATION`, `WITHDRAWAL`, `UNKNOWN`.

Candidate term statuses: `PROPOSED`, `COUNTERED`, `ACCEPTED_CANDIDATE`, `REJECTED`, `SUPERSEDED`, `CONFLICTED`, `NEEDS_REVIEW`, `UNRESOLVED`.

Rules:
- Silence never implies acceptance.
- Generic “okay”, “seen”, “noted” or delivery acknowledgement is not automatically acceptance.
- Acceptance must identify the relevant offer/term sufficiently for a deterministic rule or human reviewer to validate it.
- A later document is evidence, not automatic proof of mutual agreement.
- Contradictory sources remain visible; do not collapse them into a guessed value.
- Human correction creates a new event/version; never delete model output or original source.

## 7. Data flow

1. Authenticated user creates a deal.
2. API validates upload, hashes it, stores original privately and records asset metadata.
3. Worker parses source into fragments with exact locations.
4. SIE processes applicable model tasks; outputs are validated against strict schemas.
5. Candidate assertions persist with extraction-run and provenance links.
6. SIE Encode stores vectors linked to fragments.
7. Query applies workspace/deal filters, then SIE Score reranks candidates.
8. Deterministic reducer derives candidate deal-term versions.
9. Reconciliation compares terms with PO/invoice/delivery assertions.
10. Agent uses allowlisted tools to investigate and draft clarifications.
11. Human review appends corrections/audit events.
12. Report builder exports reviewed state and provenance index.

## 8. Authorization

All routes require authenticated identity except health/readiness. Proposed roles: `OWNER`, `ADMIN`, `CONTRIBUTOR`, `REVIEWER`, `READ_ONLY`.

- Owner/admin: manage workspace and membership.
- Contributor: create deals, upload evidence, request processing.
- Reviewer: confirm/reject/correct assertions and discrepancies.
- Read-only: view authorized deals/evidence/reports.
- Server derives workspace scope from membership; never trust browser-supplied workspace IDs.
- Every file/download/report route repeats the same access check.
- Test cross-workspace IDOR attempts for all object identifiers.

## 9. Threats and controls

Threats: malicious files/parser exploits, prompt injection embedded in evidence, cross-tenant leaks, hallucinated agreement, false speaker attribution, oversized uploads, duplicate/replayed jobs, spreadsheet formula injection and secrets in logs.

Controls:
- Allowlisted formats, content sniffing, size/count limits, parser timeouts; reject archives unless safely unpacked.
- Generated storage keys, files outside web root, original checksum, immutable originals; separate derivative hashes.
- Treat imported evidence as untrusted data, never system instructions.
- Tool allowlist, per-run budgets, typed arguments/results; no arbitrary shell/network tools.
- No raw evidence/secrets in standard logs.
- Workspace scope in each query, DB relation and file access.
- Rate limits on auth, upload, processing and export.
- CSRF/CORS/session controls per selected auth method.
- Protect against ZIP/decompression bombs and export formula injection.
- Synthetic data by default; explicit approval for hosted inference/data egress.
- OWASP ASVS checklist; target level to be selected after formal threat model.

## 10. Failure handling

- SIE timeout: preserve source, mark job retryable/failed; never mark deal processed.
- Partial extraction: preserve completed fragments, show incomplete state; idempotent retry.
- Low-confidence speech act: `NEEDS_REVIEW`.
- No evidence: return `GAP`, not generated assertion.
- Conflicting evidence: `CONFLICTED`.
- Invalid file: reject safely with reason.
- Agent budget exceeded: stop, persist trace and show remaining questions.
- Export failure: no deal-state mutation; safe retry.

## 11. Deployment

Hackathon: Docker Compose and only a verified free/approved hosting path. Configure web/API/worker/SIE endpoint. No live WhatsApp API dependency. Production would additionally require managed DB backups, private object storage, TLS, secret management, migration/rollback, monitoring, rate limits, retention controls and incident response. These are design items, not implemented capabilities.

## 12. Approval checklist

- [ ] Primary user and problem approved.
- [ ] MVP and exclusions approved.
- [ ] SIE models and hosting route proven on available resources.
- [ ] DB/vector approach tested.
- [ ] Authentication and workspace isolation approved.
- [ ] File formats, storage and retention approved.
- [ ] Official brief fit and seven-day feasibility confirmed.
