"""Host-reviewed issue and fix records with honest local adoption evidence.

These records neither execute repairs nor certify the truth of a supplied
reference. The host reviews that evidence; the engine preserves its condition
and revision, and independently inspects project-local setup when asked.
"""
from __future__ import annotations

from .core import Core, _id
from .setup import runtime_info
from .store import GovernanceError, now


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise GovernanceError('INVALID_ARGUMENT', label + ' must be nonempty text.')
    return value


def _revision(expected, previous):
    if expected is not None and (isinstance(expected, bool) or not isinstance(expected, int) or expected < 0):
        raise GovernanceError('INVALID_ARGUMENT', 'expected_revision must be a nonnegative integer.')
    actual = previous['revision'] if previous else 0
    if (previous is not None and expected != actual) or (previous is None and expected not in (None, 0)):
        raise GovernanceError('REVISION_CONFLICT', 'The record changed; review its current revision before updating.',
                              {'expected_revision': expected, 'actual_revision': actual})
    return actual + 1


class Maintenance(Core):
    def _record(self, collection, key, body, expected_revision):
        """Called inside one transaction, including the matching audit event."""
        if expected_revision is not None and (isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 0):
            raise GovernanceError('INVALID_ARGUMENT', 'expected_revision must be a nonnegative integer.')
        previous = self.store.get(collection, key)
        if previous and all(previous.get(name) == value for name, value in body.items()):
            # Identical observations are not new work and need no empty event.
            return previous, True
        revision = _revision(expected_revision, previous)
        timestamp = now()
        record = dict(body, revision=revision, created_at=previous['created_at'] if previous else timestamp,
                      updated_at=timestamp)
        self.store.put(collection, key, record)
        self.store.put(collection + '_history', key + '.' + str(revision), record)
        self.store.event({'issues': 'issue_recorded', 'fixes': 'fix_recorded'}[collection], record)
        return record, False

    def issue(self, issue_id, condition, summary, state='open', resolution_ref='', expected_revision=None):
        issue_id = _id(issue_id, 'Issue ID')
        _text(condition, 'condition')
        _text(summary, 'summary')
        if state not in ('open', 'resolved'):
            raise GovernanceError('INVALID_STATE', 'Issue state must be open or resolved.')
        if not isinstance(resolution_ref, str):
            raise GovernanceError('INVALID_ARGUMENT', 'resolution_ref must be text.')
        if state == 'resolved':
            _text(resolution_ref, 'A resolved issue needs a reviewed resolution reference')
        elif resolution_ref:
            raise GovernanceError('INVALID_ARGUMENT', 'An open issue must not retain a current resolution reference.')
        with self.store.transaction():
            previous = self.store.get('issues', issue_id)
            if previous and previous['condition'] != condition and state == 'resolved':
                raise GovernanceError('CONDITION_CHANGED_REOPEN',
                                      'A changed condition must be recorded open before a new resolution is reviewed.')
            body = {'issue_id': issue_id, 'condition': condition, 'summary': summary,
                    'state': state, 'resolution_ref': resolution_ref, 'evidence_scope': 'host_reviewed_reference'}
            record, reused = self._record('issues', issue_id, body, expected_revision)
        return {'issue': record, 'reused': reused}

    def _adoption(self, fix):
        """Check the existing disk/setup evidence; do not install or reload."""
        info = runtime_info(self.root)
        runtime = info.get('loaded_runtime') or {}
        version_matches = info.get('managed_setup_version') == fix['version'] == runtime.get('version')
        reasons = []
        for valid, reason in (
            (info.get('setup_status') == 'installed', 'setup_not_installed'),
            (not info.get('pending_installation'), 'setup_incomplete'),
            (version_matches, 'version_not_matched'),
            (info.get('managed_runtime_matches_disk') is True, 'runtime_disk_not_matched'),
            (info.get('managed_files_match') is True and info.get('generated_files_match') is True,
             'managed_files_not_matched'),
        ):
            if not valid:
                reasons.append(reason)
        matched = not reasons
        return {'status': 'installed_version_matches' if matched else 'recorded',
                'installed_version_matches': matched, 'fix_version': fix['version'],
                'managed_setup_version': info.get('managed_setup_version'),
                'current_package_version': runtime.get('version'),
                'source_sha256': runtime.get('source_sha256'), 'source_fingerprint_scope': 'on_disk',
                'setup_status': info.get('setup_status'), 'reasons': reasons,
                'host_reload_unverified': True, 'loaded_code_verified': False,
                'package_upgrade_performed': False, 'repair_execution_verified': False}

    def fix(self, fix_id, issue_id, version, evidence_refs, summary='', expected_revision=None):
        fix_id = _id(fix_id, 'Fix ID')
        issue_id = _id(issue_id, 'Issue ID')
        _text(version, 'version')
        if not isinstance(summary, str):
            raise GovernanceError('INVALID_ARGUMENT', 'summary must be text.')
        if not isinstance(evidence_refs, list) or not evidence_refs:
            raise GovernanceError('INVALID_ARGUMENT', 'A fix needs at least one reviewed evidence reference.')
        for ref in evidence_refs:
            _text(ref, 'evidence_refs item')
        refs = sorted(set(evidence_refs))
        with self.store.transaction():
            issue = self.store.get('issues', issue_id)
            if not issue:
                raise GovernanceError('ISSUE_NOT_FOUND', 'Register the issue before linking a fix.')
            body = {'fix_id': fix_id, 'issue_id': issue_id, 'condition': issue['condition'],
                    'version': version, 'evidence_refs': refs, 'summary': summary,
                    'evidence_scope': 'host_reviewed_reference'}
            record, reused = self._record('fixes', fix_id, body, expected_revision)
        # Installation is a fresh read, never a persistent claim derived from
        # a past check. Reading the same fix after setup can show new adoption
        # without emitting a duplicate fix event or closing its issue.
        return {'fix': record, 'reused': reused, 'adoption': self._adoption(record)}
