# Architecture and workflow

[简体中文](../zh-CN/architecture.md) · [繁體中文](../zh-TW/architecture.md) · [Home](../../README.md)

Agent Co-Governance Toolkit keeps durable project state outside the model's conversation. One local core owns the records and mutations. A CLI, local MCP server, and project Skills present that core to people and Codex.

## Components

| Component | Responsibility |
|---|---|
| Core and store | Tasks, immutable selected-file snapshots, artifacts, scoped experience, events, current state |
| Git integration | Frozen delivery validation, plans, local baseline integration, effect checks, workspace adoption |
| CLI | JSON request files and machine-readable result envelopes |
| MCP | Typed tools fixed to a configured project; no alternative execution engine |
| Skills | When to record, deliver, reconcile, or inspect a failure; no new authority |
| Optional scheduler | Invokes the existing workflow under the host's actual capabilities |

Durable state lives under the configured project's `.agct` directory. Treat it and its snapshots as project data. It is not meant to be committed or copied into a public issue. Do not edit the database to force a successful result.

## Work moves through explicit boundaries

1. A worker records a task and works in a registered Git workspace.
2. At a pause or useful boundary it records a checkpoint of exact selected saved files. Git snapshots preserve distinctions between HEAD, index, worktree bytes, and untracked files where covered.
3. A stable stage is explicitly delivered with a commit, base commit, and exact changed paths. Mutable workspace contents are not the frozen delivery.
4. Governance plans against an exact baseline HEAD. An execution request names the persisted plan. Changed prerequisites require a new plan, not broad reapproval of the business goal.
5. Integration verifies actual Git effects and records terminal results. On interruption, the next call checks those effects before considering missing steps.
6. A separate adoption plan updates a registered worktree if its current local work can be preserved. A conflict is reported for that workspace rather than reinterpreted as a failure of every task.

Technical acceptance never certifies business meaning, regulatory compliance, or customer approval.

## Iteration and history

Independent stages remain independent. A cumulative stage must explicitly identify what it supersedes, stay in the same task, prove ancestor relationships, and cover the earlier changed paths. A timestamp, version label, or similar filename is insufficient proof.

History remains available after supersession; it does not automatically remain in the actionable queue. Paused or unchanged work remains a current state, not a repeatedly escalating backlog. Do not infer that a user abandoned a task merely because no new instruction arrived.

## Experience must affect action

An experience rule contains a failure code, operation, supported version, optional task scope, enabled flag, and a supported recovery action. Matching similar prose is not enough. In this RC the allowed actions are bounded tool behaviors, not shell scripts supplied by an experience record.

Known recovery still verifies current prerequisites. Stale, disabled, unsupported-version, and wrong-task rules must not authorize an action. An unfamiliar issue is retained with a concrete next step. It is not relabeled solved because an explanation was written.

Source-level prevention follows a separate maintenance step: reproduce with synthetic data, change the shared implementation, run regression coverage, then release it. Saving an experience record alone does not install a patch or prove the model will use it.

## Boundaries

The RC is local and single-host. Local worktrees can represent parallel task streams. It does not implement distributed leases, multi-host consensus, remote Git push, deployment, or cross-chat scheduling. A local operation journal cannot guarantee exactly-once effects in arbitrary external services.

No agent can obtain additional native permissions by writing a project rule. The model is provided by the user's Codex environment; this toolkit does not train a model or hide a second required inference service.
