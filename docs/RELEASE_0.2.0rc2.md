# 0.2.0rc2 — Continue the same project as governance evolves

## English

This update helps the governance chat focus on current work and keep its project integration maintainable while professional tasks continue.

- **A current-work agenda.** CLI and MCP offer the same paginated view of unfinished operations, submitted stages and material decisions. It uses one database snapshot, keeps paused work as retained state and distinguishes changed inputs from repeated observations.
- **Installation that can continue after an interruption.** Setup records the chosen candidate and expected file changes before writing. Repeating the same installation can finish its record without rewriting completed files. Detected user edits and changed candidates remain explicit conflicts.
- **Clearer runtime information.** Doctor separates the running process's import metadata, disk source fingerprints and managed project files. It does not claim that another open MCP process has reloaded.
- **Separate tools, progress and business updates.** Updated Skills explain when to read project progress, update the toolkit, or explicitly adopt accepted business changes. They inspect an unfinished operation's actual effects before asking for a new plan.
- **Independent repository connections.** Setup accepts a distinct MCP server name for each control scope. A governance chat can summarize multiple scopes; each still has its own receiving baseline.

The operating manuals remain unchanged. See the [maintenance supplement](en/governance-maintenance.md) for these additions. Keep existing control state when upgrading; install the selected wheel, run setup preview/install, then restart the affected MCP connection. This release provides neither automatic package upgrades nor cross-repository transactions. Maintenance evidence is in [validation](https://github.com/bryan123466/agent-co-governance-toolkit/blob/main/docs/VALIDATION.md) in the source repository; the product ZIP contains tools and user documentation.

## 简体中文

这次更新让治理聊天更容易聚焦当前工作，也让专业任务持续推进时的工具维护更可靠。

- **当前工作清单：**CLI 与 MCP 共用可翻页的议程，从一致的数据库快照读取未完操作、已提交阶段及材料决定；暂停工作保留为状态，不增加交付义务。
- **安装中断后接续：**修改文件前记录选定候选与预期变化；再次执行相同安装时补齐记录，不重写已完成文件。检测到用户修改或候选变化时保留现场并说明冲突。
- **更明确的版本信息：**Doctor 区分当前进程的导入信息、磁盘源码指纹和项目接入文件，不把另一个 MCP 进程仍未重载误报为已更新。
- **分清工具、进度与业务更新：**Skills 说明何时读取进度、更新工具或采用已接收业务成果；存在未完操作时，先核对实际效果再决定是否重新计划。
- **独立仓库分别接入：**每个 control 可以配置不同的 MCP 服务名，由治理聊天汇总多个范围；各自仍保留独立接收基线。

操作手册保持原样，新能力见[维护补充](zh-CN/governance-maintenance.md)。升级时保留已有 control 状态，安装选定 wheel，预览并执行 setup，再重启相关 MCP 连接。本版不提供全自动包升级或跨仓库事务。验证证据留在源码仓库的[验证说明](https://github.com/bryan123466/agent-co-governance-toolkit/blob/main/docs/VALIDATION.md)；产品 ZIP 提供工具与用户文档。

## 繁體中文

這次更新讓治理對話更容易聚焦目前工作，也讓專業任務持續推進時的工具維護更可靠。

- **目前工作清單：**CLI 與 MCP 共用可翻頁的議程，從一致的資料庫快照讀取未完操作、已提交階段及材料決定；暫停工作保留為狀態，不增加交付義務。
- **安裝中斷後接續：**修改檔案前記錄選定候選與預期變更；再次執行相同安裝時補齊記錄，不重寫已完成檔案。偵測到使用者修改或候選變更時保留現場並說明衝突。
- **更明確的版本資訊：**Doctor 區分目前進程的匯入資訊、磁碟原始碼指紋與專案接入檔案，不將另一個 MCP 進程尚未重新載入誤報為已更新。
- **分清工具、進度與業務更新：**Skills 說明何時讀取進度、更新工具或採用已接收業務成果；存在未完操作時，先核對實際效果再決定是否重新計畫。
- **獨立儲存庫分別接入：**每個 control 可設定不同的 MCP 服務名稱，由治理對話彙整多個範圍；各自仍保留獨立接收基線。

操作手冊保持原樣，新能力見[維護補充](zh-TW/governance-maintenance.md)。升級時保留既有 control 狀態，安裝選定 wheel，預覽並執行 setup，再重新啟動相關 MCP 連線。本版不提供全自動套件升級或跨儲存庫交易。驗證證據留在原始碼倉庫的[驗證說明](https://github.com/bryan123466/agent-co-governance-toolkit/blob/main/docs/VALIDATION.md)；產品 ZIP 提供工具與使用者文件。
