# Agent Co-Governance Toolkit

**中文从这里开始：[Windows 完整操作流程](docs/zh-CN/windows-example.md)**

为你自己的现实项目建立一套治理，不需要先做演示业务或测试任务。

1. 先建 `CoGov`、`CoGov/control`、`CoGov/toolkit` 三个目录，把包内内容直接解压到 `toolkit`。
2. 在 `control` 新建治理聊天，填写**【项目名称】**和**【一句话介绍】**，使用主手册的安装提示词。
3. 由治理据实际现场判断首次建立基线或接续原工作；不需要选择新/旧路线。空目录不代表没有已有成果。需要新专业窗口时填写**【n：新专业窗口数量】**，每个窗口填写**【实际负责的项目内容】**。
4. 接入治理 MCP，CLI 作后备；完成首次完整状态盘点，再按需要启用宿主定时治理。

一套 CoGov 对应一个项目。只在首次初始化前统一选择或替换根目录，不直接搬动已有绑定。完整流程已提供治理、专业接续和自动化的提示词；需填字段已加粗，登录、远端和业务决定使用真实信息。

旧窗口接入：把提示词贴到旧窗口，将它的回复与手册转交提示词一起交给治理，再把治理生成的接续提示词贴回原窗口。保留原任务和历史，不从全应用自动扫描聊天。

[总览与选项](docs/zh-CN/operation-manual.md) · [快速了解](docs/zh-CN/getting-started.md) · [私有 Git 与多电脑](docs/zh-CN/remote-and-multicomputer.md)

---

**Start here in English: [Complete Windows workflow](docs/en/windows-example.md)**

Use your real project; no demonstration business or maintenance test exercise is required.

1. Create `CoGov`, `CoGov/control` and `CoGov/toolkit`. Extract the package directly into `toolkit`.
2. Open a new governance chat in `control`, supply **[Project name]** and **[One-sentence introduction]**, and use the main walkthrough's installation prompt.
3. Governance uses the actual context to establish the first baseline or continue previous work; there is no new/existing route to choose. An empty directory does not prove there are no previous outputs. For new specialists, fill in **[n: number of new specialist chats]** and **[Actual work assigned to each chat]**.
4. Connect governance through MCP with CLI fallback, establish a complete current-state inventory, then configure host scheduling if useful.

One CoGov directory belongs to one project. Choose or consistently replace the root only before first initialization; do not move an already bound project as a migration shortcut. The walkthrough supplies governance, specialist and scheduling prompts; input fields are bold. Account, remote and business details must be real.

For an existing chat, paste its onboarding prompt there, send the reply together with the manual's handoff prompt to governance, then paste governance's continuation prompt back into the original chat. Keep the task and history; this does not scan every app chat.

[Overview and options](docs/en/operation-manual.md) · [Quick orientation](docs/en/getting-started.md) · [Private Git and multiple computers](docs/en/remote-and-multicomputer.md)
