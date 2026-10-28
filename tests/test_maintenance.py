"""Synthetic issue/fix continuity; no external host or project mutation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from taskcarry import __version__
from taskcarry.core import Core
from taskcarry.maintenance import Maintenance
from taskcarry.setup import configure
from taskcarry.store import GovernanceError


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='taskcarry-maintenance-')
        self.project = Path(self.temp.name) / 'project'
        Core.initialize(self.project, 'Synthetic maintenance')
        self.engine = Maintenance(self.project)

    def tearDown(self):
        self.temp.cleanup()

    def issue(self, **kwargs):
        return self.engine.issue('receipt-gap', 'receipt-v1', 'Synthetic interrupted receipt', **kwargs)

    def fix(self, **kwargs):
        return self.engine.fix('atomic-receipt', 'receipt-gap', __version__,
                               ['test:receipt-recovery', 'commit:synthetic-fix'], **kwargs)

    def assertCode(self, code, operation):
        with self.assertRaises(GovernanceError) as context:
            operation()
        self.assertEqual(code, context.exception.code)

    def test_identical_issue_and_fix_do_not_add_empty_events(self):
        first = self.issue()
        fix = self.fix()
        before = self.engine.store.events()
        self.assertTrue(self.issue()['reused'])
        self.assertTrue(self.fix()['reused'])
        self.assertEqual(before, self.engine.store.events())
        self.assertEqual(1, first['issue']['revision'])
        self.assertEqual(1, fix['fix']['revision'])
        self.assertEqual('recorded', fix['adoption']['status'])
        self.assertFalse(fix['adoption']['installed_version_matches'])
        self.assertEqual('open', self.engine.store.get('issues', 'receipt-gap')['state'])

    def test_changed_record_requires_cas_and_retains_history(self):
        self.issue()
        self.assertCode('REVISION_CONFLICT', lambda: self.issue(state='resolved', resolution_ref='test:confirmed'))
        self.assertCode('REVISION_CONFLICT', lambda: self.issue(state='resolved', resolution_ref='test:confirmed', expected_revision=0))
        self.issue(state='resolved', resolution_ref='test:confirmed', expected_revision=1)
        record = self.engine.store.get('issues', 'receipt-gap')
        self.assertEqual(2, record['revision'])
        history = self.engine.store.list('issues_history')
        self.assertEqual(['open', 'resolved'], [item['state'] for item in history])
        self.fix()
        self.assertCode('REVISION_CONFLICT', lambda: self.fix(summary='Evidence clarified'))
        changed = self.fix(summary='Evidence clarified', expected_revision=1)
        self.assertEqual(2, changed['fix']['revision'])
        self.assertEqual(2, len(self.engine.store.list('fixes_history')))

    def test_changed_condition_cannot_reuse_old_resolution(self):
        self.issue()
        self.issue(state='resolved', resolution_ref='test:original', expected_revision=1)
        self.fix()
        self.assertCode('CONDITION_CHANGED_REOPEN', lambda: self.engine.issue(
            'receipt-gap', 'receipt-v2', 'Changed condition', state='resolved',
            resolution_ref='test:original', expected_revision=2))
        changed = self.engine.issue('receipt-gap', 'receipt-v2', 'Changed condition', expected_revision=2)
        self.assertEqual('open', changed['issue']['state'])
        self.assertEqual('', changed['issue']['resolution_ref'])
        self.assertCode('REVISION_CONFLICT', lambda: self.fix())
        self.assertEqual('receipt-v1', self.engine.store.get('fixes', 'atomic-receipt')['condition'])
        updated = self.fix(expected_revision=1)
        self.assertEqual('receipt-v2', updated['fix']['condition'])

    def test_resolution_and_fix_require_named_evidence(self):
        self.assertCode('INVALID_ARGUMENT', lambda: self.issue(state='resolved'))
        self.assertCode('INVALID_ARGUMENT', lambda: self.issue(resolution_ref='test:old'))
        self.assertCode('ISSUE_NOT_FOUND', lambda: self.fix())
        self.issue()
        self.assertCode('INVALID_ARGUMENT', lambda: self.engine.fix('fix', 'receipt-gap', __version__, []))
        self.assertCode('INVALID_ARGUMENT', lambda: self.engine.fix('fix', 'receipt-gap', __version__, [' ']))

    def test_forged_version_label_alone_cannot_claim_adoption(self):
        self.issue()
        # A label without managed file/runtime proof is not installation.
        manifest = self.project / '.taskcarry' / 'setup-manifest.json'
        manifest.write_text(json.dumps({'format': 1, 'files': {}, 'runtime': {'version': __version__}}), encoding='utf-8')
        result = self.fix()
        self.assertEqual('recorded', result['adoption']['status'])
        self.assertEqual('unavailable', result['adoption']['setup_status'])
        self.assertFalse(result['adoption']['installed_version_matches'])
        self.assertFalse(result['adoption']['package_upgrade_performed'])
        self.assertEqual('open', self.engine.store.get('issues', 'receipt-gap')['state'])

    def test_real_project_setup_matches_disk_but_not_host_reload(self):
        self.issue()
        configure(self.project, mode='install')
        result = self.fix()
        self.assertTrue(result['adoption']['installed_version_matches'])
        self.assertEqual('installed_version_matches', result['adoption']['status'])
        self.assertTrue(result['adoption']['host_reload_unverified'])
        self.assertFalse(result['adoption']['loaded_code_verified'])
        self.assertFalse(result['adoption']['repair_execution_verified'])
        self.assertFalse(result['adoption']['package_upgrade_performed'])
        self.assertEqual('open', self.engine.store.get('issues', 'receipt-gap')['state'])
        before = self.engine.store.events()
        target = self.project / '.taskcarry' / 'codex.mcp.toml'
        target.write_text(target.read_text(encoding='utf-8') + '\n# User changed file\n', encoding='utf-8')
        updated = self.fix()
        self.assertTrue(updated['reused'])
        self.assertFalse(updated['adoption']['installed_version_matches'])
        self.assertEqual('modified', updated['adoption']['setup_status'])
        self.assertEqual(before, self.engine.store.events())

    def test_different_fix_version_remains_recorded_without_blocking_work(self):
        self.issue()
        configure(self.project, mode='install')
        result = self.engine.fix('future-fix', 'receipt-gap', '999.0', ['test:future'])
        self.assertFalse(result['adoption']['installed_version_matches'])
        self.assertIn('version_not_matched', result['adoption']['reasons'])
        self.engine.task('ordinary-work', state='active')
        self.assertEqual('active', self.engine.store.get('tasks', 'ordinary-work')['state'])

    def test_issue_and_fix_events_fail_atomically(self):
        before = self.engine.store.events()
        with mock.patch.object(self.engine.store, 'event', side_effect=OSError('synthetic failure')):
            with self.assertRaises(OSError):
                self.issue()
        self.assertIsNone(self.engine.store.get('issues', 'receipt-gap'))
        self.assertEqual([], self.engine.store.list('issues_history'))
        self.assertEqual(before, self.engine.store.events())
        self.issue()
        before = self.engine.store.events()
        with mock.patch.object(self.engine.store, 'event', side_effect=OSError('synthetic failure')):
            with self.assertRaises(OSError):
                self.fix()
        self.assertIsNone(self.engine.store.get('fixes', 'atomic-receipt'))
        self.assertEqual([], self.engine.store.list('fixes_history'))
        self.assertEqual(before, self.engine.store.events())
        self.assertFalse(self.fix()['reused'])


if __name__ == '__main__':
    unittest.main()
