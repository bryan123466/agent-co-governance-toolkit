# Getting started: connect your project progress and working chats

[Complete Windows workflow](windows-example.md) · [Overview and options](operation-manual.md) · [简体中文](../zh-CN/getting-started.md) · [繁體中文](../zh-TW/getting-started.md)

Keep your existing local AI working chats, or add independent chats for work that needs to proceed in parallel. Governance uses the task and file information you provide to organize progress and collect ready stages. The concrete walkthrough uses Codex; other hosts need their own CLI/MCP connection and instruction-loading verification.

Follow the [complete Windows workflow](windows-example.md) for installation, copyable prompts, and commands. This page explains how you will use the project afterward.

## Prepare the directories and two project inputs

Before first initialization, create `TaskCarry`, `TaskCarry/control` and `TaskCarry/toolkit`. Extract the package directly into `toolkit`, with `START_HERE.md` and `packages/` immediately inside it. Open a governance chat in `control` and follow the main walkthrough.

Provide:

- **Project name: [Enter the project name]**
- **One-sentence introduction: [Describe what the project should do in one sentence]**

Normal operation requires Python 3.11+ and Git. Governance creates the dedicated `runtime` and installs the package. `control` is an ordinary governance directory, not a specialist Git workspace. One root belongs to one real project.

Governance determines whether to establish a first baseline or continue prior work from the actual context; you do not choose a route. **An empty TaskCarry directory does not prove there are no earlier outputs.** If the context is unclear, governance briefly checks for prior work or obtains the original chat's summary through section 3.1 of the main walkthrough before treating anything as a fresh empty project.

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
2. [Run the first bounded governance pass](windows-example.md#delivery) in the current chat. It reports installation, connection, registered work, actual results and your next step. Without deliverables, it reports readiness without creating sample work. Unfinished tasks keep their progress and next steps.
3. [Configure scheduling if useful](windows-example.md#automation), reusing the first pass rather than repeating it. The host wakes governance to use the same Skill and tools; daily results continue in the chat.
4. Continue your work. When pausing, save the files and next step you want to retain. Offer a stable stage to governance when it is ready, then update eligible workspaces as needed. The toolkit calls a saved progress record a checkpoint.

History and pause points remain available. When returning to an installed project, continue from its current state rather than initializing again. [Private Git, backups and multiple computers](remote-and-multicomputer.md) remain optional; unused options are not a backlog.
