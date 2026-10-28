"""Explicit legacy upgrades and indexed, history-independent agenda selection."""
from contextlib import closing, contextmanager
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from taskcarry.core import Core
from taskcarry.store import GovernanceError, Store


class IncrementalViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='taskcarry-incremental-')
        self.project = Path(self.temp.name) / 'control'
        Core.initialize(self.project, 'Synthetic indexed view')
        self.core = Core(self.project)
        self.store = self.core.store
        self.core.task('work', 'Synthetic work')

    def tearDown(self):
        self.temp.cleanup()

    def legacy(self):
        with closing(sqlite3.connect(self.store.path)) as db:
            with db:
                for operation in ('insert', 'update', 'delete'):
                    db.execute('DROP TRIGGER current_records_dirty_' + operation)
                db.execute('DROP TABLE current_records')
                db.execute('DROP TABLE store_schema')

    def state(self):
        with closing(sqlite3.connect(self.store.path)) as db:
            return (db.execute('SELECT * FROM records ORDER BY collection,key').fetchall(),
                    db.execute('SELECT * FROM events ORDER BY sequence').fetchall())

    def stage(self, identity, status='QUEUED', **fields):
        self.store.put('stages', identity, {'stage_id': identity, 'task_id': 'work', 'status': status,
                                          'workspace': 'author', **fields})

    def test_legacy_reads_and_reinitialize_do_not_install_projection(self):
        self.stage('delivery')
        self.legacy()
        before = self.state()
        reopened = Core(self.project)
        result = reopened.agenda()
        self.assertEqual('legacy_full_scan', result['storage']['mode'])
        self.assertTrue(result['storage']['upgrade_required'])
        self.assertTrue(reopened.status()['storage']['upgrade_required'])
        self.assertEqual(['stage:delivery'], [item['id'] for item in result['items']])
        Core.initialize(self.project, 'Ignored replacement')
        self.assertEqual(before, self.state())
        with closing(sqlite3.connect(self.store.path)) as db:
            self.assertIsNone(db.execute("SELECT 1 FROM sqlite_master WHERE name='current_records'").fetchone())

    def test_upgrade_preserves_old_and_new_evidence_and_is_idempotent(self):
        self.stage('old', 'COMMITTED')
        self.legacy()
        # New facts can still be recorded before the explicit upgrade.
        reopened = Core(self.project)
        reopened.task('pending', state='paused')
        self.stage('latest', relation='cumulative', supersedes=['old'])
        before = self.state()
        legacy = reopened.agenda()
        first = reopened.upgrade()
        self.assertTrue(first['upgraded'])
        self.assertEqual(before, self.state())
        indexed = Core(self.project).agenda()
        self.assertEqual(legacy['fingerprint'], indexed['fingerprint'])
        self.assertEqual(legacy['items'], indexed['items'])
        self.assertEqual(legacy['counts'], indexed['counts'])
        self.assertEqual('indexed_current_v1', indexed['storage']['mode'])
        self.assertFalse(reopened.upgrade()['upgraded'])
        self.assertEqual(before, self.state())
        self.assertEqual(1, reopened.store.get('config', 'project')['schema_version'])

    def test_failed_upgrade_rolls_back_projection_and_remains_readable(self):
        self.stage('delivery')
        self.legacy()
        before = self.state()
        with mock.patch.object(self.store, '_project_record', side_effect=OSError('synthetic migration failure')):
            with self.assertRaises(OSError):
                self.core.upgrade()
        self.assertEqual(before, self.state())
        self.assertTrue(Core(self.project).agenda()['storage']['upgrade_required'])
        self.assertTrue(self.core.upgrade()['upgraded'])
        self.assertFalse(Core(self.project).agenda()['storage']['upgrade_required'])

    def test_index_updates_on_terminal_reopen_and_artifact_decision_changes(self):
        self.stage('delivery')
        self.assertEqual(1, self.core.agenda()['counts']['stages'])
        self.stage('delivery', 'COMMITTED')
        self.assertEqual(0, self.core.agenda()['counts']['stages'])
        self.stage('delivery', 'CONFLICT')
        self.assertEqual(1, self.core.agenda()['counts']['stages'])
        artifact = {'artifact_id': 'material', 'task_id': 'work', 'decision': 'dismiss'}
        self.store.put('artifacts', 'material', artifact)
        self.assertEqual(0, self.core.agenda()['counts']['artifacts'])
        self.store.put('artifacts', 'material', {**artifact, 'decision': None})
        self.assertEqual(1, self.core.agenda()['counts']['artifacts'])

    def test_older_writer_invalidates_projection_and_readonly_fallback_finds_work(self):
        self.stage('previous', 'COMMITTED')
        # Emulate a prior release writing the source table without projection support.
        with closing(sqlite3.connect(self.store.path)) as db:
            with db:
                db.execute('INSERT INTO records(collection,key,value) VALUES(?,?,?)',
                           ('stages', 'new-from-old-client', json.dumps({'stage_id': 'new-from-old-client',
                            'task_id': 'work', 'status': 'QUEUED'})))
        # A later ordinary write must not accidentally mark unrelated changes clean.
        self.core.task('more-work')
        before = self.state()
        fallback = self.core.agenda()
        self.assertTrue(fallback['storage']['index_rebuild_required'])
        self.assertEqual(['stage:new-from-old-client'], [item['id'] for item in fallback['items']])
        self.assertEqual(before, self.state())
        self.assertTrue(self.core.upgrade()['upgraded'])
        indexed = self.core.agenda()
        self.assertFalse(indexed['storage']['index_rebuild_required'])
        self.assertFalse(indexed['storage']['upgrade_required'])
        self.assertEqual(fallback['fingerprint'], indexed['fingerprint'])
        self.assertEqual(before, self.state())

    def test_history_growth_does_not_load_terminal_rows_or_plans(self):
        self.stage('current')
        self.store.put('operations', 'pending', {'operation_id': 'pending', 'status': 'UNKNOWN',
                                                'kind': 'reconcile', 'plan_id': 'needed'})
        self.store.put('plans', 'needed', {'plan_id': 'needed', 'kind': 'reconcile'})
        counts = []
        first_fingerprint = None
        previous = 0
        for count in (100, 1000):
            with self.store.transaction():
                for index in range(previous, count):
                    self.stage(f'history-{index}', 'COMMITTED')
                    self.store.put('operations', f'old-{index}', {'operation_id': f'old-{index}', 'status': 'COMPLETED',
                                                                 'plan_id': f'plan-{index}'})
                    self.store.put('plans', f'plan-{index}', {'plan_id': f'plan-{index}'})
                    self.store.put('checkpoints', f'checkpoint-{index}', {'checkpoint_id': f'checkpoint-{index}'})
                previous = count
            steps = [0]
            original_connect = self.store._connect

            @contextmanager
            def measured_connect(*args, **kwargs):
                with original_connect(*args, **kwargs) as db:
                    def progress():
                        steps[0] += 1
                        return 0
                    db.set_progress_handler(progress, 1)
                    try:
                        yield db
                    finally:
                        db.set_progress_handler(None, 0)

            with mock.patch.object(self.store, '_connect', measured_connect):
                result = self.core.agenda(limit=1)
            counts.append(steps[0])
            self.assertEqual(2, result['total'])
            self.assertEqual(5, result['storage']['loaded_records'])
            if first_fingerprint is None:
                first_fingerprint = result['fingerprint']
            self.assertEqual(first_fingerprint, result['fingerprint'])
            snapshot = self.store.snapshot_current()
            self.assertEqual(['current'], [stage['stage_id'] for stage in snapshot['stages']])
            self.assertEqual(['pending'], [op['operation_id'] for op in snapshot['operations']])
            self.assertEqual(['needed'], [plan['plan_id'] for plan in snapshot['plans']])
            self.assertEqual([], snapshot['checkpoints'])
        # B-tree depth may change; the work must not grow with all 900 new rows.
        self.assertLess(counts[1], counts[0] * 2, counts)

    def test_ancestor_dependencies_and_pagination_match_legacy_selection(self):
        self.stage('root', 'COMMITTED', supersedes=[])
        self.stage('v1', relation='cumulative', supersedes=['root'])
        self.stage('v2', relation='cumulative', supersedes=['v1'])
        for index in range(12):
            self.stage(f'independent-{index:02d}', relation='independent')
        self.store.put('operations', 'receipt', {'operation_id': 'receipt', 'kind': 'reconcile',
                                                'status': 'EFFECT_APPLIED', 'stage_id': 'root', 'candidate': 'frozen'})
        first = self.core.agenda(limit=3)
        cursor, seen = None, []
        while True:
            result = self.core.agenda(limit=3, cursor=cursor)
            seen.extend(item['id'] for item in result['items'])
            self.assertEqual(first['fingerprint'], result['fingerprint'])
            cursor = result['next_cursor']
            if cursor is None:
                break
        self.assertEqual(14, len(seen))
        self.assertEqual(14, len(set(seen)))
        self.assertNotIn('stage:v1', seen)
        self.legacy()
        legacy = self.core.agenda(limit=3)
        self.assertEqual(first['fingerprint'], legacy['fingerprint'])
        self.assertEqual(first['items'], legacy['items'])
        self.assertEqual(first['counts'], legacy['counts'])
        self.core.upgrade()
        self.stage('root', 'COMMITTED', accepted_commit='changed')
        with self.assertRaises(GovernanceError) as captured:
            self.core.agenda(cursor=first['next_cursor'])
        self.assertEqual('AGENDA_CURSOR_STALE', captured.exception.code)


if __name__ == '__main__':
    unittest.main()
