# TaskCarry

[简体中文](#zh-CN) · [English](#en) · [繁體中文](#zh-TW)

完整产品介绍：[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

[Download TaskCarry 0.2.0rc4 / 下载产品包 / 下載產品套件](https://github.com/bryan123466/taskcarry/releases/tag/v0.2.0rc4)

Maintenance / 维护 / 維護：[English](docs/en/governance-maintenance.md) · [简体中文](docs/zh-CN/governance-maintenance.md) · [繁體中文](docs/zh-TW/governance-maintenance.md)。Scheduled governance / 定时治理 / 定時治理：[English](docs/en/automation.md) · [简体中文](docs/zh-CN/automation.md) · [繁體中文](docs/zh-TW/automation.md)。

<a id="zh-CN"></a>

**中文从这里开始：[Windows 完整操作流程](docs/zh-CN/windows-example.md)**

让本地 AI 工具中的多个工作窗口围绕同一个项目持续协作：各自推进任务，由治理窗口汇总成果并保存接续位置。本手册提供 Codex 的具体接入步骤；其他宿主通过同一 CLI/MCP 接入，需按该宿主实际能力核验。

1. 先建 `TaskCarry`、`TaskCarry/control`、`TaskCarry/toolkit` 三个目录，把包内内容直接解压到 `toolkit`。
2. 在 `control` 新建治理聊天，填写**【项目名称】**和**【一句话介绍】**，使用主手册的安装提示词。
3. 由治理据实际现场判断首次建立基线或接续原工作；不需要选择新/旧路线。空目录不代表没有已有成果。需要新专业窗口时填写**【n：新专业窗口数量】**，每个窗口填写**【实际负责的项目内容】**。
4. 按手册接通工具，在治理聊天完成一轮有限治理，直接看到安装、连接、已接入工作和本轮结果。没有阶段成果时显示已就绪，等待你分配任务。之后按需要设置定时治理，复用这次结果，不额外补跑一次。

一套 TaskCarry 对应一个项目。只在首次初始化前统一选择或替换根目录，不直接搬动已有绑定。完整流程已提供治理、专业接续和自动化的提示词；需填字段已加粗，登录、远端和业务决定使用真实信息。

旧窗口接入：把提示词贴到旧窗口，将它的回复与手册转交提示词一起交给治理，再把治理生成的接续提示词贴回原窗口。保留原任务和历史，不从全应用自动扫描聊天。

[总览与选项](docs/zh-CN/operation-manual.md) · [快速了解](docs/zh-CN/getting-started.md) · [私有 Git 与多电脑](docs/zh-CN/remote-and-multicomputer.md)

---

<a id="en"></a>

**Start here in English: [Complete Windows workflow](docs/en/windows-example.md)**

Connect the working chats in your local AI tools around one project. Each advances its assigned work, while governance collects results and records where to continue. This manual provides the Codex setup; other hosts use the same CLI/MCP foundation and require their own capability checks.

1. Create `TaskCarry`, `TaskCarry/control` and `TaskCarry/toolkit`. Extract the package directly into `toolkit`.
2. Open a new governance chat in `control`, supply **[Project name]** and **[One-sentence introduction]**, and use the main walkthrough's installation prompt.
3. Governance uses the actual context to establish the first baseline or continue previous work; there is no new/existing route to choose. An empty directory does not prove there are no previous outputs. For new specialists, fill in **[n: number of new specialist chats]** and **[Actual work assigned to each chat]**.
4. Connect the tools and complete one bounded governance pass in the current chat. See the actual installation, connection, registered work and result there. Without deliverables, report readiness for your task assignment. Configure a schedule afterward if useful, reusing this result instead of running another trial pass.

One TaskCarry directory belongs to one project. Choose or consistently replace the root only before first initialization; do not move an already bound project as a migration shortcut. The walkthrough supplies governance, specialist and scheduling prompts; input fields are bold. Account, remote and business details must be real.

For an existing chat, paste its onboarding prompt there, send the reply together with the manual's handoff prompt to governance, then paste governance's continuation prompt back into the original chat. Keep the task and history; this does not scan every app chat.

[Overview and options](docs/en/operation-manual.md) · [Quick orientation](docs/en/getting-started.md) · [Private Git and multiple computers](docs/en/remote-and-multicomputer.md)

---

<a id="zh-TW"></a>

**繁體中文從這裡開始：[Windows 完整操作流程](docs/zh-TW/windows-example.md)**

讓本機 AI 工具中的多個工作視窗圍繞同一個專案持續協作：各自推進任務，由治理視窗彙整成果並儲存接續位置。本手冊提供 Codex 的具體接入步驟；其他宿主透過同一 CLI/MCP 接入，需依該宿主實際能力核驗。

1. 先建立 `TaskCarry`、`TaskCarry/control`、`TaskCarry/toolkit` 三個目錄，將套件內容直接解壓縮到 `toolkit`。
2. 在 `control` 建立治理對話，填寫 **【專案名稱】**與 **【一句話介紹】**，使用主手冊的安裝提示詞。
3. 治理依實際情況判斷首次建立基線或接續原工作，不需要選擇新／舊路線。空目錄不代表沒有既有成果。需要新的專業視窗時，填寫 **【n：新增專業視窗數量】**，每個視窗填寫 **【實際負責的專案內容】**。
4. 依手冊接通工具，在治理對話完成一輪有限治理，直接看到安裝、連線、已接入工作與本輪結果。沒有階段成果時顯示已就緒，等待你分配任務。之後依需要設定定時治理，重用這次結果，不額外補跑一次。

一套 TaskCarry 對應一個專案。只在首次初始化前統一選擇或替換根目錄，不直接搬動已有綁定。完整流程已提供治理、專業接續與自動化的提示詞；需填欄位已加粗，登入、遠端與業務決定使用實際資訊。

既有視窗的接入方式：把提示詞貼到原視窗，將它的回覆與手冊轉交提示詞一起交給治理，再把治理產生的接續提示詞貼回原視窗。保留原任務與歷史，不會自動掃描 App 內全部對話。

[總覽與選項](docs/zh-TW/operation-manual.md) · [快速瞭解](docs/zh-TW/getting-started.md) · [私有 Git 與多電腦](docs/zh-TW/remote-and-multicomputer.md)
