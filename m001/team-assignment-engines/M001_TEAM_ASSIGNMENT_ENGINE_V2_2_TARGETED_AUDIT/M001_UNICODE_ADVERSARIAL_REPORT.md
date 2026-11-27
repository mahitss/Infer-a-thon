# M001 V2.2 — Unicode Adversarial Verification (F-007)

**Mission:** M001-TEAM-009  
**Evidence:** `tests/results/unicode_duplicate_results.json`, `reports/UNICODE_DUP_AGENT_NOTES.md`

## Algorithm inspected

`meaningful_text()` classifies a character as non-content when `unicodedata.category(ch)` is in
`frozenset(('Cc','Cf','Zs','Zl','Zp'))` and returns true when at least one character is outside
that set. It is applied at six sites: recording authority (line 304), acceptance decision ref
(343), candidate ref (364), approval basis (486), escalation contact (511) and combination rationale
(554). No input is trimmed, normalised or rewritten.

## Results

| Group | Cases | Result |
|---|---|---|
| Reject (invisible/whitespace/mixed/non-string across fields) | 104 | all rejected with expected codes (3 non-string cases fail closed via `E-SCHEMA`) |
| Meaningful Unicode (English, accented, Hindi conjuncts, RTL with marks, ZWJ emoji, meaningful + U+2028) | 60 | all pass, zero issues |
| Boundary/immutability | 11 + whole-state compare | 11 definitive, 7 additional fail-open variants found (below); original text and state unchanged |
| Distinct identities under Unicode variation | N-12 stream | NFC/NFD, fullwidth, case variants remain distinct; no normalisation collision |

## Canonical F-007

U+200B, U+200E, U+2060, BOM-only, tag characters and ASCII+invisible mixes are rejected in basis,
rationale, contact, candidate ref, decision ref and recording authority. **Canonical F-007 is
verified fixed.** Legitimate text containing `Cf` characters (ZWJ emoji, RTL marks) is not rejected.

## New residual D-02 (MEDIUM) — reproduced

The predicate equates "not in the five categories" with "visually substantive". Seven tested strings
with no base character were accepted with Stage B YES and zero issues:

| String | Category | Result |
|---|---|---|
| combining acute only | Mn | accepted |
| Devanagari vowel sign only | Mc | accepted |
| enclosing circle only | Me | accepted |
| private-use only | Co | accepted |
| unassigned U+0378 only | Cn | accepted |
| escaped lone surrogate | Cs | accepted |
| variation selector U+FE0F only | Mn | accepted |

This is a fail-open of decision-text gates by strings that render as nothing or as floating marks. It
is **not** the canonical F-007 (which concerned `Cf` formats) and does not reopen it; it is a new
MEDIUM residual requiring a base-character requirement before Stage B reliance.

## Consistency and immutability

The predicate is consistent across all six application sites. Whole-state comparison before/after
validation is identical (`whole_state_identical: true`); no placeholder or fabricated content is
introduced. No Unicode normalisation created a new identity or evidence-integrity collision in the
tested corpus.
