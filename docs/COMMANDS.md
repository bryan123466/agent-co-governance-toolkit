# CLI and MCP contract / 命令与 MCP 合同

All ordinary actions route through one dispatch API. Use JSON files to avoid shell-dependent quoting. 所有普通动作调用同一个分发 API；使用 JSON 文件避免不同终端的引号差异。

```text
python -m agct --project <control-directory> <action> --input <request.json>
```

`--input` and `--json` are mutually exclusive. Input files contain the **argument object only**, not an action wrapper. `status` and `doctor` need no input file. Replace angle-bracket placeholders; do not type them literally. 请求文件只包含参数对象，`status` 与 `doctor` 无需请求文件；尖括号是占位符。

Success: `{"ok":true,"result":{...}}`. Failure: `{"ok":false,"error":{"code":"...","message":"...","details":{...}}}` and a nonzero exit status. A successful planning result is not proof that execution occurred. 计划成功不代表实际执行成功。

| Action / 动作 | Main fields / 主要字段 | Meaning / 含义 |
|---|---|---|
| `init` | `name` | Initialize the control directory / 初始化控制目录 |
| `task` | `task_id`, optional `title`, `workstream`, `state` | Record task; states active, paused, waiting, complete / 记录任务状态 |
| `workspace` | `name`, `path` | Register existing Git workspace / 登记已有 Git 工作区 |
| `checkpoint` | `task_id`, `workspace`, `paths`, `next_step`, optional `decision`, `paused` | Snapshot exact saved work / 保存精确检查点 |
| `restore` | `checkpoint_id`, `destination` | Restore to absent/empty independent destination / 恢复到不存在或空的独立目录 |
| `artifact` | `task_id`, `path`, optional `role`, `backup`, `decision` | Register content identity and available backup evidence / 记录材料身份及备份证据 |
| `submit` | `task_id`, `workspace`, `commit`, `base`, `paths`, optional `stage_id`, `relation`, `supersedes` | Freeze explicit stage; paths must equal commit diff / 冻结明确交付，路径与提交差异须一致 |
| `reconcile` | `baseline`, optional `execute`, `plan_id` | Plan or execute local integration / 计划或执行本地接收 |
| `adopt` | `workspace`, `baseline`, optional `execute`, `plan_id` | Plan or execute workspace adoption / 计划或执行工作区采用 |
| `experience` | `rule_id`, `code`, `operation`, `action`, optional `task_id`, `version`, `enabled` | Store bounded experience / 保存有限经验 |
| `status` | none / 无 | Read current state / 读取当前状态 |
| `agenda` | optional `limit` (1–100), `previous_fingerprint`, `cursor` | Read a bounded, paginated selection; no execution / 读取有限分页议程，不执行操作 |
| `doctor` | none / 无 | Inspect prerequisites / 检查运行条件 |

Paths in a checkpoint or submission are workspace-relative exact files, not wildcard expressions. In a cumulative submission, `relation` is `cumulative` and `supersedes` lists the exact earlier stage identifiers. The default relation is `independent`. 检查点和交付的路径是工作区相对精确文件，不使用通配符；累计交付明确列出被替代阶段。

`reconcile` and `adopt` default to planning. To execute, copy the returned plan identifier into a request with `execute: true`. First reconcile recorded unfinished operations against their actual effects and resume the original operation when applicable. If external changes invalidate the relevant facts and there is no applicable operation to resume, inspect the error and generate a fresh plan. Do not edit the persisted plan. 接收和采用默认只计划；先核对未完操作的实际效果，适用时接续原操作。外部变化使前提失效且无适用原操作可续办时，再检查错误并重新计划，不直接修改保存的计划。

MCP starts with `python -m agct --project <control-directory> mcp`. Tools have `agct_` prefixes and expose the corresponding ordinary actions, except project initialization and setup. The server is project-bound. CLI and MCP output formatting differ where required by their protocols, but both call the same action dispatcher.

MCP 工具名以 `agct_` 开头，提供普通动作，不通过工具初始化或改装项目。服务固定到启动时的项目。协议封装可以不同，实际行为共用同一分发器。

See `python -m agct --help` and MCP `tools/list` for the installed version's exact interface. Fault-injection controls are for explicitly marked synthetic test projects only; they are not a supported production recovery method. 参数以已安装版本帮助和工具列表为准；故障注入只用于明确标记的合成项目。

`setup` is CLI-only: `mode` is `preview`, `install`, or `uninstall`; optional `server_name` selects a distinct MCP service name and is retained for later setup calls. Setup changes project-managed Skills and the generated configuration fragment, not live Codex configuration or business Git branches. A frozen pending install resumes only when its candidate and exact file evidence remain valid. `doctor.runtime` reports the package imported by the current process and managed setup state. See [maintenance and upgrades](en/governance-maintenance.md).

`setup` 仅通过 CLI 配置，支持 `mode` 和可选 `server_name`。安装中断后，在相同候选和精确文件证据仍有效时接续；实际文件有独立修改时保留现场。它不修改已启用的 Codex 配置或业务分支。`doctor.runtime` 区分当前进程导入的版本和项目接入状态，不能替代其他进程的实际加载验证。详见[维护与升级](zh-CN/governance-maintenance.md)。
