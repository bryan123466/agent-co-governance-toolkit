"""Bounded intake and durable no-effect adoption failures in synthetic Git repos."""
import os
from unittest.mock import patch

from taskcarry.api import invoke
from taskcarry.core import Core
from taskcarry.gitops import commit, fingerprint, git, out
from taskcarry.integration import Integration
from taskcarry.store import GovernanceError
from test_integration import GitFixture


class BoundedReceiveTests(GitFixture):
    def stages(self, count):
        result = []
        for number in range(count):
            base = commit(self.worker, "HEAD")
            path = f"independent-{number}.txt"
            tip = self.write_commit(self.worker, {path: str(number)})
            result.append(self.engine.submit("forms", "worker", tip, base, [path], stage_id=f"item-{number:02d}")["stage"])
        return result

    def test_default_twenty_and_explicit_limit_bound_actual_intake(self):
        stages = self.stages(21)
        default = self.engine.reconcile("baseline")["plan"]
        self.assertEqual(len(default["stage_ids"]), 20)
        self.assertEqual(default["selection"]["unselected_count"], 1)
        maximum = invoke(self.control, "reconcile", {"baseline": "baseline", "limit": 100})["plan"]
        self.assertEqual(len(maximum["stage_ids"]), 21)
        plan = self.engine.reconcile("baseline", limit=2)["plan"]
        result = self.engine.reconcile("baseline", True, plan["plan_id"], limit=100)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["scope"], "plan")
        self.assertTrue(result["plan_complete"])
        self.assertIsNone(result["project_complete"])
        self.assertEqual(len(result["unselected_queued_stage_ids"]), 19)
        self.assertEqual(result["current_actionable_counts"]["stages"], 19)
        self.assertEqual(self.core.store.get("stages", stages[2]["stage_id"])["status"], "QUEUED")
        self.assertFalse((self.base / "independent-2.txt").exists())
        self.assertEqual(out(self.base, "rev-list", "--count", "HEAD"), "3")

    def test_empty_old_plan_reports_new_queued_work_without_executing_it(self):
        plan = self.engine.reconcile("baseline")["plan"]
        stage = self.delivery()
        result = self.engine.reconcile("baseline", True, plan["plan_id"])
        self.assertTrue(result["plan_complete"])
        self.assertEqual(result["scope"], "plan")
        self.assertIsNone(result["project_complete"])
        self.assertEqual(result["unselected_queued_stage_ids"], [stage["stage_id"]])
        self.assertEqual(commit(self.base, "HEAD"), self.start)

    def test_pending_operations_change_plan_identity_and_do_not_double_count_stage(self):
        self.stages(2)
        original = self.engine.reconcile("baseline", limit=2)["plan"]
        (self.control / ".taskcarry" / "SYNTHETIC_TEST_ONLY").write_text("synthetic")
        with patch.dict(os.environ, {"TASKCARRY_TEST_FAULTS": "1"}):
            with self.assertRaises(GovernanceError):
                self.engine.reconcile("baseline", True, original["plan_id"], fault="after_candidate")
        newer = self.engine.reconcile("baseline", limit=2)["plan"]
        self.assertNotEqual(original["plan_id"], newer["plan_id"])
        self.assertEqual(self.core.store.get("plans", original["plan_id"]), original)
        self.assertEqual(newer["selection"]["selected_count"], 2)
        self.assertEqual(len(newer["pending_operations"]), 1)
        self.assertEqual(len(newer["stage_ids"]), 2)
        result = self.engine.reconcile("baseline", True, newer["plan_id"])
        self.assertTrue(result["plan_complete"])
        self.assertEqual(out(self.base, "rev-list", "--count", "HEAD"), "3")

    def test_only_selected_recovery_operation_is_resumed(self):
        stages = self.stages(2)
        original = self.engine.reconcile("baseline")["plan"]
        (self.control / ".taskcarry" / "SYNTHETIC_TEST_ONLY").write_text("synthetic")
        with patch.dict(os.environ, {"TASKCARRY_TEST_FAULTS": "1"}):
            for stage in stages:
                with self.assertRaises(GovernanceError):
                    self.engine._receive(self.base, stage, original["plan_id"], "after_candidate")
        plan = self.engine.reconcile("baseline", limit=1)["plan"]
        self.assertEqual(plan["selection"]["selected_count"], 1)
        self.assertEqual(len(plan["stage_ids"]), 1)
        self.assertEqual(len(plan["pending_operations"]), 1)
        untouched = [op for op in self.core.store.list("operations") if op["operation_id"] not in plan["pending_operations"]][0]
        result = self.engine.reconcile("baseline", True, plan["plan_id"])
        self.assertTrue(result["plan_complete"])
        self.assertEqual(self.core.store.get("operations", untouched["operation_id"]), untouched)
        self.assertEqual(result["unselected_operation_ids"], [untouched["operation_id"]])
        self.assertEqual(out(self.base, "rev-list", "--count", "HEAD"), "2")

    def test_legacy_plan_without_selection_still_executes_its_exact_scope(self):
        self.stages(1)
        plan = self.engine.reconcile("baseline")["plan"]
        plan.pop("selection")
        plan.pop("pending_operations")
        plan["plan_id"] = "legacy-reviewed-plan"
        self.core.store.put("plans", plan["plan_id"], plan)
        result = self.engine.reconcile("baseline", True, plan["plan_id"])
        self.assertTrue(result["plan_complete"])
        self.assertEqual(len(result["results"]), 1)

    def test_invalid_limits_do_not_create_plans_or_operations(self):
        for limit in (True, 0, 101, 1.5, "2"):
            with self.subTest(limit=limit):
                with self.assertRaises(GovernanceError) as caught:
                    invoke(self.control, "reconcile", {"baseline": "baseline", "limit": limit})
                self.assertEqual(caught.exception.code, "INVALID_ARGUMENT")
        self.assertEqual(self.core.store.list("plans"), [])
        self.assertEqual(self.core.store.list("operations"), [])


class AdoptionPreparationTests(GitFixture):
    def conflict(self):
        (self.worker / "form.txt").write_text("retained incompatible WIP\n")
        self.write_commit(self.base, {"form.txt": "public incompatible content\n"})
        return self.engine.adopt("worker", "baseline")["plan"]

    def fail(self, plan, code="WIP_CONFLICT"):
        with self.assertRaises(GovernanceError) as caught:
            self.engine.adopt("worker", "baseline", True, plan["plan_id"])
        self.assertEqual(caught.exception.code, code)

    def test_actual_preparation_failure_is_visible_after_reopening_and_reuses_checkpoint(self):
        plan = self.conflict()
        before = fingerprint(self.worker)
        self.fail(plan)
        operation = self.core.store.list("operations")[0]
        checkpoint = operation["checkpoint_id"]
        self.assertEqual(operation["status"], "PREPARATION_FAILED")
        self.assertEqual(operation["effect_state"], "NOT_APPLIED")
        self.assertEqual(operation["baseline"], "baseline")
        self.assertNotIn("candidate", operation)
        self.assertNotIn("stash", operation)
        initial_events = len(self.core.store.events())
        self.engine = Integration(self.control)
        agenda = Core(self.control).agenda()
        self.assertEqual(agenda["items"][0]["record_id"], operation["operation_id"])
        self.assertEqual(agenda["items"][0]["code"], "WIP_CONFLICT")
        for _ in range(2):
            self.fail(plan)
        self.assertEqual(len(self.core.store.list("operations")), 1)
        self.assertEqual(len(self.core.store.list("checkpoints")), 1)
        self.assertEqual(len(self.core.store.events()), initial_events)
        self.assertEqual(self.core.store.list("operations")[0]["checkpoint_id"], checkpoint)
        self.assertEqual(fingerprint(self.worker), before)
        self.assertEqual(self.engine.adopt("worker", "baseline")["plan"], plan)

    def test_transient_preparation_failure_retries_same_plan_without_repeating_checkpoint(self):
        (self.worker / "notes.txt").write_text("unfinished notes")
        self.write_commit(self.base, {"public.txt": "accepted progress"})
        plan = self.engine.adopt("worker", "baseline")["plan"]
        with patch("taskcarry.integration.import_commit", side_effect=GovernanceError("TEMPORARY_IMPORT", "Synthetic temporary failure")):
            self.fail(plan, "TEMPORARY_IMPORT")
        failed = self.core.store.list("operations")[0]
        with patch("taskcarry.integration.import_commit", side_effect=GovernanceError("TEMPORARY_IMPORT", "Different scratch diagnostic")):
            self.fail(plan, "TEMPORARY_IMPORT")
        failure_events = [event for event in self.core.store.events() if event["kind"] == "adoption_preparation_failed"]
        self.assertEqual(len(failure_events), 1)
        result = self.engine.adopt("worker", "baseline", True, plan["plan_id"])
        operation = self.core.store.get("operations", failed["operation_id"])
        self.assertTrue(result["wip_verified"])
        self.assertEqual(result["checkpoint_id"], failed["checkpoint_id"])
        self.assertEqual(operation["first_failure"]["code"], "TEMPORARY_IMPORT")
        self.assertEqual(operation["first_failure"]["message"], "Synthetic temporary failure")
        self.assertEqual(operation["last_failure"]["message"], "Different scratch diagnostic")
        self.assertEqual(operation["status"], "COMPLETED")
        self.assertEqual(len(self.core.store.list("checkpoints")), 1)
        self.assertEqual((self.worker / "notes.txt").read_text(), "unfinished notes")

    def test_interruption_before_candidate_can_resume_preparation(self):
        self.write_commit(self.base, {"public.txt": "accepted progress"})
        plan = self.engine.adopt("worker", "baseline")["plan"]
        with patch.object(self.engine, "_prepare_adoption", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.engine.adopt("worker", "baseline", True, plan["plan_id"])
        operation = self.core.store.list("operations")[0]
        self.assertEqual(operation["status"], "PREPARING")
        self.assertEqual(operation["effect_state"], "NOT_APPLIED")
        result = Integration(self.control).adopt("worker", "baseline", True, plan["plan_id"])
        self.assertTrue(result["wip_verified"])
        self.assertEqual((self.worker / "public.txt").read_text(), "accepted progress")

    def test_changed_target_requires_new_plan_and_success_retains_resolves_old_failure(self):
        plan = self.conflict()
        self.fail(plan)
        failed = self.core.store.list("operations")[0]
        # The caller resolves its own WIP; the toolkit must not replay old intent.
        (self.worker / "form.txt").write_text("name\nstatus\n")
        before = fingerprint(self.worker)
        with patch.object(self.engine, "_prepare_adoption", side_effect=AssertionError("Must not prepare stale input")):
            self.fail(plan, "STALE_PLAN")
        self.assertEqual(fingerprint(self.worker), before)
        new = self.engine.adopt("worker", "baseline")["plan"]
        self.assertEqual(new["resolves_preparation_failures"], [failed["operation_id"]])
        self.engine.adopt("worker", "baseline", True, new["plan_id"])
        old = self.core.store.get("operations", failed["operation_id"])
        self.assertEqual(old["status"], "SUPERSEDED")
        self.assertEqual(old["historical_status"], "PREPARATION_FAILED")
        self.assertEqual(old["first_failure"], failed["first_failure"])
        self.assertEqual(old["resolved_by_plan"], new["plan_id"])
        self.assertEqual(Core(self.control).agenda()["counts"]["operations"], 0)
        self.fail(plan, "OPERATION_SUPERSEDED")

    def test_changed_baseline_can_reuse_unchanged_wip_checkpoint(self):
        plan = self.conflict()
        self.fail(plan)
        failed = self.core.store.list("operations")[0]
        self.write_commit(self.base, {"form.txt": "name\nstatus\n", "public.txt": "new baseline"})
        self.fail(plan, "STALE_PLAN")
        new = self.engine.adopt("worker", "baseline")["plan"]
        result = self.engine.adopt("worker", "baseline", True, new["plan_id"])
        self.assertEqual(result["checkpoint_id"], failed["checkpoint_id"])
        self.assertEqual(len(self.core.store.list("checkpoints")), 1)
        self.assertEqual((self.worker / "form.txt").read_text(), "retained incompatible WIP\n")
        self.assertEqual(self.core.store.get("operations", failed["operation_id"])["status"], "SUPERSEDED")

    def test_invalid_or_stale_plan_does_not_create_failure_records(self):
        self.fail({"plan_id": "absent"}, "PLAN_REQUIRED")
        plan = self.engine.adopt("worker", "baseline")["plan"]
        (self.worker / "later.txt").write_text("later work")
        self.fail(plan, "STALE_PLAN")
        self.assertEqual(self.core.store.list("operations"), [])
