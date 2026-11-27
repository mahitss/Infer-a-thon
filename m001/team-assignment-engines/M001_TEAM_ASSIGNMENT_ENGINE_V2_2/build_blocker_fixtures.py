# -*- coding: utf-8 -*-
"""V2.2 blocker fixtures. All candidate data is SYNTHETIC_TEST_DATA."""
import copy, json, os
from pathlib import Path
D = Path(__file__).resolve().parent / 'tests' / 'fixtures'
BASE = json.loads((D / 'valid_four_person.json').read_text(encoding='utf-8'))


def save(name, obj):
    (D / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def make(name, mutate):
    s = copy.deepcopy(BASE)
    mutate(s)
    save(name, s)


# F-007 invisible-only and mixed basis / rationale.
for tag, ch in (('zwsp', '\u200b'), ('lrm', '\u200e'), ('wj', '\u2060'),
                ('bom', '\ufeff')):
    make('basis_invisible_' + tag + '.json',
         lambda s, c=ch: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', c * 6))
    make('rationale_invisible_' + tag + '.json',
         lambda s, c=ch: s['combination_approvals'][0].__setitem__('rationale', c * 6))
make('basis_invisible_mixed.json',
     lambda s: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', ' \t\u200b\u200e\n '))
make('rationale_invisible_mixed.json',
     lambda s: s['combination_approvals'][0].__setitem__('rationale', '\u200b \u2060\t'))

# Meaningful Unicode content controls.
CONTENT = {
    'english': 'Product Owner decision documented 2026-11-27 for RESEARCH_OWNER',
    'accented': 'Décision du Product Owner — approbation documentée pour Café Étudiant',
    'indic': 'उत्पाद स्वामी का दस्तावेज़ अनुमोदन — हिन्दी परीक्षण',
    'rtl': 'موافقة مالك المنتج موثقة - اختبار عربي',
    'emoji_zwj': 'PO approval 👩‍💻 documented with family 👨‍👩‍👧‍👦 and flag 🇬🇧',
}
for tag, text in CONTENT.items():
    make('basis_valid_' + tag + '.json',
         lambda s, t=text: s['roles']['RESEARCH_OWNER']['approval'].__setitem__('basis', t))
    make('rationale_valid_' + tag + '.json',
         lambda s, t=text: s['combination_approvals'][0].__setitem__('rationale', t))

# N-04 escalation contact.
make('escalation_ws.json',
     lambda s: s['roles']['RESEARCH_OWNER']['escalation'].__setitem__('contact', '  \t\n '))
make('escalation_invisible.json',
     lambda s: s['roles']['RESEARCH_OWNER']['escalation'].__setitem__('contact', '\u200b\u2060'))

# N-08 duplicate evidence record under a second ID.
def duplicate_evidence(s):
    src = s['evidence']['e-acc-C-P1-RESEARCH_OWNER']
    clone = copy.deepcopy(src)
    clone['evidence_id'] = 'e-acc-C-P1-RESEARCH_OWNER-copy'
    s['evidence'][clone['evidence_id']] = clone

make('evidence_duplicate.json', duplicate_evidence)


# N-11 combination decision before candidate acceptance.
def early_decision(s):
    s['combination_approvals'][0]['decision_timestamp'] = '2026-11-26T00:00:00+00:00'
    for role in ('RESEARCH_OWNER', 'CONTINUE_STOP_OWNER'):
        s['roles'][role]['acceptance']['candidate_accepted_at'] = '2026-11-27T00:00:00+00:00'

make('combination_before_acceptance.json', early_decision)


# N-12 consistent whitespace-only candidate reference.
def whitespace_ref(s):
    ws = '   '
    s['candidates'][ws] = {'candidate_ref': ws, 'active': True, 'fixture_marker': 'SYNTHETIC_TEST_DATA'}
    del s['candidates']['C-P1']
    for role in ('RESEARCH_OWNER', 'CONTINUE_STOP_OWNER'):
        s['roles'][role]['candidate_ref'] = ws
    for a in s['appointments']:
        if a['candidate_ref'] == 'C-P1':
            a['candidate_ref'] = ws
    for ca in s['combination_approvals']:
        if ca['candidate_ref'] == 'C-P1':
            ca['candidate_ref'] = ws

make('candidate_whitespace_ref.json', whitespace_ref)
print('blocker fixtures added:', len([f for f in os.listdir(D) if f.endswith('.json')]))
