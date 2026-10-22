# How the toolkit keeps a project moving

[简体中文](../zh-CN/architecture.md) · [繁體中文](../zh-TW/architecture.md) · [Home](../../README.md)

When several Codex chats work on a project, each needs to know what to do next without losing its earlier work. Agent Co-Governance Toolkit gives them a shared set of task records and a governance chat that brings ready results together. Files and progress remain on your computer; the project does not depend on one chat remembering everything.

## Who does what

You set the direction, divide responsibilities, and decide whether a result meets your needs. Professional chats work in their own registered directories. The governance chat uses AI to interpret their task records and deliverables, then calls the tools to save state, collect stages, and update workspaces.

| Part | What it does for you |
|---|---|
| Task records | Keep the goal, current position, decisions, saved progress, and next step together. |
| Git workspaces | Give parallel tasks separate working files and retain their change history. |
| Receiving baseline | Hold the stages already collected into the shared project. |
| CLI and MCP | Offer two ways to call the same local tools and records. |
| Project Skills | Explain when and how the chats should save progress, deliver work, and handle a known problem. |
| Optional host scheduling | Wake the governance chat at configured times to perform the same workflow. |

## From unfinished work to the next stage

1. **Work on the task.** A professional chat uses its registered workspace and stable task record.
2. **Save a useful pause point.** A checkpoint records selected files already saved to disk and where to continue. Within its selected scope, a Git checkpoint keeps the committed version, staged changes, working files, and new files distinguishable.
3. **Offer a ready stage.** The chat identifies the Git commit, its starting commit, and the complete changed-path list. Later edits in that workspace do not silently change the offered stage.
4. **Bring it into the shared project.** Governance prepares a plan against the current receiving baseline, checks its scope, and executes it. If the baseline changes first, it prepares a new plan using the current facts.
5. **Update workspaces that are ready.** A separate update plan preserves supported local work. A busy workspace or a concrete conflict keeps its own next step while other independent tasks continue.
6. **Continue.** The records show what was collected, what is still in progress, and what should happen next. You still decide whether the result satisfies the business or professional requirements.

## Keep history without repeating old work

A pause remains a pause; an unchanged task does not become new backlog on every run. Old stages remain traceable after a newer cumulative stage replaces them. Before replacing one, the tools require evidence that the newer stage belongs to the same task and registered workspace, descends from the earlier commit, and covers its changed paths. A newer filename or date alone is not enough; independent results remain separate.

After an interrupted operation, governance checks what actually happened before continuing. It reuses valid records and completes only the missing steps supported by the tools, rather than assuming that a missing reply means the whole operation failed.

## Reuse experience where it applies

An experience record describes a known problem and an available recovery action. The tools check its failure code, operation, version, task scope, and enabled state before applying it. This can help with a repeated problem under matching conditions. It does not turn a written note into a new repair capability or execute arbitrary scripts from that note.

For an unfamiliar problem, governance explains the concrete obstacle and next step. A general prevention fix still requires a change to the shared software and verification before it is installed; recording experience alone does not install that fix or guarantee that the model will select it.

## Where the records live

The project's `.agct` directory stores its task database, events, experience records, and selected-file snapshots. Keep these as project data, with suitable backups. Do not publish the database or edit it to make an incomplete operation look successful.

The tools run locally on one computer. Separate worktrees support parallel tasks; multi-computer work needs the explicit branch-based handoff described in the manual. The toolkit does not provide distributed locks, automatic remote push or deployment, or guaranteed recovery of effects in external services.

AI comes from your Codex environment. The toolkit does not train a model or require its own model API. Skills do not grant extra permissions; Codex connections and scheduling are enabled through the host's supported settings. See [practical capabilities and limits](../RELEASE_BOUNDARIES.md).
