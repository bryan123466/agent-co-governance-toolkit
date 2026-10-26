---
name: agct-project-setup
description: Connect an existing project to Agent Co-Governance Toolkit, inspect prerequisites, or install and remove project-scoped integration files. Use for explicit project onboarding or tool maintenance.
---

# Project setup / 项目接入

Use the existing Codex model with the local AGCT engine. No separate model server is required. Establish the exact project directory from the user's task; never substitute another active repository.

Start with `python -m agct --project <directory> setup --json '{"mode":"preview"}'`. Inspect the proposed files and conflicts. Within the user's requested onboarding scope, install with `mode: install`. This creates four project-local skills and `.agct/codex.mcp.toml`; it does not activate the fragment or edit live Codex configuration. Show the fragment for the user's chosen configuration workflow. Preserve existing `AGENTS.md` and configuration.

Use `init` only when creating this project's governance state, then `doctor` to inspect prerequisites. Git is needed only for Git operations. The fixed project used to launch MCP must match the intended governance project. `agct_workspace` registers explicit workspaces; it is not permission to read all local repositories.

Keep the installed governance runtime separate from its source checkout. When maintaining AGCT itself, use a fixed wheel environment outside the source working directory. Review `doctor.runtime` for the imported package and managed setup; it describes this process, not proof that another already-running MCP process loaded the same version. Do not recreate project state during a tool upgrade. A pending setup intent may be resumed by repeating the same install with the same candidate; do not delete the intent or overwrite a changed user file. Multiple independent control stores may use explicit distinct `server_name` values; each still has one receiving baseline.

For removal, `setup` with `mode: uninstall` removes only unchanged managed files. Modified files, governance data and manually activated configuration are retained and reported. Do not remove these by force.

中文：接入仅影响用户指定项目。预览后按既有授权安装；MCP 片段需明确配置才会生效，不宣称已自动连接。诊断通过不代表原生 Codex 界面已验收；如实报告实际测试到的层次。
