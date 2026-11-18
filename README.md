# Infer-a-Thon — Cross-Channel Deal Evidence Agent

> Provisional project concept for Geek Room × Superlinked Infer-a-Thon. Product branding is undecided.

## Mission

Reconstruct the negotiated state of one Indian B2B transaction from original communication evidence (chat exports, voice notes, quotations and other artifacts), then reconcile that state against downstream purchase orders, delivery records and invoices.

The system must distinguish proposals from accepted commitments, preserve original evidence, expose uncertainty, and route ambiguous cases to a human. It is not an ERP, legal-advice system, collections bot, or autonomous procurement agent.

## Status

- **Milestone:** M001 — Product Discovery & Technical Foundation
- **Status:** Documentation package drafted; Product Owner approval and official problem-statement fit pending.
- **Implementation:** Not started.
- **Repository baseline:** GitHub repository inspected on 2026-11-19. It was empty (size 0, no branches; tree and commit-history requests returned HTTP 409).
- **GitHub write attempt:** GitHub Contents API returned HTTP 403 `Resource not accessible by integration`; no remote files or commits were created.

## Team

- **Product Owner:** Mahit — vision, priorities, acceptance and final decisions.
- **Principal Architect / Engineering Lead:** ChatGPT — research, specifications, architecture, security, QA and milestone verification.
- **Implementation Engineer:** Codex — repository implementation, tests, debugging and implementation documentation.

## Project documents

- [Product Requirements Document](docs/PRD.md)
- [Competitive Landscape & Prior Art](docs/competitive-landscape.md)
- [Proposed Architecture](docs/architecture.md)
- [ADR-001: Evidence-first Modular Monolith](docs/ADR-001.md)
- [Roadmap & Acceptance Gates](docs/roadmap-and-acceptance.md)

## Core principle

**No accepted term without evidence. No conclusion without provenance. No external action without human approval.**

AI-derived assertions remain provisional until supported by source references and, where required, human review. Silence, generic acknowledgements and model confidence alone are never proof of acceptance.

## Competition constraint

The event announcement supplied by the Product Owner says final briefs and criteria are released on 2026-12-05, followed by a seven-day build period (2026-12-05–2026-12-11). This concept must be checked against the actual brief before implementation begins.

## Budget and data constraints

- Target ₹0 development spend unless the Product Owner explicitly approves otherwise.
- SIE self-hosting is an option; SIE Serverless is usage-priced and must not be assumed free.
- Verify local model/hardware feasibility before selecting inference deployment.
- Use synthetic/public data by default. Do not upload real commercial evidence to hosted inference without explicit data-processing approval.
- Never commit secrets, credentials, customer documents or private transaction data.

## Research caveat

The project is not claimed to be globally unprecedented. There are adjacent procurement, commitment-tracking, invoicing, commodity-trade ERP and dispute-evidence products, plus academic prior art in agreement/commitment extraction. The proposed differentiation is end-to-end, source-linked reconstruction of negotiation state across conversational evidence and later transaction artifacts. This remains a hypothesis to validate.
