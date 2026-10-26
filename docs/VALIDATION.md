# Release validation / 发布验证

## Current 0.2.0rc2 validation / 本次更新验证

This maintenance update was verified with disposable synthetic projects and real local Git worktrees on Windows with Python 3.12. The source suite ran **143 cases: 140 passed, 0 failed, 0 errored, 3 skipped**. Two skips concern unavailable native symbolic-link privileges; the third is the separately invoked installed-wheel check. The source run explicitly enabled the standard wheel/sdist build check.

The independent installed-wheel check passed, including four packaged Skills and actual stdio MCP `status`, `agenda` and `doctor` requests. A separate rc1-to-rc2 installed-wheel walkthrough preserved existing tasks, paused work, artifact records, database and checkpoint object bytes, and restored an older checkpoint without reinitializing the project. These are additional execution scopes, not extra unique tests to add to the source count.

本次在隔离的合成项目与真实本地 Git 工作树中验证。完整源码测试 **143 项：140 通过、0 失败、0 错误、3 跳过**；跳过项为两项宿主原生符号链接权限用例，以及单独执行的 wheel 安装用例。标准 wheel/sdist 构建验证已启用。独立安装包验证及 rc1 到 rc2 的原状态接续均通过；这些覆盖与源码测试有重叠，不累计成虚高用例总数。

New coverage includes consistent read snapshots, paginated current-work fingerprints, dependency binding changes, resumable setup, detected user edits, source-read diagnostic errors, cumulative version reception, effect reconciliation, and business HEAD/index/WIP preservation during tool integration updates. The nine operating-manual files remain byte-identical.

The product ZIP excludes this evidence and test results. This source repository retains maintenance evidence in [VALIDATION_RESULTS.json](VALIDATION_RESULTS.json). Native Codex connection activation, real scheduled automation, physical multi-computer execution and a new model-decision experiment were **not** performed. Cross-platform CI must be checked against the specific public commit's Actions run; local success alone is not cross-platform evidence.

新版重点覆盖一致只读快照、分页议程、依赖绑定变化、安装断点接续、已检测用户修改保全、源码读取错误诊断，以及工具更新不改变业务 HEAD/index/WIP。未运行用户真实项目、原生 Codex 自动化或实体双电脑验证。下文保留旧版本历史记录，不能作为新版新做的模型演练或新平台验证。

## Historical 0.2.0rc1 evidence / 旧版历史验证

**Agent Co-Governance Toolkit 0.2.0rc1 — local trial candidate.**

This document reports observed results, not a guarantee of autonomous production recovery. Machine-readable case results are in [VALIDATION_RESULTS.json](VALIDATION_RESULTS.json). First-time testers can use the [trial prompt](TESTER_START.md) or [中文试用提示词](TESTER_START.zh-CN.md).

The complete source test run exercised **78 cases: 75 passed, 0 failed, 0 errored, 3 skipped**. Two skips concern native symbolic-link privileges; the third is the separately invoked installed-wheel test. Package-installation outcomes are recorded separately below and in the JSON evidence rather than rewriting this original source-run result.

完整源码测试实际运行 **78 项：75 项通过、0 失败、0 错误、3 项跳过**。两项因本机无法创建原生符号链接而跳过；另一项是需要构建完成后单独执行的安装包测试。安装验证单独留证，不改写原源码测试结果。

**Supplemental checks passed:** installed wheel (four Skills and real project-bound MCP startup) and standard source wheel/sdist construction (four canonical Skills, no generated source copies). Counting unique cases across these runs gives **79 cases: 77 passed, 2 native-link privilege skips, no failures or errors**. The fictional reference adds 12 Python tests, 19 Node checks, and 13 cross-validator cases; those are reported separately from the toolkit's 79 cases.

**补充安装验证已通过：**实际 wheel 在独立目录安装，四个 Skills 齐全，生成的项目 MCP 命令可以实际启动；无预生成资源副本的标准源码也能构建完整 wheel 与 sdist。合并去重后共 **79 个工具用例：77 通过，2 个原生链接权限用例跳过，0 失败、0 错误**。虚构表单另有 12 个 Python 测试、19 个 Node 检查、13 个跨验证器用例，不混入工具用例计数。

## Scope and method / 范围与方法

The validation host is Windows with Python 3.12. Tests create disposable, fictional projects and real local Git repositories. Runtime libraries are Python standard library only; optional schema validation uses a separate test-only installation. The test workspace provides logical isolation, not an operating-system-enforced sandbox. No production automation, private project, original business directory or global host configuration was modified.

本轮使用虚构的品质管理表单任务，实际运行 Git、CLI、stdio MCP 与多 Agent 协作。使用独立目录、限定工作区与可丢弃仓库隔离测试，不把它描述为虚拟机或强制安全沙盒。没有访问真实业务来源目录，没有让专业线程参加实验。

## What was exercised / 已验证的工作链

| Layer / 层次 | Actual coverage / 实际覆盖 |
|---|---|
| Task memory / 任务状态 | Active and paused tasks; selected HEAD/index/worktree checkpoints; binary files and deletions; independent restoration; unchanged tasks do not create delivery backlog. |
| Stable delivery / 阶段交付 | Exact immutable commit ranges; independent and cumulative stages; transitive ancestry; newer working files do not alter frozen deliveries. |
| Reception / 接收 | Real baseline integration, repeated-call reuse, content conflicts, independent-stage continuation, one-baseline binding and branch identity checks. |
| Interrupted effects / 中断效果 | Inject interruption after Git effect; inspect persisted operation; verify effect and complete receipt without duplicate commit. |
| Experience / 经验 | Match error, action, version and scope; reject outdated or inapplicable rules; use `receipt-recovery-v1` in a real model-guided MCP rehearsal. |
| Workspace adoption / 工作区采用 | Preserve local commits, staged changes, unstaged changes, untracked content and paused checkpoints; resume the original journal; retain exact owned stash. |
| Byte preservation / 字节保全 | Windows autocrlf conversion, distinct index/worktree bytes, net-zero diff with nonzero staged work, and new user content after interruption. |
| Boundaries / 边界 | Wrong argument types, path traversal, metadata and secret-like paths, actual junctions, oversized new/deleted blobs, ignored-file collisions, redirected scratch storage. |
| Interfaces / 接口 | Shared typed API/CLI/MCP contract; real stdio processes; setup preview/install/uninstall and modified-file preservation. |
| Release / 发布物 | Positive file allowlist, private-term/path screening, source manifest, wheel content parity, four packaged Skills and independent installed-wheel startup. |

## Multi-Agent rehearsal / 多 Agent 演练

Three worker roles produced schema/examples, a Python validation service, and a browser form. A separate governance role interpreted current tool evidence and used public MCP tools through a shell bridge to receive and adopt their work.

The schema worker declared two cumulative versions. The receiver selected the current version and retained the old record as history. A deliberately interrupted service reception was recovered using the applicable experience rule, without replaying the already completed Git effect. Three workspaces adopted the baseline while the UI worker's paused, untracked note remained preserved.

The rehearsal exposed a real LF/CRLF preservation defect. The shared implementation was corrected and regression-tested; the governance role then resumed the original operation and verified the original byte hash. It did not delete the original failure evidence or replace the frozen plan.

Cross-module testing also found that the UI validator accepted an extra field rejected by the schema and service. The UI worker added a regression test, fixed its own files and declared a new exact incremental stage based on its adopted HEAD. This avoids re-delivering already adopted files from other workers.

The final rehearsal used **25 public MCP calls**, accepted **4 effective stages**, superseded **1 older candidate**, and completed **6 adoption operations** across three worker workspaces. The baseline contains exactly four integration commits. Final actionable stages, operations and artifacts are all empty; paused WIP remains saved state. The corrected increment passed subsequent reception and adoption. The [completed fictional reference](../examples/quality_forms/reference/README.md) is included for inspection and repeatable checks.

最终 **25 次公共 MCP 调用**完成 **4 个有效阶段接收、1 个旧候选替代、3 个工作区共 6 次采用**；基线恰好增加 4 次集成提交。待处理阶段、操作与材料均为空，暂停工作与原始未提交字节仍然保留。额外字段修复后的 Schema、服务与 UI 在 12 份标注样例及 1 份探测上全部一致。

这是实际模型依据工具证据作出决策、经公共 MCP 协议执行的演练；并非只有预写的成功状态。它仍不等同于原生 Codex 桌面 MCP 连接验收，更不等同于定时 Automation 已运行。

## Defects found and corrected / 本轮发现并修正

1. CLI truthy strings could bypass boolean intent: shared typed validation now rejects them before effects.
2. Cumulative histories and failed latest stages could reintroduce older candidates: current-state projection and receiving selection now preserve lineage without fallback replay.
3. A stage conflict could be reported as complete when a new plan had no queued stages: unresolved conflicts remain explicit.
4. WIP preservation missed staged changes cancelled in the working tree: capture considers index and worktree changes independently.
5. Git newline conversion changed raw WIP bytes: saved expected bytes, exact layer checks and bounded newline correction now protect the tested cases.
6. Adoption could overwrite ignored local files: collisions are refused before effects.
7. Invalid execute requests could prematurely bind a baseline: binding occurs only after a valid executable plan.
8. Redirected scratch paths could escape their intended location: symlink/junction ancestry is checked.
9. Frozen oversized blobs, including deleted original content, now receive bounded checks before delivery records.
10. Packaging is checked against frozen allowlisted bytes; both source installation and trial-wheel installation must include all four Skills.
11. Extracted-archive smoke testing caught omitted CSV fixtures despite a valid manifest. The release allowlist and mandatory fixture checks now include the documented example's actual inputs.

These fixes are in shared code and regression tests. They are not temporary commands applied only to a named synthetic worker. The recovery experience has explicit applicability and an executable bounded action; it does not train model weights or execute arbitrary code stored in memory.

## Evidence limits / 验证限制

- **Native Codex host connection is not accepted as passed.** The local native CLI probe stopped while loading host configuration: `invalid transport in mcp_servers.node_repl`. The AGCT MCP server had not started. No native settings were changed to bypass this. Direct stdio MCP and installed-package tests are separate evidence.
- Two native symbolic-link creation tests may be skipped on this Windows account because it cannot create those links. Actual Windows junction tests and portable rejection tests run separately. See individual outcomes in the JSON report.
- The three-platform CI matrix is configured but was not run on hosted Linux/macOS in this local validation. Do not infer cross-platform certification from configuration alone.
- HTML documentation and the fictional UI received structural/static checks. Local-file browser rendering was not accepted by the available browser tool, so no browser screenshot or full interactive UI acceptance is claimed.
- No remote push, distributed locking, multi-computer failover, production scheduled automation or OS repair was tested or promised in this RC.
- Toolkit locks serialize toolkit operations. Other programs must not concurrently mutate the same receiving/adoption workspace; the tool does not physically lock out unrelated editors or Git clients.

## Release decision / 发布判断

Suitable for an **isolated first trial** using generated material. The next external check is a volunteer's clean local installation and actual Codex tool discovery/call, followed by small fictional workflows. It is not yet a production release or a claim that every native host works.

可向愿意测试的人提供候选包，先验证独立安装、宿主 MCP 接入、任务保存、版本接收与恢复。宿主接入的未验证项有明确边界，不需要修改正在使用的生产治理或专业工作台来完成首轮测试。
