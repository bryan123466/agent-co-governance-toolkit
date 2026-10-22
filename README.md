# Agent Co-Governance Toolkit

**Connect governance to your real Codex project: preserve task progress, receive stable work and update independent workspaces.**

[Download v0.2.0rc1](https://github.com/bryan123466/agent-co-governance-toolkit/releases/tag/v0.2.0rc1) · [Complete Windows guide](docs/en/windows-example.md) · [简体中文](README.zh-CN.md)

Version **0.2.0rc1**. A local toolkit for people already using Codex and Git. The model interprets task evidence; a shared CLI/MCP engine records state, checks conditions and performs supported Git operations.

## Start here

1. **Download and prepare.** Get the [v0.2.0rc1 product package](https://github.com/bryan123466/agent-co-governance-toolkit/releases/tag/v0.2.0rc1), create `CoGov`, `CoGov/control` and `CoGov/toolkit`, and extract the product directly into `toolkit`. The [Windows guide](docs/en/windows-example.md#choose) gives the complete steps.
2. **Connect your project.** Open a governance chat in `control`, provide **[Project name]** and **[One-sentence introduction]**, and send the [installation prompt](docs/en/windows-example.md#install). Governance checks the actual context before establishing a first baseline or continuing prior work. An empty CoGov directory does not prove there are no earlier outputs; unclear context is checked first.
3. **Connect your working chats and continue.** Follow the [specialist-chat onboarding](docs/en/windows-example.md#agents), [MCP setup](docs/en/windows-example.md#mcp) and [first current-state inventory](docs/en/windows-example.md#delivery). Governance receives declared stable work and preserves unfinished work as state. The CLI remains available through the same engine and control directory.

**One CoGov directory belongs to one real project.** Before first initialization, you can choose a different root and consistently adjust its paths. Renaming or moving an already bound project is not a supported migration method.

For new specialist chats, provide **[n: number of new specialist chats]** and **[The actual project work this chat should handle]**. Governance adds n independent workspaces, continuing the existing numbering. Split chats by parallel responsibilities; sequential subtasks can stay in the same chat. No preset team or demonstration business is required.

[Existing chats can continue](docs/en/windows-example.md#existing): paste the manual's prompt into the original chat → send its reply together with the manual's handoff prompt to governance → receive a return prompt after registration → paste it back into the original chat. Preserve its tasks, history and work in progress (WIP). If old chats share a directory, keep one main writer there and continue other parallel responsibilities in independent workspaces, preserving their history and scoped WIP.

An optional [scheduled governance task](docs/en/windows-example.md#automation) uses the actual registered workspaces and tasks, with no fixed worker count.

## The working loop

`work → checkpoint when useful → declare a stable stage → plan and receive → adopt when needed → continue`

- **Checkpoint:** selected saved files, decisions and next steps remain recoverable. It is not a delivery.
- **Stable stage:** exact frozen Git changes are offered for reception. Later worker edits do not change the offer.
- **Receiving baseline:** integration effects are checked. Business acceptance remains a separate decision.
- **Workspace adoption:** update a workspace that is ready, preserving supported local work and reporting concrete conflicts.
- **Conditional recovery:** use an applicable implemented recovery action, inspect actual effects and continue missing steps. A written experience alone does not add a new executable capability.

An unchanged paused task remains available for continuation without becoming repeated backlog. Cumulative replacement needs explicit ancestry and scope evidence; a newer timestamp is insufficient.

## Requirements and scope

Python **3.11+**, Git for the normal checkpoint/reception workflow, and your existing Codex for model-assisted use. The toolkit runtime uses the Python standard library and does not call a model API itself.

This release uses one local control database and one receiving baseline per project. Multiple task workspaces may operate on that computer. Keep one main writer per task/workspace and prevent outside writes while a workspace is being updated. The toolkit does not scan every app chat, infer that every paused task is idle, create its own scheduler or repair the operating system.

The generated MCP fragment requires actual host configuration and a successful tool call before it is connected. A scheduled prompt is configured through the host's automation tools, separately from toolkit installation. Remote push and cross-computer state migration are not built-in operations; the optional multi-computer procedure uses task branches and one integration host.

## Documentation

- [Complete Windows workflow and copyable prompts](docs/en/windows-example.md)
- [Quick orientation](docs/en/getting-started.md)
- [Workflow overview and supported choices](docs/en/operation-manual.md)
- [Private Git, backups and multi-computer task branches](docs/en/remote-and-multicomputer.md)
- [Architecture](docs/en/architecture.md) · [Command reference](docs/COMMANDS.md)
- [Operating scope](docs/RELEASE_BOUNDARIES.md) · [Security](SECURITY.md)
- [Offline bilingual workflow diagram](docs/index.html)

## Languages and license

**English and Simplified Chinese are officially maintained.** The main guides link to their matching language versions. Other languages can be added through community translations under `docs/<language>/`; keep commands, supported scope and safety requirements consistent with the maintained versions. A translation is not official support until it is reviewed and designated as maintained.

The [MIT license](LICENSE) applies to independently authored public files. See [LICENSE_SCOPE.md](LICENSE_SCOPE.md) for scope.
