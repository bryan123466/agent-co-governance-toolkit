# Operating scope / 运行范围

**Agent Co-Governance Toolkit 0.2.0rc1**

The [operation manual](en/operation-manual.md) documents host scheduling, private Git, and optional multi-computer branch workflows. These are user-configured procedures; they do not add a built-in scheduler, remote push, distributed locks, state migration, or a portable recovery guarantee. See [implemented and procedural boundaries](OPERATING_PRINCIPLES.md).

[操作手册](zh-CN/operation-manual.md)新增宿主自动化、私有Git与多电脑分支协作的配置步骤；这些是用户配置的操作流程，不代表新增内建调度、远端推送、分布式锁或跨机状态迁移。详见[能力与流程边界](OPERATING_PRINCIPLES.md)。

[Get started](en/getting-started.md) · [开始使用](zh-CN/getting-started.md)

## Supported use

Use the toolkit with your own project on one computer. Register a dedicated clean integration baseline and one or more local Git workspaces for task work. CLI and MCP use the same implementation for task state, selected-file checkpoints, explicit delivery, local reconciliation, workspace adoption, and supported conditional recovery.

Keep each governance project tied to one integration baseline. Toolkit locks serialize its own operations; other editors and Git commands must avoid writing the same receiver or adoption workspace during an update. Parallel tasks can continue in their separate workspaces.

Checkpoints capture selected saved files, not unsaved editor buffers or hidden conversation state. Limits are 500 paths, 32 MiB per stored object, and 128 MiB total capture. Larger files can use artifact references. Restoration rebuilds selected layers on a clearly identified synthetic Git baseline; it is not a full repository mirror.

## Outside this version

- Remote push, cloud deployment, and external message delivery.
- Multi-computer concurrent writing, distributed coordination, or cross-machine recovery guarantees.
- Installing host scheduled jobs, reading private chat databases, or changing model permissions.
- Host operating-system repair or arbitrary code execution from experience records.

Project scopes and Skills are not an operating-system sandbox. A technical integration result does not grant business approval. MCP configuration activation is performed through the supported settings in the user's Codex installation.

## 中文

本版可以接入你在**单台电脑**上的项目。登记一条专用、干净的接收基线，并使用一个或多个本地 Git 工作区推进任务。CLI 与 MCP 共用任务状态、指定文件检查点、明确交付、本地接收、工作区采用和已实现的条件恢复能力。

一个治理项目对应一条集成基线。工具锁只串行化工具自身操作；更新期间，其他编辑器和 Git 命令不要同时写入相同接收或采用工作区。并行任务可在各自独立工作区继续。

检查点覆盖指定的已保存文件，不包括未保存的编辑器内容或聊天隐含状态；限制为 500 条路径、单对象 32 MiB、总捕获 128 MiB。大文件可登记材料引用。恢复在明确标识的合成 Git 基线上重建所选文件层，不是仓库全量镜像。

本版不包含远程推送、云部署、对外消息、多电脑并发写入、分布式协调、跨机恢复保证、自动安装宿主定时任务、读取私人聊天数据库、修改模型权限、修复操作系统或执行经验记录携带的任意代码。

项目范围和 Skills 不构成操作系统级沙盒；技术集成不替代业务批准。MCP 连接需要通过用户当前 Codex 支持的设置方式启用。
