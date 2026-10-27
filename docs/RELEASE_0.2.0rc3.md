# 0.2.0rc3 — Finite receiving work and visible recovery

## English

This candidate strengthens the existing local governance engine. Receiving plans have a configurable work limit, freeze their selected recovery operations, and distinguish completion of that selection from later or unrelated work. Workspace-update preparation failures remain discoverable with their checkpoint and original error. A verified successful successor can supersede an earlier no-effect preparation failure without erasing it.

Experience now distinguishes effect verification from planning advice. A qualifying `refresh_plan` match can return a structured, non-executing planning request. The AI still reviews the current evidence and the new plan. Shared governance and recovery Skills describe these capabilities accurately.

New English, Simplified Chinese and Traditional Chinese [automation guidance](en/automation.md) provides one governance writer, an optional read-only observer, incremental evidence review, concise summaries and meaningful-change notifications. These are host configuration instructions, not an embedded scheduler. The existing nine operating walkthroughs are preserved.

The release continues to use one local control store and receiving baseline. It does not add remote pushing, a general legacy importer, arbitrary self-repair, a full-session hard timeout, automatic chat discovery or multi-host write coordination. Validation of this release is separate from prior releases; see [validation evidence in the source repository](https://github.com/bryan123466/agent-co-governance-toolkit/blob/main/docs/VALIDATION.md).

## 简体中文

本候选加强现有本地治理内核：接收计划可限制本批工作数量，选中的恢复操作纳入冻结身份，明确区分本计划完成与后续、无关工作。工作区采用准备失败会留下可发现的记录、检查点和原错误；经验证成功的后继可取代先前没有应用效果的准备失败，原事实继续保留。

经验明确区分效果核验与计划建议。条件符合的 `refresh_plan` 可以返回结构化、不会执行的计划请求，AI 仍需复核当前证据及新计划。治理与恢复 Skills 同步说明真实能力。

新增中英繁体[自动化说明](zh-CN/automation.md)，提供单一治理写入者、可选只读观察、增量证据复核、简明晨报和有意义变化通知。它是宿主配置指导，不是包内调度器。原九份操作手册保持不变。

继续使用本地单一 control 和接收基线。本版没有增加远端推送、通用历史导入、任意自修复、整段 AI 对话硬时限、自动发现聊天或跨电脑写入协调。当前验证与旧版分别记录，见[源码仓库中的验证证据](https://github.com/bryan123466/agent-co-governance-toolkit/blob/main/docs/VALIDATION.md)。

## 繁體中文

本候選加強既有本機治理核心：接收計畫可限制本批工作數量，選中的恢復操作納入凍結身分，明確區分本計畫完成與後續、無關工作。工作區採用準備失敗會留下可發現的記錄、檢查點與原錯誤；經驗證成功的後繼可取代先前沒有套用效果的準備失敗，原事實繼續保留。

經驗明確區分效果核驗與計畫建議。條件符合的 `refresh_plan` 可以返回結構化、不會執行的計畫請求，AI 仍須複核目前證據及新計畫。治理與恢復 Skills 同步說明實際能力。

新增中英繁體[自動化說明](zh-TW/automation.md)，提供單一治理寫入者、可選唯讀觀察、增量證據複核、簡明晨報與有意義變化通知。它是宿主設定指引，不是套件內排程器。原九份操作手冊保持不變。

繼續使用本機單一 control 和接收基線。本版沒有增加遠端推送、通用歷史匯入、任意自我修復、整段 AI 對話硬時限、自動探索對話或跨電腦寫入協調。目前驗證與舊版分別記錄，見[原始碼儲存庫中的驗證證據](https://github.com/bryan123466/agent-co-governance-toolkit/blob/main/docs/VALIDATION.md)。
