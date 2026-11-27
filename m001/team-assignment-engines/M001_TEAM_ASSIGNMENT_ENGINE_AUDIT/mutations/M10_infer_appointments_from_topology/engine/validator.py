#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Deterministic validator for the M001 research team assignment state.

Diagnostic engineering tool. It does not appoint people, change governance,
configure storage or authorize research execution.
"""
from dataclasses import dataclass, asdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEVERITY_ORDER = {'ERROR': 0, 'WARNING': 1, 'INFO': 2}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    role: str = ''
    person: str = ''
    message: str = ''

    def to_dict(self):
        return asdict(self)


@dataclass
class ValidationResult:
    issues: list

    @property
    def errors(self):
        return [i for i in self.issues if i.severity == 'ERROR']

    @property
    def warnings(self):
        return [i for i in self.issues if i.severity == 'WARNING']

    @property
    def info(self):
        return [i for i in self.issues if i.severity == 'INFO']

    @property
    def valid(self):
        return not self.errors

    def sorted_issues(self):
        return sorted(self.issues, key=lambda i: (
            SEVERITY_ORDER.get(i.severity, 9), i.code, i.role, i.person, i.message))

    def to_dict(self):
        return {
            'valid': self.valid,
            'blocking_error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'info_count': len(self.info),
            'issues': [i.to_dict() for i in self.sorted_issues()]
        }


def load_json(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def load_policy(path=None):
    return load_json(path or ROOT / 'policy' / 'role_constraints.json')


def load_schema(path=None):
    return load_json(path or ROOT / 'schemas' / 'team_assignment.schema.json')


def validate_schema(instance, schema, path='$'):
    """Small deterministic JSON Schema subset validator (standard library only).

    Supports: type (including list of types), required, properties,
    additionalProperties, enum, items, and local $ref definitions. This is
    intentionally not a complete JSON Schema implementation.
    """
    errors = []

    def resolve(ref):
        if not ref.startswith('#/'):
            return None
        node = schema
        for part in ref[2:].split('/'):
            node = node.get(part)
            if node is None:
                return None
        return node

    def type_ok(value, expected):
        expected_types = expected if isinstance(expected, list) else [expected]
        mapping = {
            'object': dict, 'array': list, 'string': str, 'boolean': bool,
            'null': type(None)
        }
        for t in expected_types:
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
                errors.append('%s: unresolved schema reference %s' % (loc, sch['$ref']))
                return
            walk(value, target, loc)
            return
        if 'type' in sch and not type_ok(value, sch['type']):
            errors.append('%s: expected type %s' % (loc, sch['type']))
            return
        if 'enum' in sch and value not in sch['enum']:
            errors.append('%s: value not in enum' % loc)
        if isinstance(value, dict):
            required = sch.get('required', [])
            for key in required:
                if key not in value:
                    errors.append('%s: missing required field %s' % (loc, key))
            props = sch.get('properties', {})
            if sch.get('additionalProperties') is False:
                for key in value:
                    if key not in props:
                        errors.append('%s: additional property %s' % (loc, key))
            for key, sub in props.items():
                if key in value:
                    walk(value[key], sub, '%s.%s' % (loc, key))
        if isinstance(value, list) and 'items' in sch:
            for idx, item in enumerate(value):
                walk(item, sch['items'], '%s[%d]' % (loc, idx))

    walk(instance, schema, path)
    return errors


def _pair_key(pair):
    return '+'.join(sorted(pair))


def _role_record(state, role):
    return state.get('roles', {}).get(role, {})


def _state_of(state, role):
    return _role_record(state, role).get('state', 'UNASSIGNED')


def _requirement_present(record, req):
    if req == 'candidate_id':
        return bool(record.get('candidate_id'))
    if req == 'acceptance_evidence':
        return bool(record.get('acceptance', {}).get('evidence'))
    if req == 'candidate_acceptance':
        return record.get('acceptance', {}).get('candidate_accepted') is True
    if req == 'product_owner_approval':
        return record.get('approval', {}).get('product_owner_approved') is True
    if req == 'availability_confirmation':
        return record.get('availability', {}).get('confirmed') is True
    if req == 'conflict_disclosure':
        return record.get('conflict_disclosure', {}).get('provided') is True
    if req == 'confidentiality_acknowledgement':
        return record.get('confidentiality', {}).get('acknowledged') is True
    if req == 'escalation_contact':
        return bool(record.get('escalation', {}).get('contact'))
    if req == 'onboarding_completion':
        return record.get('onboarding', {}).get('completed') is True
    return False


def validate_state(state, policy=None, schema=None):
    """Validate a team assignment state against machine-readable policy."""
    policy = policy or load_policy()
    schema = schema or load_schema()
    issues = []

    for err in validate_schema(state, schema):
        issues.append(Issue('ERROR', 'E-SCHEMA', message=err))

    roles = policy['roles']
    states = policy['appointment_states']
    role_records = state.get('roles', {}) if isinstance(state, dict) else {}
    assignments = state.get('assignments', []) if isinstance(state, dict) else []

    # Unknown roles and invalid states
    for role in role_records:
        if role not in roles:
            issues.append(Issue('ERROR', 'E-ROLE-UNKNOWN', role=role,
                                message='Unknown role identifier'))
    for assignment in assignments:
        for role in assignment.get('roles', []):
            if role not in roles:
                issues.append(Issue('ERROR', 'E-ROLE-UNKNOWN', role=role,
                                    person=assignment.get('person_id', ''),
                                    message='Unknown role identifier in assignment'))
    for role, record in role_records.items():
        if role in roles and record.get('state') not in states:
            issues.append(Issue('ERROR', 'E-STATE-INVALID', role=role,
                                message='Invalid appointment state'))

    # Duplicate roles
    seen = {}
    for assignment in assignments:
        person = assignment.get('person_id', '')
        listed = assignment.get('roles', [])
        if len(listed) != len(set(listed)):
            issues.append(Issue('ERROR', 'E-ROLE-DUPLICATE', person=person,
                                message='Role listed more than once for one person'))
        for role in listed:
            if role in seen:
                issues.append(Issue('ERROR', 'E-ROLE-DUPLICATE', role=role,
                                    person=person,
                                    message='Role assigned to more than one person; first=%s' % seen[role]))
            else:
                seen[role] = person

    # Missing appointments
    for role in roles:
        if _state_of(state, role) in policy['missing_appointment_states']:
            issues.append(Issue('ERROR', 'E-APPOINTMENT-MISSING', role=role,
                                message='Role is not appointed'))

    # Assigned role recorded as UNASSIGNED
    for role, person in seen.items():
        if _state_of(state, role) == 'UNASSIGNED':
            issues.append(Issue('ERROR', 'E-UNASSIGNED-ASSIGNED', role=role, person=person,
                                message='Role assigned to a person while state is UNASSIGNED'))

    # State-specific completeness requirements
    for role in roles:
        record = _role_record(state, role)
        st = record.get('state', 'UNASSIGNED')
        for req in policy['state_requirements'].get(st, []):
            if not _requirement_present(record, req):
                code = policy['requirement_codes'][req]
                issues.append(Issue('ERROR', code, role=role,
                                    message='Missing required evidence: %s' % req))

    # Combination policy
    for assignment in assignments:
        person = assignment.get('person_id', '')
        held = set(assignment.get('roles', []))
        conditional = assignment.get('conditional_evidence', {})
        resolutions = assignment.get('resolutions', {})

        for combo in policy['hard_incompatibilities']:
            pair = combo['roles']
            if set(pair).issubset(held):
                issues.append(Issue('ERROR', combo['code'], person=person,
                                    role=_pair_key(pair), message=combo['message']))

        for combo in policy['discouraged_combinations']:
            pair = combo['roles']
            if set(pair).issubset(held):
                resolved = resolutions.get(_pair_key(pair), {}).get('rationale_documented') is True
                if not resolved:
                    issues.append(Issue('WARNING', combo['code'], person=person,
                                        role=_pair_key(pair), message=combo['message']))

        for combo in policy['conditional_combinations']:
            pair = combo['roles']
            if set(pair).issubset(held):
                if conditional.get(combo['requirement']) is not True:
                    issues.append(Issue('ERROR', combo['code'], person=person,
                                        role=_pair_key(pair),
                                        message='Missing conditional evidence: %s' % combo['requirement']))

        if 'RESEARCH_OWNER' in held and 'CONTINUE_STOP_OWNER' in held:
            cs_state = _state_of(state, 'CONTINUE_STOP_OWNER')
            if cs_state in ('UNASSIGNED', 'DEFERRED', 'REJECTED', 'PROPOSED'):
                issues.append(Issue('ERROR', 'E-COND-EXPLICIT-CS', person=person,
                                    role='CONTINUE_STOP_OWNER',
                                    message='Research Owner acceptance does not imply Continue/Stop Owner appointment'))

    # Topology remains a proposal until explicitly approved
    topology = state.get('topology', {}) if isinstance(state, dict) else {}
    if topology.get('status') == 'PROPOSED':
        issues.append(Issue('WARNING', 'W-TOPOLOGY-PROPOSED',
                            message='Team topology remains PROPOSED; no staffing model is approved'))

    # State distinction notices
    if _state_of(state, 'RESEARCH_OWNER') == 'ACCEPTED_IN_CONVERSATION':
        issues.append(Issue('INFO', 'I-RO-NOT-FORMAL', role='RESEARCH_OWNER',
                            message='ACCEPTED_IN_CONVERSATION is not FORMALLY_APPOINTED'))

    return ValidationResult(issues)


def human_report(result, source_name):
    lines = [
        'M001 TEAM ASSIGNMENT VALIDATION',
        'Source: %s' % source_name,
        'Valid: %s' % ('YES' if result.valid else 'NO'),
        'Blocking errors: %d' % len(result.errors),
        'Warnings: %d' % len(result.warnings),
        'Info: %d' % len(result.info),
        ''
    ]
    for issue in result.sorted_issues():
        suffix = ''
        if issue.role:
            suffix += ' role=%s' % issue.role
        if issue.person:
            suffix += ' person=%s' % issue.person
        lines.append('%s %s%s: %s' % (issue.severity, issue.code, suffix, issue.message))
    lines.append('')
    lines.append('END REPORT')
    return '\n'.join(lines)


def json_result(result, source_name):
    payload = result.to_dict()
    payload['source'] = source_name
    return json.dumps(payload, indent=2, sort_keys=True)
