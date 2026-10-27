"""Independent regressions for receipt scope, cumulative lineage and writer identity."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from taskcarry.core import Core
from taskcarry.gitops import commit, fingerprint, git, out
from taskcarry.integration import Integration
from taskcarry.store import GovernanceError


class AdversarialGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='taskcarry-adversarial-')
        self.root = Path(self.temp.name)
        self.control = self.root / 'control'
        Core.initialize(self.control, 'Synthetic adversarial project')
        self.core = Core(self.control)
        self.engine = Integration(self.control)
        self.core.task('quality')
        self.baseline = self.root / 'baseline'
        self.baseline.mkdir()
        git(self.baseline, 'init', '-b', 'main')
        (self.baseline / 'form.txt').write_text('identifier\nstatus\n', encoding='utf-8')
        git(self.baseline, 'add', '--', 'form.txt')
        git(self.baseline, 'commit', '-m', 'Synthetic baseline')
        self.base = commit(self.baseline, 'HEAD')
        self.worker = self.root / 'worker'
        git(self.root, 'clone', '--no-hardlinks', str(self.baseline), str(self.worker))
        self.engine.workspace('baseline', self.baseline)
        self.engine.workspace('worker', self.worker)

    def tearDown(self):
        self.temp.cleanup()

    def deliver(self, stage_id, content, predecessor=None):
        (self.worker / 'form.txt').write_text(content, encoding='utf-8')
        git(self.worker, 'add', '--', 'form.txt')
        git(self.worker, 'commit', '-m', 'Synthetic ' + stage_id)
        return self.engine.submit('quality', 'worker', commit(self.worker, 'HEAD'), self.base,
                                  ['form.txt'], stage_id=stage_id,
                                  relation='cumulative' if predecessor else 'independent',
                                  supersedes=[predecessor] if predecessor else None)['stage']

    def receive(self):
        plan = self.engine.reconcile('baseline')['plan']
        return self.engine.reconcile('baseline', execute=True, plan_id=plan['plan_id'])

    def assert_error(self, expected, function, *args, **kwargs):
        with self.assertRaises(GovernanceError) as caught:
            function(*args, **kwargs)
        self.assertEqual(expected, caught.exception.code)

    def test_second_baseline_cannot_reuse_first_baseline_receipt(self):
        second = self.root / 'second-baseline'
        git(self.root, 'clone', '--no-hardlinks', str(self.baseline), str(second))
        self.engine.workspace('second', second)
        self.deliver('v1', 'identifier\nstatus\nreviewer\n')
        self.assertEqual('COMPLETE', self.receive()['status'])
        receipt = self.engine.store.get('stages', 'v1')
        self.assertEqual(str(self.baseline.resolve()), receipt['accepted_baseline'])
        self.assert_error('BASELINE_BOUND', self.engine.reconcile, 'second')
        self.assertEqual(self.base, commit(second, 'HEAD'))
        self.assertEqual('identifier\nstatus\n', (second / 'form.txt').read_text())

    def test_invalid_execute_does_not_claim_an_integration_baseline(self):
        self.assert_error('PLAN_REQUIRED', self.engine.reconcile, 'baseline', True)
        self.assertIsNone(self.engine.store.get('settings', 'integration_baseline'))

    def test_oversized_new_blob_rejected_before_delivery_record(self):
        payload = bytes(range(256)) * 4
        (self.worker / 'payload.bin').write_bytes(payload)
        git(self.worker, 'add', '--', 'payload.bin')
        git(self.worker, 'commit', '-m', 'Synthetic boundedness payload')
        tip = commit(self.worker, 'HEAD')
        with patch('taskcarry.gitops.MAX_BLOB_BYTES', 128):
            self.assert_error('DELIVERY_TOO_LARGE', self.engine.submit, 'quality', 'worker', tip,
                              self.base, ['payload.bin'], stage_id='oversized-new')
        self.assertIsNone(self.engine.store.get('stages', 'oversized-new'))
        self.assertEqual(payload, (self.worker / 'payload.bin').read_bytes())
        self.assertEqual(self.base, commit(self.baseline, 'HEAD'))

    def test_oversized_deleted_blob_rejected_from_original_tree(self):
        (self.worker / 'payload.bin').write_bytes(bytes(range(256)) * 4)
        git(self.worker, 'add', '--', 'payload.bin')
        git(self.worker, 'commit', '-m', 'Synthetic old payload')
        origin = commit(self.worker, 'HEAD')
        git(self.worker, 'rm', '--', 'payload.bin')
        git(self.worker, 'commit', '-m', 'Synthetic payload deletion')
        tip = commit(self.worker, 'HEAD')
        with patch('taskcarry.gitops.MAX_BLOB_BYTES', 128):
            self.assert_error('DELIVERY_TOO_LARGE', self.engine.submit, 'quality', 'worker', tip,
                              origin, ['payload.bin'], stage_id='oversized-deleted')
        self.assertIsNone(self.engine.store.get('stages', 'oversized-deleted'))
        self.assertEqual(self.base, commit(self.baseline, 'HEAD'))

    def test_adoption_does_not_overwrite_an_ignored_local_artifact(self):
        (self.worker / '.git' / 'info' / 'exclude').write_text('draft.cache\n', encoding='utf-8')
        private = self.worker / 'draft.cache'
        private.write_bytes(b'unsaved synthetic local artifact\x00\xff')
        (self.baseline / 'draft.cache').write_bytes(b'public generated artifact')
        git(self.baseline, 'add', '--', 'draft.cache')
        git(self.baseline, 'commit', '-m', 'Synthetic public file colliding with an ignored artifact')
        plan = self.engine.adopt('worker', 'baseline')['plan']['plan_id']
        with self.assertRaises(GovernanceError):
            self.engine.adopt('worker', 'baseline', True, plan)
        self.assertEqual(b'unsaved synthetic local artifact\x00\xff', private.read_bytes())
        self.assertEqual(self.base, commit(self.worker, 'HEAD'))

    def test_autocrlf_does_not_convert_untracked_lf_bytes_during_adoption(self):
        git(self.worker, 'config', 'core.autocrlf', 'true')
        original = b'Unsubmitted synthetic design note\nSecond line remains LF\n'
        note = self.worker / 'unsubmitted-note.txt'
        note.write_bytes(original)
        (self.baseline / 'shared.txt').write_bytes(b'new public baseline content\n')
        git(self.baseline, 'add', '--', 'shared.txt')
        git(self.baseline, 'commit', '-m', 'Synthetic public update')
        plan = self.engine.adopt('worker', 'baseline')['plan']['plan_id']
        result = self.engine.adopt('worker', 'baseline', True, plan)
        self.assertEqual('ADOPTED', result['status'])
        self.assertTrue(result['wip_verified'])
        self.assertEqual(original, note.read_bytes())
        self.assertIn(b'unsubmitted-note.txt\0', git(self.worker, 'ls-files', '--others', '--exclude-standard', '-z').stdout)

    def test_autocrlf_preserves_distinct_staged_and_worktree_bytes(self):
        git(self.worker, 'config', 'core.autocrlf', 'true')
        tracked = self.worker / 'form.txt'
        tracked.write_bytes(b'identifier\r\nstatus\r\nstaged-reviewer\r\n')
        git(self.worker, 'add', '--', 'form.txt')
        original_index = git(self.worker, 'show', ':form.txt').stdout
        original_worktree = b'identifier\nstatus\nstaged-reviewer\nunstaged-resolution\n'
        tracked.write_bytes(original_worktree)
        note = self.worker / 'unsubmitted-note.txt'
        original_note = b'LF note\nUnsubmitted continuation\n'
        note.write_bytes(original_note)
        (self.baseline / 'shared.txt').write_bytes(b'new public baseline content\n')
        git(self.baseline, 'add', '--', 'shared.txt')
        git(self.baseline, 'commit', '-m', 'Synthetic independent update')
        plan = self.engine.adopt('worker', 'baseline')['plan']['plan_id']
        result = self.engine.adopt('worker', 'baseline', True, plan)
        self.assertEqual('ADOPTED', result['status'])
        self.assertTrue(result['wip_verified'])
        self.assertEqual(original_index, git(self.worker, 'show', ':form.txt').stdout)
        self.assertEqual(original_worktree, tracked.read_bytes())
        self.assertEqual(original_note, note.read_bytes())
        self.assertIn(b'MM form.txt\0', git(self.worker, 'status', '--porcelain=v1', '-z').stdout)

    def test_autocrlf_recovery_never_overwrites_new_user_content(self):
        git(self.worker, 'config', 'core.autocrlf', 'true')
        first = self.worker / 'a-note.txt'
        edited = self.worker / 'z-note.txt'
        first.write_bytes(b'First unsubmitted note\nLF needs preservation\n')
        edited.write_bytes(b'Second unsubmitted note\nOriginal content\n')
        (self.baseline / 'shared.txt').write_bytes(b'new public content\n')
        git(self.baseline, 'add', '--', 'shared.txt')
        git(self.baseline, 'commit', '-m', 'Synthetic public update')
        plan = self.engine.adopt('worker', 'baseline')['plan']['plan_id']
        (self.control / '.taskcarry' / 'SYNTHETIC_TEST_ONLY').write_text('synthetic', encoding='utf-8')
        with patch.dict(os.environ, {'TASKCARRY_TEST_FAULTS': '1'}):
            self.assert_error('INJECTED_INTERRUPTION', self.engine.adopt,
                              'worker', 'baseline', True, plan, fault='after_restore')
        first_after_stash = first.read_bytes()
        advanced_head = commit(self.worker, 'HEAD')
        new_user_content = b'Actual user continuation after interruption\nDo not overwrite this content\n'
        edited.write_bytes(new_user_content)
        self.assert_error('WIP_RESTORE_REQUIRED', self.engine.adopt, 'worker', 'baseline', True, plan)
        self.assertEqual(new_user_content, edited.read_bytes())
        # Every affected file is checked before any newline-only repair starts.
        self.assertEqual(first_after_stash, first.read_bytes())
        self.assertEqual(advanced_head, commit(self.worker, 'HEAD'))
        self.assertEqual(1, len(out(self.worker, 'stash', 'list').splitlines()))

    def test_same_sha_branch_switch_after_plan_is_rejected(self):
        self.deliver('v1', 'identifier\nstatus\nreviewer\n')
        plan = self.engine.reconcile('baseline')['plan']['plan_id']
        git(self.baseline, 'switch', '-c', 'different-writer')
        self.assertEqual(self.base, commit(self.baseline, 'HEAD'))
        self.assert_error('WORKSPACE_CHANGED', self.engine.reconcile, 'baseline', True, plan)
        self.assertEqual(self.base, commit(self.baseline, 'main'))
        self.assertEqual(self.base, commit(self.baseline, 'different-writer'))

    def test_same_sha_branch_switch_during_candidate_preparation_is_rejected(self):
        self.deliver('v1', 'identifier\nstatus\nreviewer\n')
        plan = self.engine.reconcile('baseline')['plan']['plan_id']
        original_fault = self.engine._fault
        def switch_at_candidate(requested, at):
            if at == 'after_candidate':
                git(self.baseline, 'switch', '-c', 'different-writer')
            return original_fault(requested, at)
        with patch.object(self.engine, '_fault', side_effect=switch_at_candidate):
            self.assert_error('BASELINE_CHANGED', self.engine.reconcile, 'baseline', True, plan)
        self.assertEqual(self.base, commit(self.baseline, 'main'))
        self.assertEqual(self.base, commit(self.baseline, 'different-writer'))
        self.assertEqual('QUEUED', self.engine.store.get('stages', 'v1')['status'])
        self.assertEqual('CANDIDATE_READY', self.engine.store.list('operations')[0]['status'])

    def test_three_stage_chain_after_first_accepted_has_no_historical_backlog(self):
        self.deliver('v1', 'identifier\nstatus\nreviewer\n')
        self.receive()
        first_receipt = self.engine.store.get('stages', 'v1')['accepted_commit']
        self.deliver('v2', 'identifier\nstatus\nreviewer\nresolution\n', 'v1')
        self.deliver('v3', 'identifier\nstatus\nreviewer\nresolution\nverified_by\n', 'v2')
        self.assertEqual(['v3'], self.engine.reconcile('baseline')['plan']['stage_ids'])
        result = self.receive()
        self.assertEqual('COMPLETE', result['status'])
        self.assertEqual(['v3'], [r['stage_id'] for r in result['results']])
        for stage_id in ('v1', 'v2'):
            self.assertEqual('SUPERSEDED', self.engine.store.get('stages', stage_id)['status'])
        self.assertEqual(first_receipt, self.engine.store.get('stages', 'v1')['accepted_commit'])
        self.assertEqual([], self.engine.reconcile('baseline')['plan']['stage_ids'])
        self.assertEqual([], self.core.status()['actionable']['stages'])
        self.assertEqual('3', out(self.baseline, 'rev-list', '--count', 'HEAD'))

    def test_legacy_conflict_can_be_closed_by_verified_cumulative_successor(self):
        self.deliver('v1', 'worker proposed content\n')
        (self.baseline / 'form.txt').write_text('reviewed baseline decision\n', encoding='utf-8')
        git(self.baseline, 'add', '--', 'form.txt')
        git(self.baseline, 'commit', '-m', 'Synthetic competing decision')
        self.assertEqual('ACTION_REQUIRED', self.receive()['status'])
        old = self.engine.store.get('stages', 'v1')
        self.assertEqual('CONFLICT', old['status'])
        old_operation = old['operation_id']
        # Explicitly adopt the reviewed decision in a descendant worker commit.
        self.deliver('v2', 'reviewed baseline decision\n', 'v1')
        result = self.receive()
        self.assertEqual('COMPLETE', result['status'])
        self.assertEqual([], result['remaining'])
        historical = self.engine.store.get('stages', 'v1')
        self.assertEqual('SUPERSEDED', historical['status'])
        self.assertEqual('CONFLICT', historical['historical_status'])
        operation = self.engine.store.get('operations', old_operation)
        self.assertEqual('COMPLETED', operation['status'])
        self.assertEqual('v2', operation['resolved_by_successor'])
        self.assertEqual([], self.core.status()['actionable']['operations'])

    def test_latest_cumulative_conflict_never_falls_back_to_older_delivery(self):
        self.deliver('v1', 'identifier\nstatus\nreviewer\n')
        self.deliver('v2', 'latest worker proposal\n', 'v1')
        (self.baseline / 'form.txt').write_text('independent baseline decision\n', encoding='utf-8')
        git(self.baseline, 'add', '--', 'form.txt')
        git(self.baseline, 'commit', '-m', 'Synthetic competing decision')
        first = self.receive()
        self.assertEqual('ACTION_REQUIRED', first['status'])
        self.assertEqual('CONFLICT', self.engine.store.get('stages', 'v2')['status'])
        self.assertEqual('QUEUED', self.engine.store.get('stages', 'v1')['status'])
        head_after_conflict = commit(self.baseline, 'HEAD')
        plan = self.engine.reconcile('baseline')['plan']
        self.assertEqual([], plan['stage_ids'])
        self.assertEqual(['v2'], [s['stage_id'] for s in plan['unresolved']])
        second = self.engine.reconcile('baseline', True, plan['plan_id'])
        self.assertEqual('ACTION_REQUIRED', second['status'])
        self.assertEqual([], second['results'])
        self.assertEqual(head_after_conflict, commit(self.baseline, 'HEAD'))
        self.assertEqual(['v2'], [o['stage_id'] for o in self.engine.store.list('operations')])
        self.assertEqual(['v2'], [s['stage_id'] for s in self.core.status()['actionable']['stages']])

    @unittest.skipUnless(os.name == 'nt', 'Windows junction test')
    def test_untracked_file_under_in_tree_junction_is_rejected(self):
        target = self.worker / 'actual-notes'
        target.mkdir()
        (target / 'draft.txt').write_text('preserve synthetic draft', encoding='utf-8')
        alias = self.worker / 'alias-notes'
        created = subprocess.run(['cmd', '/d', '/c', 'mklink', '/J', str(alias), str(target)], capture_output=True)
        self.assertEqual(0, created.returncode, created.stderr.decode(errors='replace'))
        try:
            self.assert_error('SYMLINK_PATH', fingerprint, self.worker)
            self.assert_error('SYMLINK_PATH', self.engine.adopt, 'worker', 'baseline')
            self.assertEqual('preserve synthetic draft', (target / 'draft.txt').read_text())
            self.assertEqual(self.base, commit(self.worker, 'HEAD'))
        finally:
            alias.rmdir()

    @unittest.skipUnless(os.name == 'nt', 'Windows junction test')
    def test_private_scratch_root_cannot_be_redirected_by_junction(self):
        self.deliver('v1', 'identifier\nstatus\nreviewer\n')
        plan = self.engine.reconcile('baseline')['plan']['plan_id']
        outside = self.root / 'unrelated-target'
        outside.mkdir()
        (outside / 'keep.txt').write_text('synthetic preserve', encoding='utf-8')
        link = self.control / '.taskcarry' / 'scratch'
        created = subprocess.run(['cmd', '/d', '/c', 'mklink', '/J', str(link), str(outside)], capture_output=True)
        self.assertEqual(0, created.returncode, created.stderr.decode(errors='replace'))
        try:
            with self.assertRaises(GovernanceError):
                self.engine.reconcile('baseline', True, plan)
            self.assertEqual(self.base, commit(self.baseline, 'HEAD'))
            self.assertEqual(['keep.txt'], sorted(p.name for p in outside.iterdir()))
        finally:
            link.rmdir()


if __name__ == '__main__':
    unittest.main()
