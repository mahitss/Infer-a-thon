# Field Validation Protocol — Cross-Channel Deal Evidence Agent

**Status:** Research preparation only. **No participants have been contacted, no interviews have been conducted, and no findings exist.**
**Version:** 0.1 · 2026-11-21
**Branch:** `research/m001-product-review`
**Related:** `docs/m001-product-owner-review.md`, `docs/PRD.md`

> This document is a protocol to be executed later. It does not record customer
> validation, market demand, or Product Owner approval. All hypotheses below
> remain unvalidated. Do not contact participants or collect real commercial
> data until a Product Owner authorises it.

## 1. Participant profile

**Target hypothesis (not a validated market):** small distributors handling repeat B2B transactions. This is **one exploratory segment**; wholesalers and manufacturers are separate segments requiring their own evidence. Successful interviews here would not establish a market.

**Who to seek:** people who personally handle at least one of negotiation, order confirmation, invoicing, or delivery reconciliation — e.g. owner/operations manager, purchase or sales coordinator, accounts/procurement operator.

**Inclusion criteria**
- Works at a small distributor with repeat B2B transactions.
- Personally handled a negotiated transaction in the last 3 months.
- Uses at least one digital channel (chat, email, documents, spreadsheet, ERP) for deal communication.
- Willing to discuss a **redacted or synthetic** transaction only.

**Exclusion criteria**
- No personal involvement in negotiation or reconciliation.
- Only large-enterprise/regulated procurement experience (different segment).
- Wants to share live confidential customer documents — do not accept them.
- Cannot provide voluntary consent or asks to be recorded anonymously without consent.

**Recruitment target:** 5–8 exploratory interviews. This number supports qualitative pattern-spotting only — not market validation, demand measurement or generalisation.

## 2. Interview protocol (25–35 minutes, neutral)

**Opening (2 min):** explain purpose, voluntary participation, recording consent, and that no confidential data should be shared. Confirm they may stop or withdraw at any time.

**Anchor on their most recent real transaction (without collecting its content).** Ask the following, in this order, using their own words:

1. "Think of the most recent deal you personally handled where terms were discussed. What happened first?"
2. "Where were the terms exchanged — chat, call, email, documents, in person? What was used most?"
3. "When the price changed during that deal, how was the change communicated and recorded?"
4. "Same question for quantity, payment terms and delivery date — where did those changes show up?"
5. "How did you decide what the final agreed terms were?"
6. "How was the purchase order checked against what had been discussed? Who did that?"
7. "Tell me about a time the invoice did not match what you expected. What did you do?"
8. "When two records disagreed, how was the disagreement resolved?"
9. "What messages, files or records did you keep for that deal? Where do they live now?"
10. "Walk me through what you did manually from first discussion to final invoice."

**Neutral probes:** "Can you say more?" / "What happened next?" / "How did you know?" / "Who else was involved?"

**Avoid leading questions.** Do **not** ask "Would you use our AI agent?", "Is this a big problem?", "Wouldn't it help to have AI find the answer?", or anything that names the proposed solution before the concept section. Do not describe features, show screens, or mention SIE/AI until section 4.

**Close (2 min):** ask what was missed and who else might have a different view. Thank participant; confirm withdrawal/contact permissions.

## 3. Task-based research exercise (10–15 min within the session)

Provide a **synthetic or properly redacted** evidence packet containing: a short chat export with a proposal, a counteroffer, an ambiguous acknowledgement, one conflicting price, a PO, a delivery note and an invoice. No real customer names, phone numbers, bank details or private documents.

Ask: "Using only this packet, tell me what you believe the current agreed terms are, and how you reached that conclusion."

**Record without interpretation:**
- Time taken to reach an answer.
- Sources consulted and order consulted.
- Statements the participant marked ambiguous.
- Conflicting terms noticed (and missed).
- Mistakes, hesitation or self-corrections.
- Manual tools used (paper, spreadsheet, calculator, notes app).
- Whether the reconstructed result matches the participant's own understanding (ask them to rate confidence in their own words).

Do not correct the participant or explain the "right" answer. Do not require disclosure of confidential information; if they start to do so, stop them and remind them of the boundary.

## 4. Concept evaluation (only after workflow questions and exercise)

Introduce the concept in neutral terms: "A tool that keeps each negotiation event, links every extracted term to its exact source, and shows conflicting or uncertain terms for a person to review."

Then ask:
1. "Which part of that, if any, would actually be useful in the workflow you just described?"
2. "Which findings would you distrust, and why?"
3. "What would you still verify manually?"
4. "What would stop you from using such a tool?"
5. "What is already solved by the software or process you use today?"

Record negative and indifferent reactions verbatim. Do not argue for the concept, do not ask "would you pay?", and do not treat enthusiasm as validation.

## 5. Structured note-taking template (one per participant)

```
Participant code: P-01 (anonymous; no name/phone/email/bank details)
Date / interviewer:
Role:
Business segment: small distributor / other (specify) — exploratory only
Consent: recording [yes/no] · quotation use [yes/no] · may withdraw [confirmed]

WORKFLOW OBSERVATIONS (what was done, not what was claimed)
- Transaction type / recency:
- Channels used:
- Steps observed (ordered):
- Artifacts retained:

DIRECT QUOTATIONS (only with consent; verbatim)
- Q1: "..."
- Q2: "..."

PAIN POINTS (report participant's words; note who raised them)
-

EXISTING ALTERNATIVES (what they use now)
-

EVIDENCE OF REPEATED PROBLEMS (recurrence across this interview / across participants)
-

CONTRADICTORY OBSERVATIONS (within or between participants)
-

RESEARCHER INTERPRETATION (clearly separate; label as inference)
-

TASK EXERCISE METRICS
- Time taken:
- Sources consulted:
- Ambiguities noticed / missed:
- Conflicts noticed / missed:
- Confidence stated (own words):

CONCEPT REACTIONS (post-exposure only)
- Useful part:
- Distrust:
- Still manual:
- Blockers:
- Already solved:
```

Keep researcher interpretation visually separate from participant statements at all times.

## 6. Privacy and consent

- Participation is **voluntary**; no inducement that could pressure participation.
- Obtain explicit consent **before** recording; offer a no-recording option with written notes.
- Do **not** collect customer names, phone numbers, bank details, or private transaction documents. Do not photograph screens containing them.
- Use only synthetic or properly redacted packets; if a participant begins disclosing confidential data, stop and redirect.
- Do **not** upload participant data, notes, recordings or packets to any AI service or hosted tool.
- Store notes locally with participant codes only; restrict access; define a deletion date before collection starts.
- Participants may stop at any time or withdraw afterwards; on withdrawal, remove their notes and recordings.
- No real evidence may be used for model training or evaluation without separate explicit legal/data-processing approval.

## 7. Analysis framework (5–8 exploratory interviews)

Build a matrix with one row per participant and four clearly separated columns:

| Participant | Observed behavior (task + workflow) | Reported pain (quoted) | Researcher interpretation (labelled inference) | Unverified assumptions |
|---|---|---|---|---|
| P-01 | | | | |
| P-02 | | | | |

**Additional comparison views:** frequency of repeated behaviours across participants; contradictions between participants; which pain points were observed in the task versus only reported; which concept reactions were positive, negative or indifferent.

**Evidence that could DISPROVE the product hypothesis — record explicitly:**
- Participants already solve this reliably with existing tools/processes.
- Reconciliation is rare, quick, or not a source of error.
- Terms are effectively recorded in one authoritative system, so no reconstruction is needed.
- Provenance/uncertainty views are ignored or distrusted.
- The main need is a different segment or a different workflow (e.g. payment follow-up, not negotiation state).
- Participants would still verify everything manually, removing the tool's value.
- Confidentiality or effort of assembling evidence outweighs any benefit.
- Language/channel assumptions (chat, Hindi/Hinglish) do not match reality.

**Do not define success as "participants liked the concept".** Success for this exploratory phase is: a clearly described recurring workflow with observable failure modes, evidence of current workarounds, and a defensible reason to continue or stop. Record stop signals as seriously as positive signals.

## 8. Decision implications

Results may change the following Product Owner decisions (all remain PROPOSED until Mahit approves):

- **Primary user (D-PO-02):** a different role may own reconciliation than assumed.
- **Business segment:** small distributors may be the wrong first segment; another segment may show stronger pain.
- **Problem statement (D-PO-01):** the real problem may be a different step (e.g. invoice mismatch handling) rather than negotiation-state reconstruction.
- **MVP scope (D-PO-04):** file formats, term groups and report content may change; audio/OCR/multilingual decisions (D-PO-05…07) may be confirmed or made irrelevant.
- **Differentiation (D-PO-03):** provenance or uncertainty may prove unimportant, weakening the proposed differentiator; Kinnow-style commitment tracking may already satisfy users.
- **Agent requirements (D-PO-16):** if users distrust automated findings, agent scope may shrink to retrieval and citation only; if manual comparison dominates, the minimum candidate agent may need to prioritise contradiction detection.
- **Competition track (D-PO-17):** observed workflow may suggest a different problem emphasis after the official brief is reviewed.

Record how each finding maps to a decision ID; do not silently update the PRD or architecture from interview impressions. Any scope change requires a new Product Owner decision.

## Execution status

**NOT STARTED.** No recruitment, contact, interviews, packets, recordings, notes or findings exist as part of this document. This kit must be executed under a separate authorised activity with its own consent and data-handling controls.
