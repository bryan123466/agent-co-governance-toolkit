---
name: agct-experience-recovery
description: Diagnose a concrete AGCT failure and apply or propose a condition-bound recovery. Use after an actual tool failure or interrupted operation, not for routine historical rechecking.
---

# Conditional recovery / 条件经验恢复

Start with the current error code, operation journal and actual Git/file effects. If an effect already happened, preserve that fact and repair only missing bookkeeping. Do not infer absence from a missing receipt, erase old evidence, or repeat the complete workflow.

AGCT's experience rules are data, not shell programs. `agct_experience` accepts only the implemented actions `verify_and_finalize` and `refresh_plan`. Bind a rule to an observed code and operation; add task scope when the evidence is task-specific. Enabled/version checks and applicability must hold before use. Similar wording alone is not a match.

For known recovery, repeat the original bounded governance call so the engine verifies effects and uses an applicable rule. Inspect the returned experience-use and completion evidence. If the effect cannot be established or the condition changed, retain an actionable issue and specify the missing fact. No unbounded retries, fake completion, expanded write scope or bypassed host permissions.

Unknown defects can produce a candidate fix and synthetic regression scenario within authorized development scope. Validate the initial failure, the corrected outcome, replay safety and a negative non-applicable case before proposing a public rule/tool update. Never experiment on a user's live unrelated task. Record whether only scripts, simulated clients or an actual AI/host integration were tested.

中文：经验闭环应降低源头复现，也应帮助中断接续。条件经验不能扩大权限，不能把过期经验强套新任务。未知情况保留实际证据，形成可验证的修正候选，不让一个任务冻结全项目。
