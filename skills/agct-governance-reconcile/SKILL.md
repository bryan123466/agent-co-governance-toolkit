---
name: agct-governance-reconcile
description: Reconcile explicit deliveries and update project workspaces using AGCT plans and effect evidence. Use for requested governance intake or an authorized scheduled reconciliation.
---

# Governance reconciliation / 治理接收

Read `agct_status`. Distinguish explicit deliveries from checkpoints and unchanged retained task state. Use task, artifact and commit evidence to understand relationships. Formatting differences or an old observation alone do not prove a current business fault. Missing evidence remains missing; do not fabricate author statements or approvals.

Call `agct_reconcile` with the registered baseline and `execute: false`. Inspect the returned finite plan. Within existing user authorization, execute that exact `plan_id` with `execute: true`. A changed baseline requires a fresh plan, not a forced update. Do not add unlisted paths, replay an already accepted stage, push remotely, or declare business acceptance.

To update a registered workspace, use `agct_adopt` preview and then its exact plan. Preserve local commits, index, unstaged and new files. A specific conflict limits that workspace; unrelated tasks continue. The tools' own scope checks do not constrain arbitrary shell commands or grant new user permissions.

When reporting, identify actual accepted stages, retained work, actionable failures and the next condition. Reuse effective receipts. A normal pause or unchanged history needs no repeated prompt. The same workflow may be manually requested or scheduled; scheduling is configured separately in the user's host.

中文：AI 依据实际任务和交付证据判断关联，内核验证并执行有限操作。先计划后执行，只续缺步。公共更新与成果接收不同，技术成功也不等于业务验收；不要用单一 PASS 代替这些状态。
