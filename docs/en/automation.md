# Scheduled governance that stays focused

[简体中文](../zh-CN/automation.md) · [繁體中文](../zh-TW/automation.md)

Start with one scheduled task in the project's governance chat. It uses the same installed AGCT tools and control directory as manual governance. The AI interprets task evidence; the toolkit plans and records exact local operations. Installing AGCT does not create a scheduler or another AI service.

## Choose the smallest useful arrangement

| Task | Responsibility | Suggested starting point |
|---|---|---|
| Governance | Receive declared stages, continue unfinished operations, explain current progress and concrete next conditions | Twice daily, for example 09:00 and 17:00 in the project's chosen time zone |
| Optional observer | Read current records and runtime information; identify a new failure, inconsistent result or missing evidence | Once daily, after a governance window |
| Separate discovery job | Usually unnecessary at first: governance already inspects registered work | Add only for a distinct source and demonstrated need |

These are examples, not required timings. One governance writer owns a control store and its receiver. An observer is neither a second writer nor an approval step. Keep ordinary task chats working independently. A delayed or missed schedule does not require replaying every missed cycle.

## Copy into the existing governance chat

First ask for one manual pass using the instructions below. Review its actual effects, scope and remaining work. Then use this scheduling request:

> Create a recurring task in this governance chat for the project already connected here, daily at 09:00 and 17:00. Show the resolved time zone and saved schedule. Keep the current model and permissions. On each run use the governance instructions below; the first daily run also supplies the morning summary. Keep quiet when there is no meaningful change, failure or required user action. Do not create a second control directory or activate schedules for another project.

Attach these durable instructions to the scheduled task:

```text
Continue governance for this chat's explicitly connected project using its installed AGCT tools and existing control directory. Use $agct-governance-reconcile and, for a concrete failure, $agct-experience-recovery. Keep project direction and professional acceptance with their existing owners.

Read agenda and only the relevant status detail. Check existing task, checkpoint, delivery, artifact and decision evidence before asking for information. When authorized host tools can read an explicitly connected chat, inspect only changed or specifically missing evidence; otherwise state that coverage is unavailable and continue the work supported by records. Do not infer delivery from file changes or read unrelated chats.

Choose a small receiving batch, normally reconcile limit 20, and inspect the actual frozen plan. An agenda page is not an execution scope. Verify already-applied effects before resuming. Within existing authorization execute the exact plan; preserve unfinished operations and checkpoints. Update business/code workspaces only for an actual dependency need, using adopt. Reading shared progress or updating Skills does not require merging business branches.

Use applicable experience after checking its code, scope and current evidence. A refresh_plan suggestion only proposes a new plan. An unchanged conflict needs its concrete condition resolved, not an identical retry loop. Within authorized development scope fix shared defects and validate a candidate separately from the installed runtime. Retain a named next condition when action is unavailable. Do not nest another full governance run or change host permissions, accounts or schedules to repair a task.

Report the selected plan's result separately from all current remaining work. A completed batch is not project completion. Keep paused tasks and agreed retention decisions out of repeated reminders. At a safe boundary leave the exact operation and next step for continuation. Before ending, check actual receipts once; do not restart historical audits to prepare a report. Notify only for a meaningful change, failure or user action. The first daily run adds the concise morning summary.
```

Skills remain in their normal installed locations. The saved task should include these instructions; a link to an earlier transient chat message is insufficient. Use the scheduling tools supplied by the host, then inspect the saved definition. Avoid hand-editing native scheduling files or embedding credentials in prompts.

## Morning summary and optional observation

A useful summary covers: accepted stages and baseline; workspaces that actually adopted code; unresolved technical work and conditions; meaningful artifact or backup decisions; runtime observations and their coverage; next actions and any user decision. Report only meaningful backup candidates; reuse verified backups and existing retention decisions. A summary describes the observed state at its time. Later completion belongs in a later result.

The AI/host supplies the report and delivery. AGCT does not provide a persistent once-per-day report dispatcher, native chat collector or automatic reminder counter. Configure reminder policies explicitly for the project rather than assuming that silence grants permission.

For an observer, create a separate authorized read-only task with this instruction:

```text
Observe this explicitly connected project's AGCT status, agenda and doctor results. Compare the latest completed governance result with its stated scope, current open operations and runtime evidence. Read only; do not receive, adopt, restore, install, edit task states, start another agent or approve the governance writer. Installation status does not prove that every host process has reloaded. Report a new discrepancy or actionable change with its object and evidence; unchanged retained history needs no notice. An unavailable observation is a coverage gap, not proof of failure or success.
```

## Verify the connection you will actually use

Confirm the saved chat/project, cadence, time zone, model settings, available tools and access to the installed runtime. A CLI test does not establish a live MCP connection or a successful native scheduled trigger. Test the prompt manually, then inspect the first scheduled result. Local-file tasks need the computer and desktop app available. See the [official scheduled-task documentation](https://learn.chatgpt.com/docs/automations?surface=app).

AGCT limits the selected receiving work and preserves supported interruptions. It does not enforce a wall-clock limit on the AI session, stop arbitrary external commands or coordinate multiple computers. Use the host's stop control and keep the journal intact. [Maintenance and safe continuation](governance-maintenance.md) describes the supported local boundaries.
