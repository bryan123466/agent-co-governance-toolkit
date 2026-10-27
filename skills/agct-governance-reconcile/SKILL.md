---
name: agct-governance-reconcile
description: Reconcile explicit deliveries and update project workspaces using AGCT plans and effect evidence. Use for requested governance intake or an authorized scheduled reconciliation.
---

# Governance reconciliation / 治理接收

Start with `agct_agenda` for a bounded current-work selection. Follow `next_cursor` while the input fingerprint remains valid; changed input requires a fresh selection. `changed: false` is a comparison, not proof that pending work is resolved. The agenda never executes, retries or starts another agent. Use `agct_status` when full recorded detail is needed. Distinguish explicit deliveries from checkpoints and unchanged retained task state. Use task, artifact and commit evidence to understand relationships. Formatting differences or an old observation alone do not prove a current business fault. Missing evidence remains missing; do not fabricate author statements or approvals.

Call `agct_reconcile` with the registered baseline, `execute: false` and a suitable `limit` (default 20, maximum 100). The count bounds selected receiving work, including unfinished receipts; an agenda page is not an execution scope. Inspect the actual returned plan, then execute that exact `plan_id` within existing user authorization. Plan completion only covers its frozen selection: inspect the separately reported remaining work before describing the current queue. A later delivery belongs to a later plan. First verify the actual effects of unfinished operations and resume applicable missing steps. When relevant inputs invalidate a plan and no applied effect requires continuation, inspect the error and request a fresh plan. Do not force an update, add unlisted paths, replay an accepted stage, push remotely, or declare business acceptance.

Use `agct_adopt` only when a task needs the accepted business/code baseline, previewing and executing its exact plan. Preserve local commits, index, unstaged and new files. Updating toolkit Skills or reading shared progress does not require adopting a business branch. A specific conflict limits that workspace; unrelated tasks continue. The tools' own scope checks do not constrain arbitrary shell commands or grant new user permissions.

When reporting, identify actual accepted stages, retained work, actionable failures and the next condition. Reuse effective receipts. A normal pause or unchanged history needs no repeated prompt. The same workflow may be manually requested or scheduled; scheduling is configured separately in the user's host.

For a schedule, keep one governance writer for this control store and receiving baseline. An optional observer only reads. Read current records before requesting chat context; when authorized host tools expose relevant chats, inspect only changed or specifically missing evidence. AGCT does not discover or read chats itself. A scheduled turn need not scan every historical receipt or exhaust every page. Finish its selected work or preserve an explicit next condition; use the host's stop mechanism at a safe boundary. AGCT has no hard AI-session timer. Separate a deep product repair from a routine intake, and keep independent professional work moving. Notify on meaningful change, failure or required action; unchanged retained work does not need repeated reminders.

中文：AI 依据实际任务和交付证据判断关联，内核验证并执行有限操作。先计划后执行，只续缺步。公共更新与成果接收不同，技术成功也不等于业务验收；不要用单一 PASS 代替这些状态。
