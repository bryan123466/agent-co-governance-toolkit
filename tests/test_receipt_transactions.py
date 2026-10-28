"""Interrupt receipt storage after real Git effects, then continue once."""
from unittest.mock import patch

from tests.test_integration import GitFixture
from taskcarry.integration import Integration
from taskcarry.gitops import commit, fingerprint
from taskcarry.store import GovernanceError


class ReceiptTransactionTests(GitFixture):
    def fail_event(self, kind):
        original = self.engine.store.event

        def save(event, payload):
            if event == kind:
                raise OSError('synthetic receipt storage interruption')
            return original(event, payload)
        return save

    def test_receive_event_failure_retains_effect_and_retries_only_receipt(self):
        stage = self.delivery()
        pid = self.plan()
        with patch.object(self.engine.store, 'event', side_effect=self.fail_event('stage_received')):
            with self.assertRaises(OSError):
                self.execute(pid)
        head = commit(self.base, 'HEAD')
        self.assertNotEqual(self.start, head)
        reopened = Integration(self.control)
        self.assertEqual('QUEUED', reopened.store.get('stages', stage['stage_id'])['status'])
        self.assertEqual('EFFECT_APPLIED', reopened.store.list('operations')[0]['status'])
        result = reopened.reconcile('baseline', True, pid)
        self.assertTrue(result['plan_complete'])
        self.assertTrue(result['results'][0]['recovered'])
        self.assertEqual(head, commit(self.base, 'HEAD'))
        reopened.reconcile('baseline', True, pid)
        received = [e for e in reopened.store.events() if e['kind'] == 'stage_received']
        applied = [e for e in reopened.store.events() if e['kind'] == 'experience_applied']
        self.assertEqual(1, len(received))
        self.assertEqual(1, len(applied))

    def test_adopt_event_failure_preserves_wip_and_finalizes_without_replay(self):
        self.write_commit(self.base, {'rules.txt': 'accepted policy\n'})
        (self.worker / 'draft.txt').write_bytes(b'unfinished\r\n')
        pid = self.engine.adopt('worker', 'baseline')['plan']['plan_id']
        with patch.object(self.engine.store, 'event', side_effect=self.fail_event('workspace_adopted')):
            with self.assertRaises(OSError):
                self.engine.adopt('worker', 'baseline', True, pid)
        after = fingerprint(self.worker)
        self.assertNotEqual('COMPLETED', self.engine.store.list('operations')[0]['status'])
        reopened = Integration(self.control)
        self.assertEqual('ADOPTED', reopened.adopt('worker', 'baseline', True, pid)['status'])
        self.assertEqual(after, fingerprint(self.worker))
        self.assertEqual(b'unfinished\r\n', (self.worker / 'draft.txt').read_bytes())
        reopened.adopt('worker', 'baseline', True, pid)
        self.assertEqual(1, len([e for e in reopened.store.events() if e['kind'] == 'workspace_adopted']))

    def test_unknown_plan_protocol_rejected_without_git_effect(self):
        self.delivery()
        pid = self.plan()
        plan = self.engine.store.get('plans', pid)
        plan['operation_protocol'] = 999
        self.engine.store.put('plans', pid, plan)
        before = fingerprint(self.base)
        with self.assertRaises(GovernanceError) as error:
            self.execute(pid)
        self.assertEqual('OPERATION_PROTOCOL_UNSUPPORTED', error.exception.code)
        self.assertEqual(before, fingerprint(self.base))
        self.assertEqual([], self.engine.store.list('operations'))

    def test_legacy_untagged_plan_and_operation_continue(self):
        self.delivery()
        pid = self.plan()
        plan = self.engine.store.get('plans', pid)
        plan.pop('operation_protocol')
        plan.pop('created_with_version')
        self.engine.store.put('plans', pid, plan)
        with patch.object(self.engine.store, 'event', side_effect=self.fail_event('stage_received')):
            with self.assertRaises(OSError):
                self.execute(pid)
        op = self.engine.store.list('operations')[0]
        op.pop('operation_protocol')
        op.pop('created_with_version')
        self.engine.store.put('operations', op['operation_id'], op)
        head = commit(self.base, 'HEAD')
        self.assertTrue(self.execute(pid)['plan_complete'])
        self.assertEqual(head, commit(self.base, 'HEAD'))

    def test_unknown_resume_protocol_keeps_real_effect_unreplayed(self):
        self.delivery()
        pid = self.plan()
        with patch.object(self.engine.store, 'event', side_effect=self.fail_event('stage_received')):
            with self.assertRaises(OSError):
                self.execute(pid)
        op = self.engine.store.list('operations')[0]
        op['operation_protocol'] = 999
        self.engine.store.put('operations', op['operation_id'], op)
        before = fingerprint(self.base)
        with self.assertRaises(GovernanceError) as error:
            self.execute(pid)
        self.assertEqual('OPERATION_PROTOCOL_UNSUPPORTED', error.exception.code)
        self.assertEqual(before, fingerprint(self.base))
        self.assertEqual('EFFECT_APPLIED', self.engine.store.get('operations', op['operation_id'])['status'])
