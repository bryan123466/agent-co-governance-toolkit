# Quick orientation: describe the project and let governance connect it

[Complete Windows workflow](windows-example.md) · [Overview and options](operation-manual.md) · [中文](../zh-CN/getting-started.md)

Open the [complete Windows workflow](windows-example.md). It is the primary installation and operating guide. This page explains the same onboarding path without introducing another set of commands or prompts.

## Prepare the directories and two project inputs

Before first initialization, create `CoGov`, `CoGov/control` and `CoGov/toolkit`. Extract the package directly into `toolkit`, with `START_HERE.md` and `packages/` immediately inside it. Open a governance chat in `control` and follow the main walkthrough.

Provide:

- **Project name: [Enter the project name]**
- **One-sentence introduction: [Describe what the project should do in one sentence]**

Normal operation requires Python 3.11+ and Git. Governance creates the dedicated `runtime` and installs the package. `control` is an ordinary governance directory, not a specialist Git workspace. One root belongs to one real project.

Governance determines whether to establish a first baseline or continue prior work from the actual context; you do not choose a route. **An empty CoGov directory does not prove there are no earlier outputs.** If the context is unclear, governance briefly checks for prior work or obtains the original chat's summary through section 3.1 of the main walkthrough before treating anything as a fresh empty project.

## Add specialists when needed

For new chats, provide **[n: number of new specialist chats]**. Governance adds n workspaces, continuing the existing numbering. You then create a chat for each and choose its directory. Each chat receives **[The actual project work this chat should handle]**. Separate parallel responsibilities when useful; sequential subtasks do not require new chats.

Existing chats join through the same workflow:

1. Paste the main walkthrough's summary prompt into the original chat; it returns its actual directory, Git ownership, task and unfinished work.
2. Send that reply **together with the manual's handoff prompt** to governance.
3. Governance verifies the context, registers the workspace/task and writes a complete continuation prompt for the original chat.
4. Paste that prompt back into the original chat and continue with its existing task, history and WIP.

Suitable workspaces can stay in place. When several old chats share a directory, retain one main specialist writer and preserve scoped work before continuing other parallel responsibilities in separate workspaces. The toolkit does not scan every chat in the app.

## After connection

1. [Governance MCP](windows-example.md#mcp) supplies direct tool calls; the CLI is a fallback to the same engine.
2. The [initial complete inventory](windows-example.md#delivery) covers registered tasks and workspaces. Distinguish already integrated work, stable pending stages, unfinished checkpoints and paused state. Complete coverage does not mean accepting all unfinished outputs.
3. [Configure scheduling if useful](windows-example.md#automation). The host wakes governance to read the actual registered set without a fixed chat count.
4. Continue real work: preserve checkpoints when pausing, declare stable stages, then receive and update eligible workspaces as needed.

For an installed project, continue its current state rather than initializing again. [Private Git, backups and multiple computers](remote-and-multicomputer.md) remain optional; unused options are not a backlog.
