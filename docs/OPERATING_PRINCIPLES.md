# Operating principles and implementation boundaries / 操作原则与实现边界

These reusable principles guide the operation manual. They are independently written public guidance. A procedure or prompt does not add an engine feature.

以下通用原则进入操作手册；均为独立整理的公开说明。提示词与操作流程不会自动增加内核功能。

| Principle / 原则 | Current implementation / 当前实现 | Remaining boundary / 尚未实现 |
|---|---|---|
| Preserve original facts; record successors / 保留原事实，单列后继 | Explicit stage lineage, history, operation records / 明确阶段关系、历史与操作记录 | No general legacy authorization or external receipt migration / 无通用历史授权或外部回执迁移 |
| Consult existing evidence before asking again / 先核对已有证据再询问 | Task/checkpoint/stage/artifact records available to AI; artifact hashes / AI可读任务与交付记录，工具核对材料哈希 | No automatic semantic task-assignment controller / 无自动语义归属控制器 |
| Resume actual missing effects / 只续实际缺步 | Named effect-present/receipt-missing recovery; plan checks / 具名效果已发生而回执缺失的恢复、计划检查 | No arbitrary self-repair; a stored refresh_plan rule is not an implemented automatic recovery consumer / 不承诺任意自修复；登记refresh_plan不代表已有自动执行入口 |
| Version change is not automatic historical failure / 版本变化不抹除历史 | Historical records retained; current plan conditions checked / 保留历史、核对当前计划条件 | No cross-version pending-operation migration or semantic compatibility proof / 无跨版本未完事务迁移及语义兼容证明 |
| Keep routine work bounded / 控制每轮处理范围 | Explicit queued stages and targeted workspaces / 明确阶段与目标工作区 | No max-items, batch wall-clock budget, or durable fair cursor / 无条数上限、整批时长预算、持久公平游标 |
| Separate installation, adoption, and host activation / 安装、采用、原生启用分别核实 | Setup results, adoption operations, explicit MCP verification / setup结果、采用操作、MCP实际调用核对 | No claim that generated config is active; no native scheduler test from a shell simulation / 配置生成不等于启用，脚本模拟不等于原生调度验收 |
| External dependency failure is not project failure / 外部依赖故障不改写项目事实 | doctor and preserved state / 运行条件检查与状态保留 | No operating-system repair or universal dependency watcher / 无操作系统维修及通用依赖监控器 |

For high-volume unattended use, finite batching and explicit version migration are the next core engineering priorities. They need implementation and interruption/replay tests before a release can claim them. Multi-computer procedures currently use one integration authority and separate task branches; no shared live SQLite database.

高频无人值守场景下一步优先实现有限批次与显式版本迁移，并验证中断、接续和不重复执行，再声明具备这些能力。当前多电脑流程使用一个集成责任主体与不同任务分支，不共享运行中的SQLite数据库。

[English manual](en/operation-manual.md) · [中文手册](zh-CN/operation-manual.md)
