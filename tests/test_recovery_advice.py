"""Recovery advice is bounded data and must never execute a new plan."""
from pathlib import Path
import tempfile
import unittest

from taskcarry.api import invoke
from taskcarry.core import Core


class RecoveryAdviceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='taskcarry-advice-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'control'
        Core.initialize(self.root, 'Synthetic recovery advice')
        self.core = Core(self.root)
        self.core.task('draft', 'Draft')
        self.plan = {'plan_id': 'adopt-plan-demo', 'kind': 'adopt',
                     'workspace': 'author', 'baseline': 'main'}
        self.op = {'operation_id': 'attempt', 'kind': 'adopt', 'task_id': 'draft',
                   'plan_id': self.plan['plan_id'], 'workspace': 'author',
                   'status': 'PREPARATION_FAILED', 'code': 'WIP_CONFLICT',
                   'effect_state': 'NOT_APPLIED'}
        self.core.store.put('plans', self.plan['plan_id'], self.plan)
        self.core.store.put('operations', 'attempt', self.op)
        self.core.experience('review-preparation', 'WIP_CONFLICT', 'adopt',
                             'refresh_plan', task_id='draft')

    def advice(self):
        return invoke(self.root, 'agenda', {'limit': 1})['items'][0]['experience_candidates']

    def test_advice_prepares_a_call_but_does_not_mutate(self):
        before = self.core.store.snapshot(('plans', 'operations', 'experience'))
        suggestion = self.advice()[0]
        self.assertEqual({'action': 'adopt', 'arguments': {
            'workspace': 'author', 'baseline': 'main', 'execute': False}}, suggestion['plan_request'])
        self.assertEqual('proposal_only', suggestion['execution'])
        self.assertTrue(suggestion['requires_new_plan_review'])
        self.assertEqual(before, Core(self.root).store.snapshot(('plans', 'operations', 'experience')))

    def test_possible_effect_never_suggests_a_replacement_plan(self):
        for extra in ({'candidate': 'abc'}, {'stash': 'abc'}, {'effect_state': 'UNKNOWN'}):
            with self.subTest(extra=extra):
                self.core.store.put('operations', 'attempt', {**self.op, **extra})
                suggestion = self.advice()[0]
                self.assertNotIn('plan_request', suggestion)
                self.assertEqual('candidate_only', suggestion['execution'])

    def test_rule_scope_and_version_are_checked_before_advice(self):
        for change in ({'task_id': 'different'}, {'version': '0'}, {'enabled': False}):
            with self.subTest(change=change):
                rule = {'rule_id': 'review-preparation', 'code': 'WIP_CONFLICT',
                        'operation': 'adopt', 'action': 'refresh_plan', 'task_id': 'draft',
                        'version': '1', 'enabled': True, **change}
                self.core.store.put('experience', rule['rule_id'], rule)
                self.assertEqual([], self.advice())

    def test_missing_or_mismatched_plan_remains_evidence_gap(self):
        for plan_id, kind in (('missing', 'adopt'), (self.plan['plan_id'], 'reconcile')):
            with self.subTest(plan_id=plan_id, kind=kind):
                self.core.store.put('plans', self.plan['plan_id'], {**self.plan, 'kind': kind})
                self.core.store.put('operations', 'attempt', {**self.op, 'plan_id': plan_id})
                self.assertNotIn('plan_request', self.advice()[0])


if __name__ == '__main__':
    unittest.main()
