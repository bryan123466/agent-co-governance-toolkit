# Agent Co-Governance Toolkit

[简体中文](#zh-CN) · [English](#en) · [繁體中文](#zh-TW)

完整产品介绍：[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

0.2.0rc3 preserves the existing installation workflow. Maintenance and safe continuation: [English](docs/en/governance-maintenance.md) · [简体中文](docs/zh-CN/governance-maintenance.md) · [繁體中文](docs/zh-TW/governance-maintenance.md)。本版沿用原操作手册，新增维护补充，不需要重建已有项目。原操作手冊繼續適用，更新工具時保留既有專案狀態。

Scheduled governance and optional observation: [English](docs/en/automation.md) · [简体中文](docs/zh-CN/automation.md) · [繁體中文](docs/zh-TW/automation.md)。附可复制的自动化运行说明；安装本身不创建或启用定时任务。附可複製的自動化執行說明；安裝本身不建立或啟用定時任務。

<a id="zh-CN"></a>

**中文从这里开始：[Windows 完整操作流程](docs/zh-CN/windows-example.md)**

让几个 Codex 工作窗口围绕同一个项目持续协作：各自推进任务，由治理窗口整理进度、汇总阶段成果，并把可以继续工作的状态保存下来。直接接入你自己的项目即可。

1. 先建 `CoGov`、`CoGov/control`、`CoGov/toolkit` 三个目录，把包内内容直接解压到 `toolkit`。
2. 在 `control` 新建治理聊天，填写**【项目名称】**和**【一句话介绍】**，使用主手册的安装提示词。
3. 由治理据实际现场判断首次建立基线或接续原工作；不需要选择新/旧路线。空目录不代表没有已有成果。需要新专业窗口时填写**【n：新专业窗口数量】**，每个窗口填写**【实际负责的项目内容】**。
4. 按手册接通治理工具，先整理各项工作目前做到哪里，再按需要设置定时汇总。MCP 用于直接调用工具，CLI 是同一工具的命令行入口。

一套 CoGov 对应一个项目。只在首次初始化前统一选择或替换根目录，不直接搬动已有绑定。完整流程已提供治理、专业接续和自动化的提示词；需填字段已加粗，登录、远端和业务决定使用真实信息。

旧窗口接入：把提示词贴到旧窗口，将它的回复与手册转交提示词一起交给治理，再把治理生成的接续提示词贴回原窗口。保留原任务和历史，不从全应用自动扫描聊天。

[总览与选项](docs/zh-CN/operation-manual.md) · [快速了解](docs/zh-CN/getting-started.md) · [私有 Git 与多电脑](docs/zh-CN/remote-and-multicomputer.md)

---

<a id="en"></a>

**Start here in English: [Complete Windows workflow](docs/en/windows-example.md)**

Connect the Codex chats working on your project. Each chat advances its assigned work, while a governance chat brings progress and completed stages together and records where to continue. Start with your own project.

1. Create `CoGov`, `CoGov/control` and `CoGov/toolkit`. Extract the package directly into `toolkit`.
2. Open a new governance chat in `control`, supply **[Project name]** and **[One-sentence introduction]**, and use the main walkthrough's installation prompt.
3. Governance uses the actual context to establish the first baseline or continue previous work; there is no new/existing route to choose. An empty directory does not prove there are no previous outputs. For new specialists, fill in **[n: number of new specialist chats]** and **[Actual work assigned to each chat]**.
4. Connect the governance tools, establish where each task stands, and set up scheduled summaries if useful. MCP offers direct tool calls; the CLI is a command-line entry to the same tools.

One CoGov directory belongs to one project. Choose or consistently replace the root only before first initialization; do not move an already bound project as a migration shortcut. The walkthrough supplies governance, specialist and scheduling prompts; input fields are bold. Account, remote and business details must be real.

For an existing chat, paste its onboarding prompt there, send the reply together with the manual's handoff prompt to governance, then paste governance's continuation prompt back into the original chat. Keep the task and history; this does not scan every app chat.

[Overview and options](docs/en/operation-manual.md) · [Quick orientation](docs/en/getting-started.md) · [Private Git and multiple computers](docs/en/remote-and-multicomputer.md)

---

<a id="zh-TW"></a>

**繁體中文從這裡開始：[Windows 完整操作流程](docs/zh-TW/windows-example.md)**

讓多個 Codex 工作視窗圍繞同一個專案持續協作：各自推進任務，由治理視窗整理進度、彙整階段成果，並儲存下次可以接續的位置。直接接入你自己的專案即可。

1. 先建立 `CoGov`、`CoGov/control`、`CoGov/toolkit` 三個目錄，將套件內容直接解壓縮到 `toolkit`。
2. 在 `control` 建立治理對話，填寫 **【專案名稱】**與 **【一句話介紹】**，使用主手冊的安裝提示詞。
3. 治理依實際情況判斷首次建立基線或接續原工作，不需要選擇新／舊路線。空目錄不代表沒有既有成果。需要新的專業視窗時，填寫 **【n：新增專業視窗數量】**，每個視窗填寫 **【實際負責的專案內容】**。
4. 依手冊接通治理工具，先整理各項工作目前做到哪裡，再依需要設定定時彙整。MCP 用於直接呼叫工具，CLI 是同一工具的命令列入口。

一套 CoGov 對應一個專案。只在首次初始化前統一選擇或替換根目錄，不直接搬動已有綁定。完整流程已提供治理、專業接續與自動化的提示詞；需填欄位已加粗，登入、遠端與業務決定使用實際資訊。

既有視窗的接入方式：把提示詞貼到原視窗，將它的回覆與手冊轉交提示詞一起交給治理，再把治理產生的接續提示詞貼回原視窗。保留原任務與歷史，不會自動掃描 App 內全部對話。

[總覽與選項](docs/zh-TW/operation-manual.md) · [快速瞭解](docs/zh-TW/getting-started.md) · [私有 Git 與多電腦](docs/zh-TW/remote-and-multicomputer.md)
