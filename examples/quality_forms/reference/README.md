# Multi-agent quality-form reference / 多 Agent 品质表单参考结果

These fictional files are the accepted result of an actual local multi-agent exercise: separate workers produced a schema, a Python validator, and a local web form. A governance agent used the toolkit's public MCP interface to recover an interrupted receipt, accept cumulative and independent deliveries, and adopt the baseline into the worker workspaces. A later cross-check exposed an extra-field validation difference; an explicit UI increment corrected it and was received through the same public workflow.

The files here were copied from the verified synthetic baseline's committed Git contents using an explicit allowlist. They contain no real organization, customer, person, private source, machine path, run database, or unsubmitted worker note. Internal run evidence is not distributed here.

## Try the reference

From this directory:

```text
python -B -m unittest discover -s tests -v
node tests/test_quality_ui.js
```

Python 3.11+ and Node.js are required for their respective tests. Node is only a dependency for this optional web example's checks; it is not an TaskCarry runtime requirement. The tests use the Python and JavaScript standard runtimes without network services.

Open `web/index.html` in a browser for local form entry, visible validation, and a safe text-rendered JSON preview. The preview does not persist a record or transmit it. `samples/valid.json` and `samples/invalid.json` are collections of labeled cases; the command-line validator accepts a **single record object**, not the collection wrapper.

The JSON Schema uses draft 2020-12 and the `date` format. A schema consumer must explicitly enable format checking to validate real calendar dates. A complete schema-validator library is not bundled or required by TaskCarry itself.

This is a software and governance workflow reference, **not a certified quality system, medical tool, compliance template, or production product**. Recorded status and a Git acceptance do not prove actual investigation, review, or corrective-action effectiveness.

## 中文说明

这些虚构文件来自一次真实的本地多 Agent 演练：工作者分别形成 Schema、Python 验证器与本地网页表单；治理 Agent 通过公共 MCP 接口恢复中断回执、接收累计及独立交付，并把基线采用到工作区。交叉验证发现额外字段的判断差异后，再用一次明确的 UI 增量修正并通过同一公共流程接收。

本目录只按白名单复制已验证合成基线中的 Git 提交内容，不包含真实组织、客户、人员、私有源码、主机路径、运行数据库或工作者未提交便笺；内部演练回执不随这里的文件公开。

在本目录运行上述 Python 与 Node 命令即可检查参考实现。Python 要求 3.11 或以上；Node 仅用于这个可选网页示例的检查，不是 TaskCarry 的运行依赖。直接打开 `web/index.html` 可填写虚构记录、查看校验和文本式 JSON 预览，预览不持久化、不传输资料。

有效/无效样例文件包含多个标注案例；命令行验证器接受的是**单条记录对象**，不是整个案例集合。Schema 使用 2020-12 草案，消费者须启用日期 format 检查；完整 Schema 验证器没有捆绑进产品运行时。

这是软件与治理工作流参考，**不是经过认证的品质体系、医疗工具、合规模板或生产产品**。记录状态或 Git 接收不证明现实调查、复核或纠正措施已经有效。
