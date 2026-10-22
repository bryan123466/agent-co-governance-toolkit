"""Synthetic local evidence tests. No user configuration or network writes."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from agct.core import Core, git, validate_relative_path
from agct.store import GovernanceError, Store


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='agct-core-')
        self.root = Path(self.temp.name)
        self.project = self.root / 'governance'
        Core.initialize(self.project, 'Synthetic quality forms')
        self.core = Core(self.project)
        self.core.task('forms', 'Quality forms')
        self.workspace = self.root / 'author'
        self.workspace.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def assertCode(self, code, fn, *args, **kwargs):
        with self.assertRaises(GovernanceError) as captured:
            fn(*args, **kwargs)
        self.assertEqual(code, captured.exception.code)

    def create_git(self):
        git(self.workspace, 'init', '--quiet')
        git(self.workspace, 'config', 'user.name', 'Synthetic Author')
        git(self.workspace, 'config', 'user.email', 'synthetic@example.invalid')
        git(self.workspace, 'config', 'core.autocrlf', 'false')

    def test_task_pause_is_retained_not_actionable(self):
        self.core.task('forms', state='paused')
        result = self.core.status()
        self.assertEqual(['forms'], [t['task_id'] for t in result['retained_task_state']])
        self.assertEqual([], result['actionable']['stages'])
        self.assertEqual([], result['actionable']['operations'])

    def test_current_view_excludes_terminal_history(self):
        self.core.store.put('stages', 'old', {'stage_id': 'old', 'status': 'SUPERSEDED'})
        self.core.store.put('stages', 'new', {'stage_id': 'new', 'status': 'QUEUED'})
        self.core.store.put('operations', 'done', {'operation_id': 'done', 'status': 'COMPLETED'})
        self.core.store.put('operations', 'review', {'operation_id': 'review', 'status': 'REVIEW_REQUIRED'})
        current = self.core.status()
        self.assertEqual(['new'], [r['stage_id'] for r in current['actionable']['stages']])
        self.assertEqual(['review'], [r['operation_id'] for r in current['actionable']['operations']])

    def test_current_view_shows_cumulative_leaf_without_forging_old_terminal_state(self):
        base = {'task_id': 'forms', 'workspace': 'worker', 'status': 'QUEUED'}
        self.core.store.put('stages', 'v1', {**base, 'stage_id': 'v1', 'relation': 'independent', 'supersedes': []})
        self.core.store.put('stages', 'v2', {**base, 'stage_id': 'v2', 'relation': 'cumulative', 'supersedes': ['v1']})
        self.core.store.put('stages', 'v3', {**base, 'stage_id': 'v3', 'relation': 'cumulative', 'supersedes': ['v2']})
        self.core.store.put('stages', 'other', {'task_id': 'other', 'workspace': 'worker', 'status': 'QUEUED',
                                             'stage_id': 'other', 'relation': 'independent', 'supersedes': []})
        current = self.core.status()
        self.assertEqual(['other', 'v3'], [s['stage_id'] for s in current['actionable']['stages']])
        self.assertEqual(0, current['history_counts']['terminal_stages'])
        self.assertEqual('QUEUED', self.core.store.get('stages', 'v1')['status'])
        self.assertEqual('QUEUED', self.core.store.get('stages', 'v2')['status'])
        self.assertEqual({'v1', 'v2'}, {s['stage_id'] for s in current['covered_pending_stages']})
        latest = self.core.store.get('stages', 'v3')
        latest['status'] = 'CONFLICT'
        self.core.store.put('stages', 'v3', latest)
        conflicted = self.core.status()
        self.assertEqual(['other', 'v3'], [s['stage_id'] for s in conflicted['actionable']['stages']])
        self.assertEqual('CONFLICT', conflicted['actionable']['stages'][1]['status'])
        self.assertEqual(0, conflicted['history_counts']['terminal_stages'])

    def test_store_persists_without_replaying_history(self):
        first = self.core.store.events()
        Core.initialize(self.project, 'Ignored new name')
        self.assertEqual(first, Store(self.project).events())
        self.assertEqual('Synthetic quality forms', Store(self.project).get('config', 'project')['name'])

    def test_unsupported_schema_does_not_silently_downgrade(self):
        config = self.core.store.get('config', 'project')
        config['schema_version'] = 999
        self.core.store.put('config', 'project', config)
        self.assertCode('SCHEMA_VERSION_UNSUPPORTED', Core, self.project)
        self.assertCode('SCHEMA_VERSION_UNSUPPORTED', Core.initialize, self.project)
        self.assertEqual(999, Store(self.project).get('config', 'project')['schema_version'])

    def test_store_guard_is_reentrant_and_process_exclusive(self):
        with self.core.store.guard():
            with self.core.store.guard():
                self.core.store.put('checks', 'test', {'value': 1})
            command = "from agct.store import Store,GovernanceError;import sys\ns=Store(sys.argv[1])\ntry:\n with s.guard(): print('unexpected')\nexcept GovernanceError as e: print(e.code)"
            process = subprocess.run([sys.executable, '-c', command, str(self.project)], capture_output=True, text=True)
            self.assertEqual(0, process.returncode, process.stderr)
            self.assertEqual('BUSY', process.stdout.strip())
        with Store(self.project).guard():
            pass

    def test_path_escape_metadata_and_secrets_rejected(self):
        for path, code in [('../outside.txt', 'UNSAFE_PATH'), ('C:/outside.txt', 'UNSAFE_PATH'),
                           ('.git/config', 'RESERVED_PATH'), ('.agct/state.sqlite3', 'RESERVED_PATH'),
                           ('.env', 'SECRET_PATH'), ('keys/id_rsa', 'SECRET_PATH')]:
            self.assertCode(code, validate_relative_path, self.workspace, path)

    def test_symlink_escape_rejected(self):
        outside = self.root / 'outside.txt'
        outside.write_text('synthetic')
        link = self.workspace / 'link.txt'
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest('Host cannot create symlinks; native junction test remains separate.')
        self.assertCode('SYMLINK_PATH', self.core.checkpoint, 'forms', str(self.workspace), ['link.txt'], 'continue')
        self.assertEqual([], self.core.store.list('checkpoints'))

    @unittest.skipUnless(os.name == 'nt', 'Native Windows junction test')
    def test_windows_junction_escape_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'protected.txt').write_text('synthetic preserve')
        link = self.workspace / 'junction'
        result = subprocess.run(['cmd', '/d', '/c', 'mklink', '/J', str(link), str(outside)], capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr.decode(errors='replace'))
        try:
            self.assertCode('SYMLINK_PATH', self.core.checkpoint, 'forms', self.workspace, ['junction/protected.txt'], 'Continue')
            self.assertEqual('synthetic preserve', (outside / 'protected.txt').read_text())
        finally:
            link.rmdir()

    def test_symlink_detection_portable_negative_path(self):
        (self.workspace / 'safe.txt').write_text('safe')
        original = Path.is_symlink
        with mock.patch.object(Path, 'is_symlink', lambda p: p.name == 'safe.txt' or original(p)):
            self.assertCode('SYMLINK_PATH', validate_relative_path, self.workspace, 'safe.txt')

    def test_partial_git_root_rejected(self):
        self.create_git()
        child = self.workspace / 'subdir'
        child.mkdir()
        (child / 'file.txt').write_text('synthetic')
        self.assertCode('GIT_WORKSPACE_ROOT', self.core.checkpoint, 'forms', child, ['file.txt'], 'Continue')

    def test_plain_checkpoint_restore_and_source_preserved(self):
        target = self.workspace / 'form.txt'
        target.write_bytes(b'draft\r\n')
        checkpoint = self.core.checkpoint('forms', self.workspace, ['form.txt'], 'Review draft', paused=True)
        target.write_bytes(b'newer draft\n')
        restored = self.root / 'restore'
        result = self.core.restore(checkpoint['checkpoint_id'], restored)
        self.assertEqual(b'draft\r\n', (restored / 'form.txt').read_bytes())
        self.assertEqual(b'newer draft\n', target.read_bytes())
        self.assertFalse(result['original_workspace_modified'])
        self.assertFalse(checkpoint['delivery'])

    def test_restore_requires_independent_empty_destination(self):
        (self.workspace / 'f.txt').write_text('saved')
        checkpoint = self.core.checkpoint('forms', self.workspace, ['f.txt'], 'Continue')
        self.assertCode('RESTORE_NOT_INDEPENDENT', self.core.restore, checkpoint['checkpoint_id'], self.workspace / 'copy')
        destination = self.root / 'occupied'
        destination.mkdir()
        (destination / 'keep.txt').write_text('keep')
        self.assertCode('RESTORE_NOT_EMPTY', self.core.restore, checkpoint['checkpoint_id'], destination)
        self.assertEqual('keep', (destination / 'keep.txt').read_text())

    def test_corrupt_snapshot_fails_before_destination_write(self):
        (self.workspace / 'f.txt').write_bytes(b'saved')
        checkpoint = self.core.checkpoint('forms', self.workspace, ['f.txt'], 'Continue')
        digest = checkpoint['files'][0]['worktree']['sha256']
        (self.project / '.agct' / 'objects' / digest).write_bytes(b'corrupt')
        destination = self.root / 'untouched'
        self.assertCode('SNAPSHOT_CORRUPT', self.core.restore, checkpoint['checkpoint_id'], destination)
        self.assertFalse(destination.exists())

    def test_git_checkpoint_reconstructs_binary_layers_and_deletions(self):
        self.create_git()
        baseline = {'binary.dat': b'\x00HEAD\xff\r\n', 'deleted.txt': b'delete later\n',
                    'unstaged-delete.txt': b'keep staged\n', 'base.txt': b'unchanged\n'}
        for name, content in baseline.items():
            (self.workspace / name).write_bytes(content)
        git(self.workspace, 'add', '--', *baseline)
        git(self.workspace, 'commit', '-qm', 'Synthetic baseline')
        (self.workspace / 'binary.dat').write_bytes(b'\x00INDEX\xff\n')
        git(self.workspace, 'add', '--', 'binary.dat')
        (self.workspace / 'binary.dat').write_bytes(b'\x00WORKTREE\xfe\r\n')
        git(self.workspace, 'rm', '--quiet', '--', 'deleted.txt')
        (self.workspace / 'unstaged-delete.txt').unlink()
        (self.workspace / 'untracked.dat').write_bytes(b'\x00UNTRACKED\xff')
        (self.workspace / 'added.txt').write_bytes(b'index addition\n')
        git(self.workspace, 'add', '--', 'added.txt')
        (self.workspace / 'added.txt').write_bytes(b'working addition\r\n')
        paths = [*baseline, 'untracked.dat', 'added.txt']
        index_before = git(self.workspace, 'ls-files', '--stage', '-z').stdout
        status_before = git(self.workspace, 'status', '--porcelain=v1', '-z', '--untracked-files=all').stdout
        checkpoint = self.core.checkpoint('forms', self.workspace, paths, 'Continue integration')
        restored = self.root / 'git-restored'
        result = self.core.restore(checkpoint['checkpoint_id'], restored)
        self.assertTrue(result['synthetic_git_baseline'])
        self.assertEqual(index_before, git(restored, 'ls-files', '--stage', '-z').stdout)
        self.assertEqual(status_before, git(restored, 'status', '--porcelain=v1', '-z', '--untracked-files=all').stdout)
        self.assertEqual(index_before, git(self.workspace, 'ls-files', '--stage', '-z').stdout)
        for path in paths:
            original, copy = self.workspace / path, restored / path
            self.assertEqual(original.exists(), copy.exists(), path)
            if original.exists():
                self.assertEqual(original.read_bytes(), copy.read_bytes(), path)
        self.assertIn(b'AGCT synthetic restore baseline', git(restored, 'log', '-1', '--format=%B').stdout)

    def test_artifact_decision_is_bound_to_content(self):
        target = self.workspace / 'large.bin'
        target.write_bytes(b'first')
        first = self.core.artifact('forms', target, decision='no_backup_needed')
        same = self.core.artifact('forms', target)
        self.assertEqual('no_backup_needed', same['decision'])
        self.assertEqual([], self.core.status()['actionable']['artifacts'])
        target.write_bytes(b'new version')
        changed = self.core.artifact('forms', target)
        self.assertTrue(changed['content_changed'])
        self.assertIsNone(changed['decision'])
        self.assertNotEqual(first['sha256'], changed['sha256'])

    def test_artifact_backup_verified_by_bytes(self):
        target = self.workspace / 'deliverable.bin'
        target.write_bytes(b'fake quality form')
        backup = self.root / 'backup.bin'
        backup.write_bytes(target.read_bytes())
        self.assertTrue(self.core.artifact('forms', target, backup=backup)['backup_verified'])
        self.assertTrue(self.core.artifact('forms', target)['backup_verified'])
        backup.write_bytes(b'different')
        self.assertFalse(self.core.artifact('forms', target, backup=backup)['backup_verified'])
        backup.unlink()
        missing = self.core.artifact('forms', target)
        self.assertFalse(missing['backup_verified'])
        self.assertFalse(missing['backup_available'])
        self.assertCode('BACKUP_NOT_INDEPENDENT', self.core.artifact, 'forms', target, backup=target)

    def test_experience_scope_version_enabled_and_action(self):
        self.core.task('other')
        self.core.experience('scope', 'SYNTHETIC', 'reconcile', 'refresh_plan', task_id='forms')
        self.core.experience('old', 'SYNTHETIC', 'reconcile', 'refresh_plan', version='0')
        self.core.experience('off', 'SYNTHETIC', 'reconcile', 'refresh_plan', enabled=False)
        self.assertEqual(['scope'], [r['rule_id'] for r in self.core.match_experience('SYNTHETIC', 'reconcile', 'forms')['matches']])
        self.assertEqual([], self.core.match_experience('SYNTHETIC', 'reconcile', 'other')['matches'])
        self.assertEqual([], self.core.match_experience('SYNTHETIC', 'adopt', 'forms')['matches'])
        self.assertCode('UNSUPPORTED_EXPERIENCE_ACTION', self.core.experience, 'bad', 'FAIL', 'reconcile', 'run_shell')
        self.assertEqual(1, len(self.core.match_experience('EFFECT_PRESENT_RECEIPT_MISSING', 'reconcile')['matches']))


if __name__ == '__main__':
    unittest.main()
