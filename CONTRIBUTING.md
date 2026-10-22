# Contributing / 参与贡献 / 參與貢獻

[English](#en) · [简体中文](#zh-CN) · [繁體中文](#zh-TW)

<a id="en"></a>

## English

**You can use the product without developing it or running its maintenance tests.** Start with the [Windows guide](docs/en/windows-example.md) to connect your own project. If you would like to help improve the toolkit, everyday experience is welcome alongside code contributions.

### Ways to help

- **Share a use case.** Describe what you were trying to do and which part of the workflow helped or felt unclear. Use a fictional or sanitized example.
- **Ask a question or report a problem.** Search [Issues](https://github.com/bryan123466/agent-co-governance-toolkit/issues), then [open an issue](https://github.com/bryan123466/agent-co-governance-toolkit/issues/new/choose) if needed. Include the relevant step, what you expected, and what happened. A question does not require a test project or a code fix.
- **Improve the guides or translations.** Small corrections, clearer examples, and fixes to English, Simplified Chinese, or Traditional Chinese are useful contributions. Point to the page or propose a focused pull request.
- **Contribute code.** Describe the problem first, especially before adding a command, a state store, or a recovery mechanism. This helps keep changes consistent with the rest of the toolkit.

Do not post secrets, private project files, personal information, or full chat exports. The [security guide](SECURITY.md) explains how to share a sanitized report and handle a sensitive vulnerability. Contribute only material you have the right to share; see [LICENSE](LICENSE) and [LICENSE_SCOPE.md](LICENSE_SCOPE.md).

### For code contributors

Use Python 3.11+ and Git in a dedicated development environment. From the source repository root, run:

```text
python -m pip install .
python -m agct --help
python -m unittest discover -s tests -v
```

Keep CLI, MCP, and Skills connected to one shared engine. For a new behavior or a real failure, add a small regression case in a disposable synthetic project. Check observable results such as Git trees, staged changes, event records, and whether retrying repeats an effect. Preserve user work instead of asserting only that implementation text looks right.

Keep the three language editions consistent, and update examples when command arguments change. A documentation-only change needs relevant content and link checks; it does not require exercising real project operations. In a pull request, describe the change, its affected behavior, the exact checks you ran, their results, and anything not checked.

Keep private source, customer data, credentials, real host paths, proprietary Skills without redistribution rights, and real-project run records out of contributions. Fault injection must be explicitly enabled only in marked synthetic projects. CI must not modify external projects or push a user's branch.

The [CI configuration](.github/workflows/ci.yml) defines synthetic checks on Windows, Linux, and macOS with Python 3.11 and 3.12, including an installed-wheel check. Report the actual [Actions result for the relevant commit](https://github.com/bryan123466/agent-co-governance-toolkit/actions); a configured matrix is not evidence that every check passed.

<a id="zh-CN"></a>

## 简体中文

**使用产品不需要参与开发，也不需要运行维护测试。** 按照 [Windows 操作手册](docs/zh-CN/windows-example.md)接入自己的项目即可。如果你愿意帮助改进工具，实际使用中的经验和代码贡献同样欢迎。

### 可以怎样参与

- **分享使用场景。** 说明你想完成什么，哪些步骤有帮助、哪些地方不好理解；使用虚构或已脱敏的例子。
- **提问或反馈问题。** 先查看 [Issues](https://github.com/bryan123466/agent-co-governance-toolkit/issues)，需要时[新建问题](https://github.com/bryan123466/agent-co-governance-toolkit/issues/new/choose)，说明操作步骤、预期和实际结果。普通提问不要求你先搭测试项目或修代码。
- **改善文档与翻译。** 修正错字、补充更清楚的例子，或改善英文、简体中文、繁体中文表达，都可以参与。可以指出对应页面，也可以提交小范围的 Pull Request。
- **贡献代码。** 先说明要解决的具体问题，尤其是在增加命令、状态存储或恢复机制之前，方便与现有工具保持一致。

不要公开密钥、私有项目文件、个人信息或完整聊天记录。[安全说明](SECURITY.md)提供脱敏反馈和敏感漏洞的处理方式。只提交有权分享的内容；许可说明见 [LICENSE](LICENSE) 与 [LICENSE_SCOPE.md](LICENSE_SCOPE.md)。

### 给代码贡献者

准备 Python 3.11+ 与 Git，并使用独立开发环境。在源码仓库根目录运行：

```text
python -m pip install .
python -m agct --help
python -m unittest discover -s tests -v
```

CLI、MCP 和 Skills 继续共用同一个内核。针对新行为或真实故障，在可丢弃的虚构项目中增加小范围回归案例，检查 Git 内容、暂存修改、事件记录和重复执行是否造成重复效果。保护用户工作，不只检查实现文字是否相符。

三语文档保持一致，命令参数改变时同步更新示例。仅修改文档时，检查相关内容和链接即可，不需要操作真实项目。Pull Request 中说明改了什么、影响什么行为、实际运行的检查及结果，以及尚未检查的内容。

贡献内容不得包含私有源码、真实客户资料、凭证、真实主机路径、无再分发权的 Skill 或真实项目运行记录。故障注入只在明确标记的虚构项目中显式启用；CI 不得修改外部项目或推送用户分支。

[CI 配置](.github/workflows/ci.yml)定义 Windows、Linux、macOS 与 Python 3.11、3.12 的虚构项目检查，并包含安装后 wheel 检查。报告验证结果时使用[对应提交的 Actions 实际结果](https://github.com/bryan123466/agent-co-governance-toolkit/actions)，配置了检查不代表所有检查已经通过。

<a id="zh-TW"></a>

## 繁體中文

**使用產品不需要參與開發，也不需要執行維護測試。** 依照 [Windows 操作手冊](docs/zh-TW/windows-example.md)接入自己的專案即可。如果你願意協助改善工具，實際使用經驗與程式碼貢獻都很歡迎。

### 可以如何參與

- **分享使用情境。** 說明你想完成什麼、哪些步驟有幫助、哪些地方不好理解；使用虛構或已去識別化的例子。
- **提問或回報問題。** 先查看 [Issues](https://github.com/bryan123466/agent-co-governance-toolkit/issues)，需要時[建立問題](https://github.com/bryan123466/agent-co-governance-toolkit/issues/new/choose)，說明操作步驟、預期與實際結果。一般提問不要求你先建立測試專案或修正程式碼。
- **改善文件與翻譯。** 修正錯字、補充更清楚的例子，或改善英文、簡體中文、繁體中文表達，都可以參與。可以指出對應頁面，也可以提交小範圍的 Pull Request。
- **貢獻程式碼。** 先說明要解決的具體問題，尤其是在增加指令、狀態儲存或恢復機制之前，方便與現有工具保持一致。

不要公開金鑰、私有專案檔案、個人資訊或完整對話記錄。[安全說明](SECURITY.md)提供去識別化回報與敏感漏洞的處理方式。只提交有權分享的內容；授權說明見 [LICENSE](LICENSE) 與 [LICENSE_SCOPE.md](LICENSE_SCOPE.md)。

### 給程式碼貢獻者

準備 Python 3.11+ 與 Git，並使用獨立開發環境。在原始碼儲存庫根目錄執行：

```text
python -m pip install .
python -m agct --help
python -m unittest discover -s tests -v
```

CLI、MCP 與 Skills 繼續共用同一個核心。針對新行為或真實故障，在可丟棄的虛構專案中增加小範圍回歸案例，檢查 Git 內容、暫存修改、事件記錄與重複執行是否造成重複效果。保護使用者工作，不只檢查實作文字是否相符。

三語文件保持一致，指令參數變更時同步更新範例。只修改文件時，檢查相關內容與連結即可，不需要操作真實專案。Pull Request 中說明改了什麼、影響什麼行為、實際執行的檢查與結果，以及尚未檢查的內容。

貢獻內容不得包含私有原始碼、真實客戶資料、憑證、真實主機路徑、無再散布權的 Skill 或真實專案執行記錄。故障注入只在明確標記的虛構專案中明確啟用；CI 不得修改外部專案或推送使用者分支。

[CI 設定](.github/workflows/ci.yml)定義 Windows、Linux、macOS 與 Python 3.11、3.12 的虛構專案檢查，並包含安裝後的 wheel 檢查。報告驗證結果時使用[對應提交的 Actions 實際結果](https://github.com/bryan123466/agent-co-governance-toolkit/actions)，設定了檢查不代表所有檢查已經通過。
