#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V2 deterministic research-team governance validator.

Diagnostic control only. It does not appoint people, authorize recruitment,
authorize field validation, configure storage or modify governance records.
"""
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import re

try:  # Full JSON Schema validation is preferred when locally installed.
    import jsonschema
    _JSONSCHEMA_AVAILABLE = True
except ImportError:  # Deterministic documented subset fallback; no installs.
    jsonschema = None
    _JSONSCHEMA_AVAILABLE = False

ROOT = Path(__file__).resolve().parents[1]
SEVERITY_ORDER = {'ERROR': 0, 'WARNING': 1, 'INFO': 2}

# V2.1 N-15: schema/reference failures are input-condition errors, not validator bugs.
_SCHEMA_EXCEPTION_TYPES = []
if _JSONSCHEMA_AVAILABLE:
    _SCHEMA_EXCEPTION_TYPES.append(jsonschema.exceptions.SchemaError)
    try:  # jsonschema >= 4.18 delegates reference resolution to `referencing`.
        from referencing.exceptions import (  # type: ignore
            PointerToNowhere, Unresolvable, NoSuchResource, InvalidAnchor,
        )
        _SCHEMA_EXCEPTION_TYPES.extend(
            [PointerToNowhere, Unresolvable, NoSuchResource, InvalidAnchor])
    except ImportError:
        pass
    for _name in ('RefResolutionError', '_WrappedReferencingError'):
        _t = getattr(jsonschema.exceptions, _name, None)
        if isinstance(_t, type) and _t not in _SCHEMA_EXCEPTION_TYPES:
            _SCHEMA_EXCEPTION_TYPES.append(_t)
_SCHEMA_EXCEPTION_TYPES = tuple(_SCHEMA_EXCEPTION_TYPES)


def brief(exc, limit=180):
    """Short, stable one-line description of an exception for structured output."""
    text = str(exc).splitlines()[0] if str(exc) else ''
    if len(text) > limit:
        text = text[:limit] + '...[truncated]'
    return '%s: %s' % (type(exc).__name__, text)


def meaningful_text(value):
    """V2.1 N-01/N-02: only a string with non-whitespace Unicode content is meaningful."""
    return isinstance(value, str) and bool(value.strip())


def identity_subject(ref, role):
    """Canonical subject for a role-bound appointment decision."""
    return '%s:%s' % (ref, role)


class DuplicateKeyError(ValueError):
    pass


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    dimension: str = ''
    role: str = ''
    candidate: str = ''
    message: str = ''

    def to_dict(self):
        return asdict(self)


@dataclass
class ValidationResult:
    dimensions: dict
    issues: list
    stage_b_role_ready: bool
    recruitment_authorized: bool = False
    field_validation_authorized: bool = False

    @property
    def errors(self):
        return [i for i in self.issues if i.severity == 'ERROR']

    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == 'WARNING']

    def sorted_issues(self):
        return sorted(self.issues, key=lambda i: (
            SEVERITY_ORDER.get(i.severity, 9), i.code, i.dimension, i.role, i.candidate, i.message))

    def to_dict(self):
        return {
            'stage_b_role_ready': self.stage_b_role_ready,
            'recruitment_authorized': self.recruitment_authorized,
            'field_validation_authorized': self.field_validation_authorized,
            'dimensions': dict(sorted(self.dimensions.items())),
            'blocking_error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'issues': [i.to_dict() for i in self.sorted_issues()]
        }


def load_json_strict(path):
    """Load JSON with duplicate-key rejection and stable input error codes."""
    p = Path(path)
    try:
        raw = p.read_bytes()
    except OSError as exc:
        raise ValueError('E-FILE-NOT-FOUND: %s' % exc.__class__.__name__)
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError('E-ENCODING-INVALID: invalid UTF-8')
    def no_dupes(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise DuplicateKeyError('E-DUPLICATE-JSON-KEY: %s' % k)
            out[k] = v
        return out
    try:
        return json.loads(text, object_pairs_hook=no_dupes)
    except DuplicateKeyError:
        raise
    except json.JSONDecodeError:
        raise ValueError('E-JSON-INVALID: malformed JSON')


def load_policy(path=None):
    return load_json_strict(path or ROOT / 'policy' / 'role_constraints.json')


def load_schema(path=None):
    return load_json_strict(path or ROOT / 'schemas' / 'team_assignment.schema.json')


def validate_schema(instance, schema, path='$'):
    """Documented standard-library subset validator.

    Supports $ref, type, required, properties, additionalProperties (false or
    schema), enum, and items. It does not support full JSON Schema keywords.
    """
    errors = []

    def resolve(ref):
        if not ref.startswith('#/'):
            return None
        node = schema
        for part in ref[2:].split('/'):
            node = node.get(part) if isinstance(node, dict) else None
            if node is None:
                return None
        return node

    def type_ok(value, expected):
        tlist = expected if isinstance(expected, list) else [expected]
        mapping = {'object': dict, 'array': list, 'string': str,
                   'boolean': bool, 'null': type(None)}
        for t in tlist:
            if t == 'number':
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    return True
            elif t == 'integer':
                if isinstance(value, int) and not isinstance(value, bool):
                    return True
            elif t in mapping and isinstance(value, mapping[t]):
                if t != 'boolean' or isinstance(value, bool):
                    return True
        return False

    def walk(value, sch, loc):
        if '$ref' in sch:
            target = resolve(sch['$ref'])
            if target is None:
                errors.append('%s: unresolved $ref %s' % (loc, sch['$ref']))
                return
            walk(value, target, loc)
            return
        if 'type' in sch and not type_ok(value, sch['type']):
            errors.append('%s: type mismatch' % loc)
            return
        if 'enum' in sch and value not in sch['enum']:
            errors.append('%s: enum mismatch' % loc)
        if isinstance(value, dict):
            for key in sch.get('required', []):
                if key not in value:
                    errors.append('%s: missing %s' % (loc, key))
            props = sch.get('properties', {})
            extra = sch.get('additionalProperties', True)
            for key, val in value.items():
                if key in props:
                    walk(val, props[key], '%s.%s' % (loc, key))
                elif extra is False:
                    errors.append('%s: unexpected %s' % (loc, key))
                elif isinstance(extra, dict):
                    walk(val, extra, '%s.%s' % (loc, key))
        if isinstance(value, list) and 'items' in sch:
            for idx, item in enumerate(value):
                walk(item, sch['items'], '%s[%d]' % (loc, idx))

    walk(instance, schema, path)
    return errors


def structural_schema_errors(instance, schema):
    """Full JSON Schema (Draft 2020-12) when available; subset otherwise.

    V2.1 N-15: schema/reference/input failures become stable E-SCHEMA* messages
    and never escape as raw exceptions. Unexpected engine programming errors
    are not swallowed: only the narrow schema/reference exception classes and
    basic container/type errors from a malformed schema or instance are handled.
    """
    if _JSONSCHEMA_AVAILABLE:
        try:
            cls = jsonschema.validators.validator_for(schema)
            cls.check_schema(schema)
            errors = sorted(
                cls(schema).iter_errors(instance),
                key=lambda e: (tuple((type(p).__name__, str(p)) for p in e.absolute_path), e.message))
            return ['E-SCHEMA: %s: %s' %
                    ('/'.join(str(p) for p in e.absolute_path) or '$', e.message)
                    for e in errors]
        except _SCHEMA_EXCEPTION_TYPES as exc:
            return ['E-SCHEMA-REFERENCE: %s' % brief(exc)]
        except (TypeError, AttributeError, ValueError, KeyError) as exc:
            return ['E-SCHEMA-INVALID: %s' % brief(exc)]
    try:
        return ['E-SCHEMA: %s' % err for err in validate_schema(instance, schema)]
    except (TypeError, AttributeError, ValueError, KeyError) as exc:
        return ['E-SCHEMA-INVALID: %s' % brief(exc)]


def valid_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return False
    return dt.tzinfo is not None and dt.utcoffset() is not None


def parse_timestamp(value):
    if not valid_timestamp(value):
        return None
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def pair_key(roles):
    return '+'.join(sorted(set(roles)))


def evidence_check(evidence, eid, expected_type, subject, dimension, issues, code_prefix='E-EVIDENCE'):
    """Resolve an evidence reference and enforce its structural guarantees.

    V2.1 additions: registry-key/evidence_id consistency, revocation and the
    requirement that the identity reference itself be a non-empty string.
    """
    if not isinstance(eid, str) or not eid.strip():
        issues.append(Issue('ERROR', code_prefix + '-MISSING', dimension,
                            message='Evidence reference is empty or not a string'))
        return None
    record = evidence.get(eid)
    if not isinstance(record, dict):
        issues.append(Issue('ERROR', code_prefix + '-UNKNOWN', dimension,
                            message='Unknown evidence id %s' % eid))
        return None
    if record.get('evidence_id') != eid:
        issues.append(Issue('ERROR', code_prefix + '-ID-MISMATCH', dimension,
                            message='Evidence id field does not match registry key: %s' % eid))
    if record.get('revoked') is True or record.get('revoked_at') is not None:
        issues.append(Issue('ERROR', code_prefix + '-REVOKED', dimension,
                            message='Evidence is revoked: %s' % eid))
    if record.get('evidence_type') != expected_type:
        issues.append(Issue('ERROR', code_prefix + '-TYPE', dimension,
                            message='Invalid evidence type for %s' % eid))
    if record.get('verification_status') != 'VERIFIED':
        issues.append(Issue('ERROR', code_prefix + '-UNVERIFIED', dimension,
                            message='Evidence not verified: %s' % eid))
    if not record.get('source_ref') or not meaningful_text(record.get('recording_authority')):
        issues.append(Issue('ERROR', code_prefix + '-INCOMPLETE', dimension,
                            message='Evidence missing source or recording authority: %s' % eid))
    if not valid_timestamp(record.get('timestamp')):
        issues.append(Issue('ERROR', 'E-TIMESTAMP-INVALID', dimension,
                            message='Evidence timestamp invalid or naive: %s' % eid))
    if subject and record.get('subject') != subject:
        issues.append(Issue('ERROR', code_prefix + '-SUBJECT', dimension,
                            message='Evidence subject mismatch: %s' % eid))
    h = record.get('content_hash')
    if h is not None and not re.fullmatch(r'[0-9a-fA-F]{64}', str(h)):
        issues.append(Issue('ERROR', code_prefix + '-HASH', dimension,
                            message='Invalid content hash: %s' % eid))
    return record


def acceptance_evidence_check(evidence, rec, ref, role, issues, used_decisions):
    """V2.1 N-03: bind acceptance evidence to one exact candidate and role.

    The evidence record must prove acceptance for this appointment: exact
    candidate ref and role in its subject, matching role and appointment_ref
    fields, a distinct decision reference, verified status, timezone-aware
    timestamp, recording authority and a non-revoked record.
    """
    subject = identity_subject(ref, role)
    record = evidence_check(evidence, rec.get('evidence_id'), 'CANDIDATE_ACCEPTANCE',
                            subject, 'evidence_integrity', issues,
                            code_prefix='E-EVIDENCE')
    if record is None:
        return
    if record.get('role') != role:
        issues.append(Issue('ERROR', 'E-ACCEPTANCE-ROLE', 'evidence_integrity', role=role,
                            candidate=str(ref),
                            message='Acceptance evidence is for a different role'))
    if record.get('appointment_ref') != subject:
        issues.append(Issue('ERROR', 'E-ACCEPTANCE-APPOINTMENT', 'evidence_integrity', role=role,
                            candidate=str(ref),
                            message='Acceptance evidence is for a different appointment'))
    decision_ref = record.get('decision_ref')
    if not meaningful_text(decision_ref):
        issues.append(Issue('ERROR', 'E-ACCEPTANCE-DECISION', 'evidence_integrity', role=role,
                            candidate=str(ref),
                            message='Acceptance decision reference is missing or empty'))
    else:
        if decision_ref in used_decisions and used_decisions[decision_ref] != subject:
            issues.append(Issue('ERROR', 'E-ACCEPTANCE-DECISION-REUSED', 'evidence_integrity',
                                role=role, candidate=str(ref),
                                message='Acceptance decision reference reused for another appointment'))
        used_decisions[decision_ref] = subject


def candidate_registry_check(candidates, policy, issues):
    seen = {}
    for key, rec in candidates.items():
        if not isinstance(rec, dict):
            issues.append(Issue('ERROR','E-CANDIDATE-RECORD','candidate data',candidate=key,message='Invalid candidate record'))
            continue
        ref = rec.get('candidate_ref')
        if ref != key or not ref:
            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=key,message='Candidate key/reference mismatch'))
        if ref in seen:
            issues.append(Issue('ERROR','E-CANDIDATE-DUPLICATE','candidate data',candidate=ref,message='Duplicate candidate identity'))
        seen[ref] = rec
        if rec.get('active') is not True:
            issues.append(Issue('ERROR','E-CANDIDATE-INACTIVE','candidate data',candidate=ref,message='Candidate registry entry inactive'))
    return seen


def validate_state(state, policy=None, schema=None):
    policy = policy or load_policy()
    schema = schema or load_schema()
    issues = []
    roles = policy['roles']
    formal_states = set(policy['formal_appointment_states'])
    dims = {k: 'PASS' for k in policy['stage_b_dimensions']}
    dims['structural_topology_validity'] = 'PASS'

    def dim(name):
        if name not in dims:
            dims[name] = 'PASS'

    def fail(dimension, code, role='', candidate='', message=''):
        issues.append(Issue('ERROR', code, dimension, role, candidate, message))
        if dimension in dims:
            dims[dimension] = 'FAIL'

    if not isinstance(state, dict):
        fail('structural_topology_validity', 'E-SCHEMA-INVALID',
             message='Assignment state is not a JSON object')
        return ValidationResult({k: 'FAIL' for k in dims}, issues, False)

    # V2.1 N-15: schema failure is terminal. Nothing below may dereference a
    # value that has not been proven to match the schema.
    schema_errors = structural_schema_errors(state, schema)
    if schema_errors:
        for err in schema_errors:
            code = 'E-SCHEMA'
            if err.startswith('E-SCHEMA-REFERENCE:'):
                code = 'E-SCHEMA-REFERENCE'
            elif err.startswith('E-SCHEMA-INVALID:'):
                code = 'E-SCHEMA-INVALID'
            fail('structural_topology_validity', code, message=err)
        return ValidationResult({k: 'FAIL' for k in dims}, issues, False)

    governance = state.get('governance', {})
    # No positive authorization may be inferred.
    if governance.get('recruitment') != 'UNAUTHORIZED' or governance.get('field_validation') != 'NOT_STARTED':
        fail('structural_topology_validity','E-AUTHORIZATION-STATE',message='Invalid authorization governance state')

    topology = state.get('topology', {})
    if topology.get('status') != 'APPROVED' and policy.get('require_topology_approved_for_stage_b'):
        fail('structural_topology_validity','E-TOPOLOGY-UNAPPROVED',message='Topology is PROPOSED; Stage B role readiness blocked')

    evidence = state.get('evidence', {}) if isinstance(state.get('evidence', {}), dict) else {}
    for eid, rec in evidence.items():
        if not isinstance(rec, dict):
            fail('evidence_integrity','E-EVIDENCE-RECORD',message='Invalid evidence record %s' % eid)
            continue
        if rec.get('evidence_type') not in policy['evidence_types']:
            fail('evidence_integrity','E-EVIDENCE-TYPE',message='Unknown evidence type %s' % eid)
        if rec.get('verification_status') not in policy['verification_statuses']:
            fail('evidence_integrity','E-EVIDENCE-UNVERIFIED',message='Unverified evidence %s' % eid)
        if not valid_timestamp(rec.get('timestamp')):
            fail('evidence_integrity','E-TIMESTAMP-INVALID',message='Evidence timestamp invalid %s' % eid)

    candidates = candidate_registry_check(
        state.get('candidates', {}) if isinstance(state.get('candidates', {}), dict) else {},
        policy, issues)
    if any(i.code.startswith('E-CANDIDATE-') for i in issues):
        dims['human_candidate_acceptance'] = 'FAIL'

    used_acceptance_decisions = {}
    role_records = state.get('roles', {}) if isinstance(state.get('roles', {}), dict) else {}
    for role in role_records:
        if role not in roles:
            fail('structural_topology_validity','E-ROLE-UNKNOWN',role=role,message='Unknown role')
    for role in roles:
        rec = role_records.get(role, {})
        st = rec.get('state')
        if st not in policy['appointment_states']:
            fail('role_assignment_completeness','E-STATE-INVALID',role=role,message='Invalid appointment state')
        if st not in formal_states:
            fail('role_assignment_completeness','E-APPOINTMENT-MISSING',role=role,
                 message='Role is not FORMALLY_APPOINTED')
            continue
        dim('human_candidate_acceptance'); dim('formal_appointment_validity')
        dim('onboarding_readiness')
        ref = rec.get('candidate_ref')
        if ref not in candidates:
            fail('formal_appointment_validity','E-CANDIDATE-UNKNOWN',role=role,candidate=str(ref),message='Unknown candidate')
        acc = rec.get('acceptance', {})
        appr = rec.get('approval', {})
        formal = rec.get('formal', {})
        if acc.get('candidate_accepted') is not True:
            fail('human_candidate_acceptance','E-CANDIDATE-ACCEPTANCE',role=role,candidate=str(ref),message='Candidate acceptance absent')
        acceptance_evidence_check(evidence, acc, ref, role, issues, used_acceptance_decisions)
        evidence_check(evidence, appr.get('evidence_id'), 'PRODUCT_OWNER_APPROVAL', ref,
                       'evidence_integrity', issues)
        evidence_check(evidence, formal.get('evidence_id'), 'FORMAL_APPOINTMENT', ref,
                       'evidence_integrity', issues)
        if appr.get('product_owner_approved') is not True:
            fail('formal_appointment_validity','E-PO-APPROVAL',role=role,message='Product Owner approval absent')
        if appr.get('formal') is not True:
            fail('formal_appointment_validity','E-FORMAL-APPROVAL-MISMATCH',role=role,message='FORMALLY_APPOINTED with formal=false')
        if not meaningful_text(appr.get('basis')):
            fail('formal_appointment_validity','E-DECISION-EVIDENCE-EMPTY',role=role,
                 message='Approval basis is missing, non-string or contains only whitespace')
        if formal.get('formally_appointed') is not True:
            fail('formal_appointment_validity','E-FORMAL-RECORD-MISSING',role=role,message='Formal record missing')
        for tfield in ['candidate_accepted_at','product_owner_approved_at','formal_appointed_at']:
            holder = acc if tfield == 'candidate_accepted_at' else (appr if tfield == 'product_owner_approved_at' else formal)
            if not valid_timestamp(holder.get(tfield)):
                fail('formal_appointment_validity','E-TIMESTAMP-MISSING',role=role,message='Missing timezone-aware timestamp %s' % tfield)
        ts_a = parse_timestamp(acc.get('candidate_accepted_at'))
        ts_p = parse_timestamp(appr.get('product_owner_approved_at'))
        ts_f = parse_timestamp(formal.get('formal_appointed_at'))
        if ts_a and ts_p and ts_f and not (ts_a <= ts_p <= ts_f):
            fail('formal_appointment_validity','E-TIMESTAMP-ORDER',role=role,message='Contradictory decision sequence')
        if rec.get('availability',{}).get('confirmed') is not True:
            fail('onboarding_readiness','E-AVAILABILITY',role=role,message='Availability not confirmed')
        if rec.get('conflict_disclosure',{}).get('provided') is not True:
            fail('onboarding_readiness','E-CONFLICT-DISCLOSURE',role=role,message='Conflict disclosure absent')
        if rec.get('confidentiality',{}).get('acknowledged') is not True:
            fail('onboarding_readiness','E-CONFIDENTIALITY',role=role,message='Confidentiality not acknowledged')
        if rec.get('onboarding',{}).get('completed') is not True:
            fail('onboarding_readiness','E-ONBOARDING',role=role,message='Onboarding incomplete')
        evidence_check(evidence, rec.get('onboarding',{}).get('evidence_id'), 'ONBOARDING', ref,
                       'evidence_integrity', issues)
        if not rec.get('escalation',{}).get('contact'):
            fail('onboarding_readiness','E-ESCALATION-CONTACT',role=role,message='Escalation contact absent')

    appointments = state.get('appointments', []) if isinstance(state.get('appointments', []), list) else []
    seen_app = set()
    by_candidate = {}
    for ap in appointments:
        if not isinstance(ap, dict):
            fail('role_assignment_completeness','E-APPOINTMENT-RECORD',message='Invalid appointment record')
            continue
        ref = ap.get('candidate_ref'); role = ap.get('role')
        key = (ref, role)
        if key in seen_app:
            fail('role_assignment_completeness','E-CANDIDATE-DUPLICATE',role=str(role),candidate=str(ref),message='Duplicate appointment')
        seen_app.add(key)
        if ref not in candidates:
            fail('human_candidate_acceptance','E-CANDIDATE-UNKNOWN',role=str(role),candidate=str(ref),message='Appointment references unknown candidate')
        if role not in roles:
            fail('structural_topology_validity','E-ROLE-UNKNOWN',role=str(role),message='Appointment references unknown role')
        if role_records.get(role,{}).get('state') not in formal_states:
            fail('role_assignment_completeness','E-UNAPPROVED-APPOINTMENT',role=str(role),candidate=str(ref),message='Appointment without formal role record')
        by_candidate.setdefault(ref, set()).add(role)
    for role in roles:
        if role_records.get(role,{}).get('state') in formal_states:
            ref = role_records[role].get('candidate_ref')
            if (ref, role) not in seen_app:
                fail('role_assignment_completeness','E-APPOINTMENT-RECORD',role=role,candidate=str(ref),message='Formal role lacks appointment record')

    approvals = state.get('combination_approvals', []) if isinstance(state.get('combination_approvals', []), list) else []
    approval_map = {}
    used_rationales = {}
    for ca in approvals:
        if not isinstance(ca, dict):
            fail('product_owner_combination_approval','E-COMBINATION-APPROVAL-RECORD',message='Invalid combination approval')
            continue
        key = (ca.get('candidate_ref'), pair_key(ca.get('roles', [])))
        approval_map[key] = ca
        if ca.get('outcome') != 'APPROVED':
            fail('product_owner_combination_approval','E-COMBINATION-APPROVAL-REJECTED',candidate=str(ca.get('candidate_ref')),message='Combination not approved')
        if ca.get('product_owner_approved') is not True:
            fail('product_owner_combination_approval','E-PO-APPROVAL',candidate=str(ca.get('candidate_ref')),message='Combination lacks PO approval')
        rationale = ca.get('rationale')
        if not meaningful_text(rationale):
            fail('product_owner_combination_approval', 'E-COMBINATION-RATIONALE',
                 candidate=str(ca.get('candidate_ref')),
                 message='Combination rationale is missing, non-string or contains only whitespace')
        else:
            normalized = ' '.join(rationale.split())
            if normalized in used_rationales and used_rationales[normalized] != key:
                fail('product_owner_combination_approval', 'E-COMBINATION-RATIONALE-REUSED',
                     candidate=str(ca.get('candidate_ref')),
                     message='Rationale reused from another combination decision')
            used_rationales[normalized] = key
        evidence_check(evidence, ca.get('evidence_id'), 'COMBINATION_REVIEW',
                       '%s:%s' % (ca.get('candidate_ref'), key[1]), 'evidence_integrity', issues)
        if not valid_timestamp(ca.get('decision_timestamp')):
            fail('product_owner_combination_approval','E-TIMESTAMP-INVALID',candidate=str(ca.get('candidate_ref')),message='Combination decision timestamp invalid')

    for candidate, held in by_candidate.items():
        if len(held) <= 1:
            continue
        key = (candidate, pair_key(held))
        ca = approval_map.get(key)
        if not ca:
            fail('product_owner_combination_approval','E-COMBINATION-APPROVAL-MISSING',candidate=str(candidate),
                 message='No exact Product Owner approval for combination %s' % key[1])
        for combo in policy['hard_incompatibilities']:
            if set(combo['roles']).issubset(held):
                fail('role_compatibility',combo['code'],message='Hard incompatibility cannot be approved')
        for combo in policy['discouraged_combinations']:
            if set(combo['roles']).issubset(held) and not ca:
                fail('role_compatibility',combo['code'],message='Discouraged combination lacks PO review')
        for combo in policy['conditional_combinations']:
            if not set(combo['roles']).issubset(held):
                continue
            if combo['requirement'] == 'evidence_separation':
                found = any(
                    e.get('evidence_type')=='EVIDENCE_SEPARATION' and
                    e.get('subject')=='%s:%s' % (candidate, pair_key(held)) and
                    e.get('verification_status')=='VERIFIED'
                    for e in evidence.values() if isinstance(e, dict))
                if not found:
                    fail('role_compatibility','E-COND-EVIDENCE-SEPARATION',message='Evidence separation record missing')
            if combo['requirement'] == 'explicit_additional_appointment':
                if role_records.get('CONTINUE_STOP_OWNER',{}).get('state') not in formal_states or not ca:
                    fail('role_compatibility','E-COND-EXPLICIT-CS',message='No explicit Continue/Stop appointment evidence')

    stage_b = (topology.get('status')=='APPROVED' and
               all(dims.get(k)=='PASS' for k in policy['stage_b_dimensions']) and
               not issues)
    return ValidationResult(dims, issues, stage_b, False, False)


def human_report(result, source_name):
    lines = ['M001 TEAM ASSIGNMENT VALIDATION V2', 'Source: %s' % source_name]
    for k, v in sorted(result.dimensions.items()):
        lines.append('%s: %s' % (k, v))
    lines.append('Stage B role readiness: %s' % ('YES' if result.stage_b_role_ready else 'NO'))
    lines.append('Recruitment authorized: NO')
    lines.append('Field validation authorized: NO')
    lines.append('Blocking errors: %d' % len(result.errors))
    lines.append('Warnings: %d' % len(result.warnings))
    for issue in result.sorted_issues():
        extra = []
        if issue.dimension: extra.append('dimension=%s' % issue.dimension)
        if issue.role: extra.append('role=%s' % issue.role)
        if issue.candidate: extra.append('candidate=%s' % issue.candidate)
        lines.append('%s %s%s: %s' % (issue.severity, issue.code,
                                      (' ['+', '.join(extra)+']') if extra else '', issue.message))
    lines.append('END REPORT')
    return '\n'.join(lines)


def json_result(result, source_name):
    payload = result.to_dict()
    payload['source'] = source_name
    payload['engine'] = 'M001_TEAM_ASSIGNMENT_ENGINE_V2'
    return json.dumps(payload, indent=2, sort_keys=True)
