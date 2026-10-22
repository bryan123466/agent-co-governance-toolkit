# Agent Co-Governance Toolkit

**把治理接入你的实际 Codex 项目：保留任务进度、接收稳定成果，并更新独立工作区。**

[下载 v0.2.0rc1](https://github.com/bryan123466/agent-co-governance-toolkit/releases/tag/v0.2.0rc1) · [Windows 完整操作手册](docs/zh-CN/windows-example.md) · [English](README.md)

版本 **0.2.0rc1**。面向已经使用 Codex 和 Git 的用户。模型理解任务证据，CLI/MCP 共用的内核记录状态、检查条件并执行已实现的 Git 操作。

## 从这里开始

1. **下载并准备目录。** 获取 [v0.2.0rc1 产品包](https://github.com/bryan123466/agent-co-governance-toolkit/releases/tag/v0.2.0rc1)，建立 `CoGov`、`CoGov/control` 和 `CoGov/toolkit`，把产品内容直接解压到 `toolkit`。[Windows 手册](docs/zh-CN/windows-example.md#choose)提供完整步骤。
2. **接入你的项目。** 在 `control` 新建治理聊天，填写**【项目名称】**和**【一句话介绍】**，发送[安装提示词](docs/zh-CN/windows-example.md#install)。治理根据现场判断首次建立基线还是接续原工作；空的 CoGov 不代表没有旧成果，信息不足时先核对。
3. **接入工作窗口并继续。** 按手册完成[专业窗口接入](docs/zh-CN/windows-example.md#agents)、[MCP 配置](docs/zh-CN/windows-example.md#mcp)和[首次当前状态盘点](docs/zh-CN/windows-example.md#delivery)。治理接收明确交付的稳定成果，未完成工作保留为状态；CLI 仍可通过同一内核和治理目录使用。

**一套 CoGov 目录对应一个现实项目。** 初次初始化前可以选择其他根目录，并统一调整路径；不能靠改目录名或搬动已绑定项目来完成迁移。

需要新专业窗口时，填写**【n：新专业窗口数量】**和**【请填入该对话窗需要实际负责的项目内容】**，由治理新增 n 个独立工作区并接续已有编号。窗口按并行职责划分，顺序子任务可以留在同一窗口，无须预设团队或先做演示业务。

[已有窗口可以继续工作](docs/zh-CN/windows-example.md#existing)：把手册提示词贴给原窗口 → 将其回复与手册的转交提示词一起交给治理 → 登记后取得回贴提示词 → 贴回原窗口，保留任务、历史与未完成工作（WIP）。多个旧窗口共用一个目录时，保留一个主要写入者，其余并行职责在保全历史与各自 WIP 后用独立工作区接续。

可选的[定时治理](docs/zh-CN/windows-example.md#automation)读取实际已登记的工作区与任务，不固定专业窗口数量。

## 日常闭环

`工作 → 按需检查点 → 稳定阶段交付 → 计划与接收 → 按需采用 → 接续工作`

- **检查点：**保留选定的已保存文件、决定与下一步，不代表交付。
- **稳定阶段：**明确提出一份冻结的 Git 变化，专业工作区后续编辑不改变这份交付。
- **接收基线：**核对实际集成效果，业务验收仍单独判断。
- **工作区采用：**在目标可更新时采用新基线，保全支持范围内的本地工作，报告具体冲突。
- **条件恢复：**使用适用且已经实现的恢复动作，先核对效果再续缺步；写下一段经验不会自动新增执行能力。

没有变化的暂停任务保留接续位置，不反复成为积压。累计替代需要明确的祖先与范围证据，时间更晚本身不构成覆盖证明。

## 环境与范围

需要 Python **3.11+**、供正常检查点/接收流程使用的 Git，以及用于模型协作的现有 Codex。工具运行时使用 Python 标准库，不自行调用模型 API。

本版每个项目使用一个本地控制库和一条接收基线，同一台电脑可有多个任务工作区。每个任务/工作区保持一个主要写入者，工作区更新时避免其他程序同时写入。工具不会扫描应用内全部聊天、把所有暂停任务推定为空闲、内建自己的调度器或修复操作系统。

MCP 配置片段必须在宿主中真正配置并成功调用，才算接通。定时治理通过宿主正式自动化工具配置，与工具安装分开。远端推送和跨电脑状态迁移不是内建操作；可选多电脑方案采用任务分支与一个集成主机。

## 文档

- [Windows 完整流程与可复制提示词](docs/zh-CN/windows-example.md)
- [快速了解入口](docs/zh-CN/getting-started.md)
- [工作流总览与可选配置](docs/zh-CN/operation-manual.md)
- [私有 Git、备份与多电脑任务分支](docs/zh-CN/remote-and-multicomputer.md)
- [架构](docs/zh-CN/architecture.md) · [命令参考](docs/COMMANDS.md)
- [运行范围](docs/RELEASE_BOUNDARIES.md) · [安全说明](SECURITY.md)
- [离线中英双语流程图](docs/index.html)

## 语言与许可

**正式维护英文与简体中文。** 主要操作手册提供对应语言切换链接。其他语种可以通过社区翻译扩展至 `docs/<language>/`；命令、支持范围与安全要求须与正式维护版本保持一致。新增翻译经审阅并明确纳入维护前，不代表该语言已获得正式支持。

[MIT 许可](LICENSE)适用于独立新写的公开文件，适用范围见 [LICENSE_SCOPE.md](LICENSE_SCOPE.md)。
