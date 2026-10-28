"""Atomic local receipts; no real project, scheduler or remote side effects."""
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from taskcarry.core import Core
from taskcarry.store import Store


class AtomicStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='taskcarry-atomic-')
        self.root = Path(self.temp.name)
        self.project = self.root / 'control'
        Core.initialize(self.project, 'Synthetic atomic receipts')
        self.core = Core(self.project)
        self.store = self.core.store

    def tearDown(self):
        self.temp.cleanup()

    def test_task_event_failure_rolls_back_fact_and_retry_publishes_one_event(self):
        before = self.store.events()
        with mock.patch.object(self.store, 'event', side_effect=OSError('synthetic event failure')):
            with self.assertRaises(OSError):
                self.core.task('draft', 'Synthetic draft')
        reopened = Core(self.project)
        self.assertIsNone(reopened.store.get('tasks', 'draft'))
        self.assertEqual(before, reopened.store.events())
        self.assertEqual([], reopened.agenda()['items'])
        reopened.task('draft', 'Synthetic draft')
        reopened.task('draft', 'Synthetic draft')
        changed = [event for event in reopened.store.events() if event['kind'] == 'task_changed']
        self.assertEqual(1, len(changed))
        self.assertEqual('draft', changed[0]['payload']['task_id'])

    def test_checkpoint_event_failure_keeps_task_and_source_then_retry_succeeds(self):
        self.core.task('draft', state='active')
        workspace = self.root / 'author'
        workspace.mkdir()
        content = b'Synthetic unfinished work\r\n'
        (workspace / 'draft.txt').write_bytes(content)
        before_task, before_events = self.store.get('tasks', 'draft'), self.store.events()
        with mock.patch.object(self.store, 'event', side_effect=OSError('synthetic event failure')):
            with self.assertRaises(OSError):
                self.core.checkpoint('draft', workspace, ['draft.txt'], 'Continue editing', paused=True)
        reopened = Core(self.project)
        self.assertEqual(before_task, reopened.store.get('tasks', 'draft'))
        self.assertEqual([], reopened.store.list('checkpoints'))
        self.assertEqual(before_events, reopened.store.events())
        self.assertEqual(content, (workspace / 'draft.txt').read_bytes())
        result = reopened.checkpoint('draft', workspace, ['draft.txt'], 'Continue editing', paused=True)
        task = reopened.store.get('tasks', 'draft')
        self.assertEqual('paused', task['state'])
        self.assertEqual(result['checkpoint_id'], task['latest_checkpoint'])
        self.assertEqual(1, len(reopened.store.list('checkpoints')))
        self.assertEqual(1, sum(event['kind'] == 'checkpoint_saved' for event in reopened.store.events()))

    def test_artifact_event_failure_cannot_leave_an_unrecorded_decision(self):
        self.core.task('draft')
        artifact = self.root / 'material.txt'
        artifact.write_text('Synthetic material', encoding='utf-8')
        original = self.core.artifact('draft', artifact)
        with mock.patch.object(self.store, 'event', side_effect=OSError('synthetic event failure')):
            with self.assertRaises(OSError):
                self.core.artifact('draft', artifact, decision='no_backup_needed')
        reopened = Core(self.project)
        self.assertEqual(original, reopened.store.get('artifacts', original['artifact_id']))
        self.assertEqual(1, reopened.agenda()['counts']['artifacts'])
        reopened.artifact('draft', artifact, decision='no_backup_needed')
        self.assertEqual(0, reopened.agenda()['counts']['artifacts'])

    def test_experience_event_failure_preserves_previous_rule(self):
        original = self.store.get('experience', 'receipt-recovery-v1')
        with mock.patch.object(self.store, 'event', side_effect=OSError('synthetic event failure')):
            with self.assertRaises(OSError):
                self.core.experience('receipt-recovery-v1', 'OTHER', 'reconcile', 'refresh_plan')
        self.assertEqual(original, Store(self.project).get('experience', 'receipt-recovery-v1'))

    def test_nested_savepoint_reads_own_writes_and_inner_failure_isolated(self):
        with self.store.transaction():
            self.store.put('tasks', 'outer', {'task_id': 'outer', 'state': 'active'})
            self.assertIsNotNone(self.store.get('tasks', 'outer'))
            self.assertEqual(1, len(self.store.snapshot_current()['tasks']))
            try:
                with self.store.transaction():
                    self.store.put('tasks', 'inner', {'task_id': 'inner', 'state': 'active'})
                    self.store.event('inner_event', {})
                    raise OSError('synthetic nested failure')
            except OSError:
                pass
            self.assertIsNone(self.store.get('tasks', 'inner'))
            self.store.event('outer_event', {})
        reopened = Store(self.project)
        self.assertEqual(['outer'], [task['task_id'] for task in reopened.list('tasks')])
        self.assertNotIn('inner_event', [event['kind'] for event in reopened.events()])
        self.assertIn('outer_event', [event['kind'] for event in reopened.events()])

    def test_guard_preserves_effect_journal_when_external_operation_raises(self):
        with self.assertRaises(OSError):
            with self.store.guard():
                self.store.put('operations', 'effect', {'operation_id': 'effect', 'status': 'EFFECT_APPLIED'})
                self.store.event('effect_recorded', {})
                raise OSError('external Git acknowledgment interrupted')
        reopened = Core(self.project)
        self.assertEqual('EFFECT_APPLIED', reopened.store.get('operations', 'effect')['status'])
        self.assertEqual(1, reopened.agenda()['counts']['operations'])
        self.assertIn('effect_recorded', [event['kind'] for event in reopened.store.events()])


if __name__ == '__main__':
    unittest.main()
