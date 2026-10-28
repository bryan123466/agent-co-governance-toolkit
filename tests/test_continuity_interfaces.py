"""Public dispatch and current-work projection of durable review evidence."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from taskcarry.api import invoke
from taskcarry.core import Core
from taskcarry.mcp import Server
from tests.test_interfaces import initialize, request


class ContinuityInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='taskcarry-public-evidence-')
        self.root = Path(self.tmp.name)
        invoke(self.root, 'init')
        self.core = Core(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_issue_reaches_agenda_then_resolved_evidence_leaves_current_selection(self):
        server = Server(self.root)
        server.handle(initialize())
        args = {'issue_id': 'format', 'condition': 'source-v1', 'summary': 'Synthetic malformed field'}
        first = server.handle(request('tools/call', {'name': 'taskcarry_issue', 'arguments': args}))
        self.assertFalse(first['result']['isError'])
        self.assertEqual(['issue:format'], [i['id'] for i in invoke(self.root, 'agenda')['items']])
        before = self.core.store.events()
        self.assertTrue(invoke(self.root, 'issue', args)['reused'])
        self.assertEqual(before, self.core.store.events())
        invoke(self.root, 'issue', {**args, 'state': 'resolved', 'resolution_ref': 'synthetic-check-1', 'expected_revision': 1})
        self.assertEqual([], invoke(self.root, 'agenda')['items'])
        self.assertEqual('resolved', invoke(self.root, 'status')['continuity']['issues'][0]['state'])

    def test_unfinished_run_reads_only_its_observation_dependencies(self):
        store = self.core.store
        store.put('observations', 'linked', {'observation_id': 'linked', 'fingerprint': 'v1'})
        store.put('observations', 'unrelated', {'observation_id': 'unrelated', 'fingerprint': 'v1'})
        invoke(self.root, 'run', {'run_id': 'round', 'observation_ids': ['linked']})
        first = invoke(self.root, 'agenda')
        self.assertEqual(['run:round'], [i['id'] for i in first['items']])
        store.put('observations', 'unrelated', {'observation_id': 'unrelated', 'fingerprint': 'v2'})
        self.assertFalse(invoke(self.root, 'agenda', {'previous_fingerprint': first['fingerprint']})['changed'])
        store.put('observations', 'linked', {'observation_id': 'linked', 'fingerprint': 'v2'})
        self.assertTrue(invoke(self.root, 'agenda', {'previous_fingerprint': first['fingerprint']})['changed'])
        finished = invoke(self.root, 'run', {'run_id': 'round', 'mode': 'finish'})
        self.assertEqual(['linked'], finished['inspection']['changed_observations'])
        self.assertEqual([], invoke(self.root, 'agenda')['items'])
        self.assertIsNone(finished['inspection']['project_complete'])

    def test_cli_and_mcp_share_index_upgrade_and_run_inspection(self):
        invoke(self.root, 'run', {'run_id': 'empty'})
        proc = subprocess.run([sys.executable, '-B', '-m', 'taskcarry', '--project', str(self.root),
                               'run', '--json', json.dumps({'run_id': 'empty', 'mode': 'inspect'})],
                              capture_output=True, text=True, timeout=20)
        self.assertEqual(0, proc.returncode, proc.stderr + proc.stdout)
        self.assertTrue(json.loads(proc.stdout)['result']['inspection']['selected_complete'])
        server = Server(self.root)
        server.handle(initialize())
        result = server.handle(request('tools/call', {'name': 'taskcarry_upgrade', 'arguments': {}}))
        self.assertFalse(result['result']['isError'])
        self.assertFalse(result['result']['structuredContent']['result']['upgraded'])
