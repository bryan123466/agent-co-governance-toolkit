# Contributing / 参与贡献

Start with a small reproducible case in a disposable project. Discuss behavior changes before adding a new command, state store, or recovery mechanism. CLI, MCP, and Skills must retain one shared engine.

1. Use Python 3.11+ and Git. Install locally with `python -m pip install .`.
2. Run `python -m unittest discover -s tests -v`.
3. Add an outcome-based regression test for a real new behavior or failure mode. Prefer checking Git trees, index state, event records, and repeat effects over asserting implementation text.
4. Keep English and Chinese user-facing documentation consistent. Update command examples when argument schemas change.
5. Include a sanitized description, affected boundary, test command, actual result, and limitations in the pull request.

Do not include private source, real customer data, personal information, credentials, absolute host paths, copied proprietary Skills, or machine-specific run receipts. Synthetic fault injection must remain explicitly enabled only for marked synthetic projects. No CI job should mutate an external project or push a user's branch.

The configured CI matrix proposes Windows, Linux, and macOS validation. Passing local checks or authoring a matrix does not prove those hosted jobs have run.

先在独立项目中用最小案例复现，再讨论是否需要新命令、状态存储或恢复机制。CLI、MCP、Skills 必须共用内核。

修改后运行 `python -m unittest discover -s tests -v`。针对实际行为和故障增加验证，核对 Git 内容、暂存状态、事件和重复执行效果，而不是只匹配实现文字。命令与参数改变时同步更新中英文示例。

提交说明应包含脱敏的问题、影响边界、测试命令、实际结果和限制。不得纳入私有源码、真实客户资料、个人信息、凭证、主机绝对路径、无再分发权的 Skill 或实际项目运行回执。故障注入仅能在明确标记的合成项目中启用。
