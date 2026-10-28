# TaskCarry 0.2.0rc5

## English

This release makes long-running project governance more dependable without adding another service or model. The host AI reviews work and evidence; the same local engine serves CLI, MCP and Skills.

- Current-work queries use a rebuildable index and load relevant history only. Finished history remains available. Older stores stay readable and can opt into the index with `upgrade`.
- Task changes and final receiving/adoption receipts save their related database state and events together. An interrupted receipt can resume from verified Git effects without duplicating the integration.
- Reviewed source references and task/material relationships can be retained with revision checks. A named run preserves its selected scope and reports missing receipts separately from later work.
- Defects can be linked to a tested fix version and checked against actual project setup evidence. Changed conditions reopen review; recording a fix does not install it or prove host reload.
- New operation protocol tags protect continuation across toolkit versions while supporting earlier untagged records.

The English, Simplified Chinese and Traditional Chinese manuals clarify when a task actually needs to adopt business changes. A new [design evolution report](en/governance-evolution.md) explains the smaller workflow and structural synthetic checks.

Local governance needs no remote repository. This release does not add remote push, automatic package upgrades, broad source scanning or verified physical multi-computer takeover. Host-native activation and schedules require their own environment checks.

Download `taskcarry-0.2.0rc5-product.zip` and follow [Start here](../START_HERE.md). Existing users keep their project records, install the new wheel, preview and update their project-managed setup, then reconnect their host. Use `upgrade` only when the current-work storage reports it is needed. See [version-specific validation](https://github.com/bryan123466/taskcarry/blob/v0.2.0rc5/docs/VALIDATION.md).

## 简体中文

本版补齐长期项目治理的持久依据和执行闭环，不增加常驻服务或模型。宿主 AI 理解工作与证据，CLI、MCP、Skills 继续共用同一内核。

- 当前事项采用可重建索引，只取相关历史，保留全部原记录；旧状态库仍可读取，需要时显式 `upgrade`。
- 任务变化、接收和工作区采用的最终状态与事件一并保存。中断后先核对已有 Git 效果，再补回执，避免重复合并。
- 已核对的来源和材料关系可持久保存并校验修订号；具名轮次只核对其冻结范围，不把项目整体误报完成。
- 具体问题可关联修正版本与验证依据，再核对实际项目安装。条件改变需重新复核，登记修正不等于已经安装或宿主已重新加载。
- 新增操作协议标识，兼容旧记录，对未知协议保留现场。

三语手册明确：读取共享进度无需合并业务分支，实际任务需要时才采用成果。新增[治理演进报告](zh-CN/governance-evolution.md)，用通用结构与合成验证说明如何减少重复工作。本地使用不要求远端仓库；目录扫描、自动升级和实体多电脑接管未在本次引入。

新项目下载本版产品包，按原操作手册安装即可。旧项目保留记录，安装新 wheel、预览并更新项目接入文件，再重新连接宿主；仅在存储提示需要时执行索引 `upgrade`。

## 繁體中文

本版補齊長期專案治理的持久依據與執行閉環，不增加常駐服務或模型。宿主 AI 理解工作與證據，CLI、MCP、Skills 繼續共用同一核心。

- 目前事項使用可重建索引，只讀取相關歷史並保留原記錄；舊狀態庫仍可讀取，需要時明確執行 `upgrade`。
- 任務變更、接收及工作區採用的最終狀態與事件一起保存。中斷後核對既有 Git 效果再補回執，避免重複合併。
- 已核對的來源及材料關係可持久保存並檢查修訂號；具名輪次只核對其固定範圍，不將整個專案誤報完成。
- 具體問題可關聯修正版本與驗證依據，再核對實際專案安裝。條件變更須重新複核；登記修正不代表已安裝或宿主已重新載入。
- 新增操作協定標識，支援舊記錄，遇到未知協定時保留現場。

三語手冊說明讀取共同進度無須合併業務分支，實際任務需要時才採用成果。新增[治理演進報告](zh-TW/governance-evolution.md)，以通用結構與合成驗證說明如何減少重複工作。本機使用不需要遠端儲存庫；目錄掃描、自動升級及實體多電腦接管未於本次引入。

新專案下載本版產品套件，依原操作手冊安裝即可。舊專案保留記錄，安裝新 wheel、預覽並更新專案接入檔案，再重新連接宿主；僅在儲存狀態提示需要時執行索引 `upgrade`。
