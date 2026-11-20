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
- Declines to participate voluntarily. **Declining recording does NOT exclude participation** (see section 6); written notes may be used with participation consent.

**Recruitment target:** 5–8 exploratory interviews. This number supports qualitative pattern-spotting only — not market validation, demand measurement or generalisation.

## 2. Interview protocol (25–35 minutes, neutral)

**Opening (2 min):** explain the purpose and the three **separate** permissions — (1) consent to participate in the research, (2) separate consent to record, and (3) separate permission to use direct quotations. Explain that no confidential data should be shared, that declining recording or quotation use still allows participation through written notes, and that they may stop at any time. Never record without explicit prior consent; anonymity is not a substitute for consent.

### 2A. Participant-reported workflow (retrospective, not observed)

The questions below ask the participant to **recall** their most recent real transaction without collecting its content. All answers in this section are **participant-reported workflow** — retrospective self-report, **not** independently observed evidence. Do not label them as observations.

Ask the following, in this order, using their own words:

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

**Close (2 min):** ask what was missed and who else might have a different view. Thank participant. Re-state the three separate permissions, hand over the written withdrawal contact method and cutoff date if post-session withdrawal is configured (section 6A), or state plainly that withdrawal is only possible during the session if it is not.

## 3. Task-based research exercise — DIRECTLY OBSERVED TASK BEHAVIOUR (10–15 min within the session)

This section is different in kind from section 2A. The synthetic packet exercise produces **directly observed task behaviour**: the researcher watches what the participant actually does with a controlled packet. It is not a recollection of a historical deal and must be recorded and analysed separately from participant-reported workflow.

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
CONSENT (three separate permissions)
- Participation consent (voluntary; required to proceed): [yes/no]
- Recording consent (optional; separate): [yes/no] — record ONLY if yes
- Direct quotation permission (optional; separate): [yes/no] — quote ONLY if yes
- Withdrawal contact method given to participant: [yes/no] (configured before recruitment)
- Withdrawal cutoff / deletion date stated to participant: [date]

PARTICIPANT-REPORTED WORKFLOW (retrospective self-report; NOT independently observed)
- Transaction type / recency (as recalled):
- Channels used (as recalled):
- Steps described (ordered, as recalled):
- Artifacts retained (as reported):

DIRECT QUOTATIONS (only with quotation permission; verbatim)
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

DIRECTLY OBSERVED TASK BEHAVIOUR (synthetic packet exercise; observed, not recalled)
- Time taken:
- Sources consulted and order:
- Ambiguities noticed / missed:
- Conflicts noticed / missed:
- Mistakes, hesitation, self-corrections:
- Manual tools used:
- Confidence stated (own words):

RESEARCHER INTERPRETATION (clearly separate; label every line as inference)
-

CONCEPT REACTIONS (post-session concept exposure only)
- Useful part:
- Distrust:
- Still manual:
- Blockers:
- Already solved:
```

Keep researcher interpretation visually separate from participant statements at all times.

## 6. Privacy and consent

- Participation is **voluntary**; no inducement that could pressure participation.
- **Participation consent**, **recording consent**, and **quotation permission** are three separate permissions, requested and recorded separately. Declining recording or quotation use does **not** prevent participation through written notes.
- Recording is permitted **only** after explicit prior consent. **Anonymous recording is not consent.** Never record without it.
- Do **not** collect customer names, phone numbers, bank details, or private transaction documents. Do not photograph screens containing them.
- Use only synthetic or properly redacted packets; if a participant begins disclosing confidential data, stop and redirect.
- Do **not** upload participant data, notes, recordings or packets to any AI service or hosted tool.
- Store notes locally with participant codes only; restrict access. Do **not** create an identity-to-code mapping.
- No real evidence may be used for model training or evaluation without separate explicit legal/data-processing approval.

### 6A. Post-session withdrawal procedure (must be configured before recruitment)

Post-session withdrawal is offered **only** if the following process is actually configured. If it is not configured, do **not** promise withdrawal after the session; offer only the right to stop during the session.

1. **Random participant code:** before the session, assign each participant a random code (e.g. `P-01` generated from a random sequence, not from a name, initials, phone number or organisation). Use this code on all notes and recordings.
2. **Written withdrawal contact method:** give each participant a written contact method **at the start of the session**, configured by the research organiser before recruitment. It may be a generic study inbox, form, or equivalent channel chosen by the organiser. **No email address, phone number or contact identity is invented in this document** — the placeholder is `[withdrawal contact method — configured before recruitment]`.
3. **How to request deletion:** the participant sends only their random participant code through that contact method with a request to withdraw. They do not need to reveal identity or a reason.
4. **No identity mapping:** because identity/contact details are not linked to codes, a valid request is any message containing the participant code. Do not build a lookup table that defeats this separation.
5. **Deletion schedule:** before recruitment begins, define and record the withdrawal cutoff / final deletion date (e.g. analysis-end date) and tell the participant that date. The placeholder `[withdrawal cutoff / deletion date — configured before recruitment]` must be filled in before any recruitment.
6. **What is deleted:** on a valid withdrawal request received before the cutoff, delete **all** notes, quotations, task-exercise records and recordings carrying that participant code, and remove any aggregated references to that code. Confirm deletion to the participant through the same contact method where feasible.
7. **After the cutoff:** once the documented deletion date passes, records can no longer be withdrawn individually; state this plainly to participants rather than implying indefinite withdrawal.
8. **Precondition:** if steps 2 and 5 are not configured, post-session withdrawal is **not available** and the protocol must say so instead of promising it.

## 7. Analysis framework (5–8 exploratory interviews)

Build a matrix with one row per participant and **separate columns for the two evidence types**. Never merge recalled workflow with observed task behaviour.

| Participant | Participant-reported workflow (retrospective, NOT observed) | Directly observed task behaviour (synthetic packet) | Reported pain (quoted, with permission) | Researcher interpretation (clearly labelled inference) | Unverified assumptions |
|---|---|---|---|---|---|
| P-01 | | | | | |
| P-02 | | | | | |

**Additional comparison views:** frequency of repeated behaviours across participants; contradictions between participants; which pain points appeared in **directly observed task behaviour** versus only in **participant-reported workflow**; which concept reactions were positive, negative or indifferent. Researcher interpretation remains inference in every case.

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
- **Competition track (D-PO-17):** participant-reported workflow and directly observed task behaviour may suggest a different problem emphasis after the official brief is reviewed.

Record how each finding maps to a decision ID; do not silently update the PRD or architecture from interview impressions. Any scope change requires a new Product Owner decision.

## Execution status

**NOT STARTED.** No recruitment, contact, interviews, packets, recordings, notes or findings exist as part of this document. This kit must be executed under a separate authorised activity with its own consent and data-handling controls.
