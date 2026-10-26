# Keep governance current while work continues

[简体中文](../zh-CN/governance-maintenance.md) · [繁體中文](../zh-TW/governance-maintenance.md)

AGCT keeps project records in the control directory while the installed toolkit provides the operations that use them. Updating the toolkit should help the next session continue the same work. It should not create a new project, resubmit past results, or merge business branches simply to refresh a Skill.

This supplement applies to 0.2.0rc2. The existing installation and operating walkthroughs remain applicable. Start a new project with the normal walkthrough; the arrangements below help maintain an existing installation.

## Three updates with different purposes

| What changes | How to use it |
|---|---|
| Toolkit and project Skills | Install the chosen wheel in the dedicated runtime, preview project setup, then install the managed integration files. Keep the existing control state. |
| Shared project progress | Read `status` or `agenda` from the same control directory. Reading progress does not require changing a worker's Git branch. |
| Accepted code or deliverables needed by a worker | Use an explicit `adopt` plan. This is a business/code update and keeps its existing conflict and WIP checks. |

## Start a governance turn with current work

`agenda` gives the existing AI a limited selection of unfinished operations, submitted stages, and artifacts needing a decision. Paused or waiting tasks stay recorded without becoming extra deliveries. Completed history remains available through the full status and records.

```json
{"limit": 20}
```

Send this to `agct_agenda`, or use the CLI `agenda` action with a JSON request file. Follow `next_cursor` to inspect remaining pages. A cursor belongs to the same current-input fingerprint; if work changes, start a fresh selection. Pass the previous `fingerprint` as `previous_fingerprint` when comparing observations. `changed: false` does not close pending work or authorize another attempt.

Selection does not perform a repair, run another AI, or start a schedule. Matching experience is a suggestion; the existing executor must still verify actual effects. The item limit bounds the response, not database scanning costs, query time, or the duration of an AI session.

## Resume an interrupted installation

Setup saves an exact installation intent before changing managed files. If it stops after writing a file but before recording the result, repeating the same install can recognize that effect and finish the record. Files that have already reached the expected state do not need to be rewritten.

If you have edited a managed file, or selected a different candidate while an installation is pending, setup preserves the evidence and reports the conflict. Keep the pending record and use the original candidate to diagnose or resume; deleting metadata is not a recovery method. Unmanaged files are not adopted merely because they happen to match a packaged file.

While setup is changing its managed files, avoid editing those same files in another application. Its lock coordinates setup operations; it does not lock every external editor.

## Confirm which version is actually running

`doctor.runtime` reports the package version, interpreter and module location imported by the process answering the request, together with managed setup information. A successful CLI check does not prove a previously opened MCP process has reloaded. After deliberately updating its configuration or restarting that connection, check through that connection too.

Source fingerprints describe the files currently on disk. They do not prove that a long-running process has replaced previously imported code. Restart the affected MCP connection after changing the runtime package; `loaded_code_verified` remains false rather than asserting in-memory code attestation.

For AGCT's own development, run governance from an installed wheel outside the editable source checkout. Develop and test the next version separately. Adopt it when the affected operations are safely stopped. Keep the control directory: tasks, checkpoints and previous receipts belong to the project, not a particular toolkit build. This release does not include a general automatic package upgrader or a cross-schema rollback engine.

## One governance chat, separate repository scopes

One control store still has one receiving baseline. A product with two independent repositories can use two control stores and one common project overview maintained by its governance chat. Give each MCP connection an explicit distinct `server_name` during setup, for example `product_core` and `product_app`; subsequent setup calls retain the chosen name.

```json
{"mode": "preview", "server_name": "product_core"}
```

After reviewing the result, use `mode: install` with the same name. The generated fragment still requires deliberate host configuration; it is not activated automatically. Do not assign two control stores to write the same receiver. This arrangement does not create a shared multi-repository transaction or a cross-computer lock.

The same issue found by a local governance turn and by a user report should remain one product change. Fix the shared implementation once, validate it, then record which installations adopted it. A note about a fix and the installed fix are different parts of that work.
