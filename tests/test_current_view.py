"""Read-only current views and finite AI agendas over synthetic project state."""
import base64
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest import mock

from agct.core import Core
from agct.gitops import commit, git
from agct.integration import Integration
from agct.store import GovernanceError, Store


class CurrentViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='agct-current-view-')
        self.root = Path(self.temp.name)
        self.project = self.root / 'control'
        Core.initialize(self.project, 'Synthetic current view')
        self.core = Core(self.project)
        self.store = self.core.store
        self.core.task('forms', 'Synthetic forms')

    def tearDown(self):
        self.temp.cleanup()

    def record(self, collection, identity, **fields):
        id_key = {'stages': 'stage_id', 'operations': 'operation_id', 'artifacts': 'artifact_id'}[collection]
        value = {id_key: identity, 'task_id': 'forms', **fields}
        self.store.put(collection, identity, value)
        return value

    def assertCode(self, code, function, *args, **kwargs):
        with self.assertRaises(GovernanceError) as captured:
            function(*args, **kwargs)
        self.assertEqual(code, captured.exception.code)

    def logical_state(self):
        with closing(sqlite3.connect(self.store.path)) as connection:
            return (connection.execute('SELECT * FROM records ORDER BY collection,key').fetchall(),
                    connection.execute('SELECT * FROM events ORDER BY sequence').fetchall())

    def test_reading_missing_project_never_initializes_it(self):
        missing = self.root / 'absent'
        self.assertCode('NOT_INITIALIZED', Core, missing)
        self.assertFalse(missing.exists())

    def test_database_removed_after_open_is_not_recreated_by_read(self):
        self.store.path.unlink()
        for read in (self.core.status, self.core.agenda, self.store.events):
            with self.assertRaises(sqlite3.OperationalError):
                read()
            self.assertFalse(self.store.path.exists())

    def test_read_connections_cannot_write_records(self):
        before = self.logical_state()
        with self.store._connect(readonly=True) as connection:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("DELETE FROM records")
        self.assertEqual(before, self.logical_state())

    def test_status_and_agenda_do_not_change_records_events_or_work_files(self):
        self.record('operations', 'interrupted', kind='reconcile', status='UNKNOWN', code='INSPECT_EFFECT')
        workspace = self.root / 'ordinary-work'
        workspace.mkdir()
        draft = workspace / 'draft.txt'
        draft.write_bytes(b'Unfinished work\r\n')
        before = self.logical_state()
        self.core.status()
        first = self.core.agenda(limit=1)
        second = self.core.agenda(limit=1, previous_fingerprint=first['fingerprint'])
        self.assertFalse(second['changed'])
        self.assertEqual(before, self.logical_state())
        self.assertEqual(b'Unfinished work\r\n', draft.read_bytes())
        self.assertFalse(second['effects_executed'])
        self.assertTrue(second['selection_only'])
        self.assertIsNone(second['project_complete'])

    def test_corrupt_database_is_reported_not_replaced_or_hidden(self):
        self.store.path.write_bytes(b'not a sqlite database')
        for read in (self.core.status, self.core.agenda):
            with self.assertRaises(sqlite3.DatabaseError):
                read()
            self.assertEqual(b'not a sqlite database', self.store.path.read_bytes())

    def test_status_reads_one_snapshot_while_another_connection_commits(self):
        self.record('stages', 'draft', status='QUEUED')
        first_row = threading.Event()
        writer_done = threading.Event()
        writer_errors = []
        original_connect = sqlite3.connect

        def writer():
            try:
                if not first_row.wait(5):
                    raise AssertionError('Reader did not reach the snapshot')
                with Store(self.project).guard(), closing(original_connect(self.store.path)) as connection:
                    with connection:
                        for collection, key, updates in (
                                ('tasks', 'forms', {'state': 'complete'}),
                                ('stages', 'draft', {'status': 'COMMITTED'})):
                            row = connection.execute('SELECT value FROM records WHERE collection=? AND key=?',
                                                     (collection, key)).fetchone()
                            value = json.loads(row[0])
                            value.update(updates)
                            connection.execute('UPDATE records SET value=? WHERE collection=? AND key=?',
                                               (json.dumps(value), collection, key))
            except Exception as exc:
                writer_errors.append(exc)
            finally:
                writer_done.set()

        def connect(*args, **kwargs):
            connection = original_connect(*args, **kwargs)
            if 'mode=ro' in str(args[0]):
                def row_factory(cursor, row):
                    if cursor.description[0][0] == 'collection' and not first_row.is_set():
                        first_row.set()
                        if not writer_done.wait(5):
                            raise AssertionError('Concurrent writer could not complete')
                    return row
                connection.row_factory = row_factory
            return connection

        thread = threading.Thread(target=writer)
        thread.start()
        try:
            with mock.patch('agct.store.sqlite3.connect', side_effect=connect):
                observed = self.core.status()
        finally:
            thread.join(6)
        self.assertFalse(thread.is_alive())
        self.assertEqual([], writer_errors)
        self.assertEqual('active', observed['tasks'][0]['state'])
        self.assertEqual('QUEUED', observed['stages'][0]['status'])
        after = self.core.status()
        self.assertEqual('complete', after['tasks'][0]['state'])
        self.assertEqual('COMMITTED', after['stages'][0]['status'])

    def test_unknown_and_review_operations_precede_stages_and_artifacts(self):
        self.record('stages', 'stage-1', status='QUEUED')
        self.record('artifacts', 'artifact-1', backup_verified=False)
        self.record('operations', 'operation-1', kind='reconcile', status='UNKNOWN')
        self.record('operations', 'operation-2', kind='adopt', status='REVIEW_REQUIRED')
        page = self.core.agenda(limit=2)
        self.assertEqual(['operation:operation-1', 'operation:operation-2'], [item['id'] for item in page['items']])
        self.assertEqual(4, page['total'])
        self.assertEqual(2, page['truncated'])
        unchanged = self.core.agenda(limit=2, previous_fingerprint=page['fingerprint'])
        self.assertFalse(unchanged['changed'])
        self.assertEqual(page['items'], unchanged['items'])

    def test_paused_and_waiting_tasks_are_retained_without_becoming_backlog(self):
        self.core.task('forms', state='paused')
        self.core.task('waiting', state='waiting')
        result = self.core.agenda()
        self.assertEqual(2, result['counts']['retained_tasks'])
        self.assertEqual(0, result['total'])
        self.assertEqual([], result['items'])
        self.assertIsNone(result['project_complete'])

    def test_cumulative_projection_selects_current_leaf_without_mutating_history(self):
        self.record('stages', 'v1', workspace='author', status='QUEUED', relation='independent', supersedes=[])
        self.record('stages', 'v2', workspace='author', status='QUEUED', relation='cumulative', supersedes=['v1'])
        before = self.logical_state()
        result = self.core.agenda()
        self.assertEqual(['stage:v2'], [item['id'] for item in result['items']])
        self.assertEqual(1, result['counts']['covered_stages'])
        self.assertEqual(before, self.logical_state())
        self.assertEqual('QUEUED', self.store.get('stages', 'v1')['status'])

    def test_large_history_does_not_fill_or_change_the_current_agenda(self):
        self.record('stages', 'current', status='QUEUED')
        initial = self.core.agenda(limit=1)
        with self.store.guard(), self.store._connect() as connection:
            connection.executemany('INSERT INTO records(collection,key,value) VALUES(?,?,?)',
                                   [('stages', f'history-{i}', json.dumps({'stage_id': f'history-{i}', 'status': 'COMMITTED'}))
                                    for i in range(1000)])
        result = self.core.agenda(limit=1, previous_fingerprint=initial['fingerprint'])
        self.assertFalse(result['changed'])
        self.assertEqual(initial['items'], result['items'])
        self.assertEqual(1, result['total'])
        self.assertEqual(0, result['truncated'])

    def test_pages_cover_every_current_item_without_a_persisted_cursor(self):
        for index in range(25):
            self.record('stages', f'stage-{index:02d}', status='QUEUED')
        before = self.logical_state()
        cursor, seen, first_fingerprint = None, [], None
        while True:
            result = self.core.agenda(limit=4, cursor=cursor, previous_fingerprint=first_fingerprint)
            if first_fingerprint is None:
                first_fingerprint = result['fingerprint']
            else:
                self.assertFalse(result['changed'])
            self.assertLessEqual(len(result['items']), 4)
            seen.extend(item['id'] for item in result['items'])
            cursor = result['next_cursor']
            if cursor is None:
                break
        self.assertEqual(25, len(seen))
        self.assertEqual(25, len(set(seen)))
        self.assertEqual(0, result['truncated'])
        self.assertEqual(before, self.logical_state())

    def test_limit_and_page_do_not_change_whole_input_fingerprint(self):
        for index in range(3):
            self.record('stages', f'stage-{index}', status='QUEUED')
        first = self.core.agenda(limit=1)
        second = self.core.agenda(limit=2, cursor=first['next_cursor'])
        whole = self.core.agenda(limit=100)
        self.assertEqual(first['fingerprint'], second['fingerprint'])
        self.assertEqual(first['fingerprint'], whole['fingerprint'])

    def test_change_beyond_first_page_invalidates_cursor_and_changes_fingerprint(self):
        for index in range(3):
            self.record('stages', f'stage-{index}', status='QUEUED')
        first = self.core.agenda(limit=1)
        self.record('stages', 'stage-2', status='CONFLICT', code='CONTENT_CONFLICT')
        changed = self.core.agenda(limit=1, previous_fingerprint=first['fingerprint'])
        self.assertTrue(changed['changed'])
        self.assertEqual(first['items'], changed['items'])
        self.assertCode('AGENDA_CURSOR_STALE', self.core.agenda, cursor=first['next_cursor'])

    def test_added_failure_changes_fingerprint_and_appears_first(self):
        self.record('stages', 'stage', status='QUEUED')
        initial = self.core.agenda()
        self.record('operations', 'failure', kind='adopt', status='UNKNOWN', code='EFFECT_UNCONFIRMED')
        result = self.core.agenda(previous_fingerprint=initial['fingerprint'])
        self.assertTrue(result['changed'])
        self.assertEqual('operation:failure', result['items'][0]['id'])
        self.assertEqual('UNKNOWN', result['items'][0]['state'])

    def test_observation_timestamp_alone_is_not_new_work(self):
        self.record('artifacts', 'material', sha256='0' * 64, backup_verified=False, updated_at='earlier')
        initial = self.core.agenda()
        self.record('artifacts', 'material', sha256='0' * 64, backup_verified=False, updated_at='later')
        result = self.core.agenda(previous_fingerprint=initial['fingerprint'])
        self.assertFalse(result['changed'])
        self.record('artifacts', 'material', sha256='1' * 64, backup_verified=False, updated_at='later')
        self.assertTrue(self.core.agenda(previous_fingerprint=initial['fingerprint'])['changed'])

    def test_changed_relevant_predecessor_is_not_mistaken_for_unrelated_history(self):
        self.record('stages', 'v1', workspace='author', status='COMMITTED', accepted_commit='old', supersedes=[])
        self.record('stages', 'v2', workspace='author', status='QUEUED', relation='cumulative', supersedes=['v1'])
        first = self.core.agenda()
        self.record('stages', 'v1', workspace='author', status='COMMITTED', accepted_commit='changed', supersedes=[])
        self.assertTrue(self.core.agenda(previous_fingerprint=first['fingerprint'])['changed'])

    def test_interrupted_receipt_tracks_baseline_path_and_committed_stage_workspace(self):
        engine = Integration(self.project)
        baseline, worker = self.root / 'baseline', self.root / 'worker'
        baseline.mkdir()
        git(baseline, 'init', '-b', 'main')
        git(baseline, 'config', 'user.name', 'Synthetic Tester')
        git(baseline, 'config', 'user.email', 'tester@example.invalid')
        (baseline / 'form.txt').write_text('Initial form\n', encoding='utf-8')
        git(baseline, 'add', '--', 'form.txt')
        git(baseline, 'commit', '-m', 'Synthetic starting point')
        start = commit(baseline, 'HEAD')
        git(self.root, 'clone', '--no-hardlinks', str(baseline), str(worker))
        git(worker, 'config', 'user.name', 'Synthetic Worker')
        git(worker, 'config', 'user.email', 'worker@example.invalid')
        engine.workspace('baseline', baseline)
        engine.workspace('worker', worker)
        (worker / 'form.txt').write_text('Updated form\n', encoding='utf-8')
        git(worker, 'add', '--', 'form.txt')
        git(worker, 'commit', '-m', 'Synthetic delivery')
        stage = engine.submit('forms', 'worker', commit(worker, 'HEAD'), start, ['form.txt'])['stage']
        plan = engine.reconcile('baseline')['plan']['plan_id']
        original_save = engine._save

        def interrupt_after_stage_receipt(collection, key, record):
            result = original_save(collection, key, record)
            if collection == 'stages' and record.get('status') == 'COMMITTED':
                raise RuntimeError('Synthetic interruption after stage receipt')
            return result

        with mock.patch.object(engine, '_save', side_effect=interrupt_after_stage_receipt):
            with self.assertRaisesRegex(RuntimeError, 'after stage receipt'):
                engine.reconcile('baseline', True, plan)
        self.assertEqual('COMMITTED', self.store.get('stages', stage['stage_id'])['status'])
        operation = self.store.list('operations')[0]
        self.assertEqual('EFFECT_APPLIED', operation['status'])
        self.assertEqual(str(baseline.resolve()), operation['baseline'])
        self.assertNotIn('workspace', operation)
        # A separate current material keeps the first page bounded and produces
        # a cursor without turning the committed stage back into a backlog item.
        self.record('artifacts', 'material', sha256='0' * 64, backup_verified=False)
        first = self.core.agenda(limit=1)
        self.assertEqual(0, first['counts']['stages'])
        self.assertEqual(1, first['counts']['operations'])
        self.assertIsNotNone(first['next_cursor'])

        for name, path in (('baseline', baseline), ('worker', worker)):
            with self.subTest(rebound_workspace=name):
                head = commit(path, 'HEAD')
                git(path, 'checkout', '-b', 'next-work')
                engine.workspace(name, path)
                before = self.logical_state()
                changed = self.core.agenda(limit=1, previous_fingerprint=first['fingerprint'])
                self.assertTrue(changed['changed'])
                self.assertCode('AGENDA_CURSOR_STALE', self.core.agenda, cursor=first['next_cursor'])
                self.assertEqual(before, self.logical_state())
                self.assertEqual(head, commit(path, 'HEAD'))
                self.assertEqual(operation, self.store.get('operations', operation['operation_id']))
                first = changed

    def test_experience_is_a_conditioned_suggestion_not_an_executed_recovery(self):
        self.record('operations', 'receipt', kind='reconcile', status='EFFECT_APPLIED', candidate='frozen-result')
        before = self.logical_state()
        initial = self.core.agenda()
        item = initial['items'][0]
        self.assertEqual('EFFECT_PRESENT_RECEIPT_MISSING', item['code'])
        self.assertEqual('receipt-recovery-v1', item['experience_candidates'][0]['rule_id'])
        self.assertTrue(item['experience_candidates'][0]['requires_current_evidence'])
        self.assertEqual(before, self.logical_state())
        self.assertEqual('EFFECT_APPLIED', self.store.get('operations', 'receipt')['status'])
        self.core.experience('receipt-recovery-v1', 'EFFECT_PRESENT_RECEIPT_MISSING',
                             'reconcile', 'verify_and_finalize', enabled=False)
        result = self.core.agenda(previous_fingerprint=initial['fingerprint'])
        self.assertTrue(result['changed'])
        self.assertEqual([], result['items'][0]['experience_candidates'])

    def test_cursor_cannot_cross_project_identity(self):
        for index in range(2):
            self.record('stages', f'stage-{index}', status='QUEUED')
        cursor = self.core.agenda(limit=1)['next_cursor']
        other_project = self.root / 'other'
        Core.initialize(other_project, 'Synthetic current view')
        other = Core(other_project)
        other.task('forms', 'Synthetic forms')
        for stage in self.store.list('stages'):
            other.store.put('stages', stage['stage_id'], stage)
        self.assertCode('AGENDA_CURSOR_STALE', other.agenda, cursor=cursor)

    def test_strict_limits_and_cursor_inputs(self):
        for limit in (True, False, 0, -1, 101, 1.0, '20', None):
            self.assertCode('INVALID_ARGUMENT', self.core.agenda, limit=limit)
        for previous in ('', 'not-a-fingerprint', True):
            self.assertCode('INVALID_ARGUMENT', self.core.agenda, previous_fingerprint=previous)
        for cursor in ('not base64!', '', True, 'a' * 1025):
            self.assertCode('AGENDA_CURSOR_INVALID', self.core.agenda, cursor=cursor)
        malformed = base64.urlsafe_b64encode(json.dumps({'version': 1, 'offset': True, 'fingerprint': '0' * 64}).encode()).decode()
        self.assertCode('AGENDA_CURSOR_INVALID', self.core.agenda, cursor=malformed)

    def test_actionable_record_without_identity_fails_instead_of_disappearing(self):
        self.store.put('operations', 'broken', {'status': 'UNKNOWN'})
        self.assertCode('STATE_RECORD_INVALID', self.core.agenda)


if __name__ == '__main__':
    unittest.main()
