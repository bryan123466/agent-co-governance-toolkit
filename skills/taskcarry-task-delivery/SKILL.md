---
name: taskcarry-task-delivery
description: Preserve task checkpoints or deliver stable project work through TaskCarry. Use when work pauses, reaches a meaningful stage, or needs continuation; ordinary editing remains independent.
---

# Task continuity and delivery / 接续与交付

Read `taskcarry_status` for the named task, then continue from its current evidence and next step. Register a missing task with `taskcarry_task`. Keep distinct workstreams separate; do not infer that a paused or quiet task is overdue.

Use `taskcarry_checkpoint` at a meaningful pause or milestone. Select exact task-owned relative paths and record the next step and relevant decision. Checkpoints preserve saved work and selected Git layers; they do not capture unsaved editor buffers and do not declare delivery. Avoid secret, unrelated and generated dependency files. Use `taskcarry_restore` only into an empty independent destination.

For an authorized stable delivery, make a precise local Git commit, determine its base, and use `taskcarry_submit` with the exact changed path set. Supply cumulative lineage only when the newer commit covers the older delivered work from the same task; a later timestamp alone is insufficient. The delivery points to frozen commit content, so subsequent workspace edits remain independent.

Large reference artifacts can use `taskcarry_artifact` with content identity and an optional backup path. A recorded location is not proof of an available, matching backup. Record ignore/dismiss decisions only when the user has actually made them.

中文：保存、提交、交付、接收和业务验收分别报告。普通工作不等待治理事务。暂停保留接续点；后续迭代只有证据充分才声明覆盖旧交付，不把历史安静状态重复当积压。
