# M001 V2.2 — Unicode Validation Security Report (F-007)

**Mission:** M001-TEAM-008  
**Component:** `engine/validator.py` → `meaningful_text()`, `NON_CONTENT_CATEGORIES`

## Root cause in V2.1

`meaningful_text(value)` was `isinstance(value, str) and bool(value.strip())`. `str.strip()` removes
Unicode whitespace (e.g. U+00A0, U+2003, U+3000) but not Unicode format characters (`Cf`). A basis
or rationale consisting solely of U+200B ZERO WIDTH SPACE, U+200E LEFT-TO-RIGHT MARK or U+2060
WORD JOINER was therefore accepted, yielding Stage B YES with no issues. Independently reproduced
in the V2.1 follow-up and again here.

## Documented Unicode policy

A character is classified as NON-CONTENT when its Unicode general category is one of:

| Category | Meaning | Examples |
|---|---|---|
| `Cc` | Control | U+0000–U+001F, U+0085 |
| `Cf` | Format | U+200B ZWSP, U+200E LRM, U+200F RLM, U+2060 WJ, U+FEFF BOM |
| `Zs` | Space separator | U+0020, U+00A0, U+2003 |
| `Zl` / `Zp` | Line / paragraph separator | U+2028, U+2029 |

`meaningful_text()` returns true only when the string contains **at least one** character whose
category is NOT in that set. It never modifies, trims, normalises or coerces the input; it only
classifies it. The predicate is applied consistently to:

- approval basis (`E-DECISION-EVIDENCE-EMPTY`)
- combination rationale (`E-COMBINATION-RATIONALE`)
- escalation contact (`E-ESCALATION-CONTACT`, N-04)
- candidate reference (`E-CANDIDATE-REF-INVALID`, N-12)
- acceptance decision reference and recording authority

## Avoiding indiscriminate removal

Combining marks (`Mn/Mc/Me`), letters, numbers, symbols and emoji remain CONTENT. This preserves:

- English and accented text (`Décision … Café Étudiant`)
- Indic scripts (`उत्पाद स्वामी का दस्तावेज़ अनुमोदन`)
- RTL text (`موافقة مالك المنتج موثقة`)
- legitimate ZWJ emoji sequences (`👩‍💻`, `👨‍👩‍👧‍👦`, `🇬🇧`) — the `Cf` ZWJ is ignored but the `So` emoji
  characters count as content, so the string passes.

A string containing only directional formatting or invisible joiners still fails, as intended.

## Executed cases

| Group | Fixtures | Result |
|---|---|---|
| Invisible-only basis | `basis_invisible_{zwsp,lrm,wj,bom}.json` | all `E-DECISION-EVIDENCE-EMPTY`, readiness NO |
| Invisible-only rationale | `rationale_invisible_{zwsp,lrm,wj,bom}.json` | all `E-COMBINATION-RATIONALE`, readiness NO |
| Mixed whitespace + invisible | `basis_invisible_mixed.json`, `rationale_invisible_mixed.json` | blocked |
| ASCII/Unicode whitespace | `basis_ascii_ws.json`, `basis_unicode_ws.json`, `rationale_{ws,unicode_ws}.json` | blocked |
| Meaningful Unicode (5 languages/forms × basis & rationale) | `*_valid_{english,accented,indic,rtl,emoji_zwj}.json` | all readiness YES, zero issues |
| Non-string/null | `basis_null.json`, `basis_nonstring.json`, `rationale_null.json`, `rationale_nonstring.json` | fail closed via schema or predicate |
| No fabrication | `test_07_no_fabrication` | original basis text unchanged after validation |

## Mutation proof

`M1_F007_predicate_reverted` restores truthiness semantics; the 8-check canary fails it (exit 1).
All five V2.2 mutations detected, 0 survived.
