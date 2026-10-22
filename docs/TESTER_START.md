# First trial: start with a fictional project

[中文](TESTER_START.zh-CN.md) · [Full guide](en/trial-guide.md) · [Evidence](VALIDATION.md)

Use the source ZIP, matching wheel and SHA256SUMS.txt. The goal is independent installation and a small, understandable workflow, using no real project data.

## Prompt for Codex

> Read README.md, docs/VALIDATION.md and docs/en/trial-guide.md first. Create a dedicated Python environment in the new temporary location I specify; prefer the matching local wheel. Do not use administrator privileges or change another project.
> Use the fictional quality-forms example to register tasks and three workspaces. Save an unfinished-work checkpoint, declare a stable delivery, then declare a cumulative successor with explicit lineage. Receive the current stage into the dedicated baseline. Adopt the baseline while preserving local commits, staged changes, unstaged changes and new files.
> Verify that completed deliveries are not executed again and paused work is not treated as a new backlog. Restore checkpoints only to a new separate directory. After CLI validation, preview the project Skills and MCP configuration fragment. Enable MCP only if this host supports it and I confirm its configuration location; then actually call agct_doctor and agct_status.
> Report CLI, Git, MCP protocol and actual Codex connection separately. On failure, preserve the scene and already completed effects; do not reset, clean or edit the database to force success. Do not run automations, push, deploy or read/upload another project's data. Return concise feedback using templates/defect-report.md.

## Feedback checklist

- Installation and doctor work in an independent environment with the expected version.
- Task pause, stable delivery and technical acceptance are understandable.
- A verified cumulative successor replaces earlier candidates without replay.
- Local commits and each Git/worktree layer remain intact.
- Repeated reception reuses the result and creates no duplicate integration commit.
- Host integration is reported as not enabled, host-start failure, or an actual successful call; a generated TOML fragment alone is not proof.
- Identify the most confusing step, unclear recovery message and unnecessary manual input.

Fault tests create their own disposable repositories. Never enable fault injection on a working project. Submit fictional reproductions and necessary errors, not a complete governance-state directory. CLI-only success is useful but is not host integration acceptance.
