# Security and project data / 安全与项目资料 / 安全與專案資料

## English

TaskCarry works with local task records, selected file snapshots, and Git workspaces. Keep the control directory and its backups as carefully as the project files they describe: they can contain working material, paths, and decisions.

### Using it with your project

Review plans before receiving results or updating a workspace. For a sensitive project, you can first become familiar with the workflow in a separate local copy. The tool may create snapshots, commits, refs, and managed setup files within the operations you choose.

The local user, Python, and Git are trusted parts of the environment. Path checks, link rejection, and operation locks help reduce accidental writes; they do not provide a container, virtual machine, or security boundary against hostile local users. A project Skill guides an AI assistant but cannot remove permissions available through that assistant's other tools.

Selected snapshots may include sensitive file content. Exclude credentials and any material you are not permitted to store there. Filename filters are an additional precaution, not a complete secret scanner. A material reference records a location; an independent backup still requires the file to exist and match.

### AI hosts and external actions

The TaskCarry engine does not upload project data or push to remote Git. Your AI host, prompts, connected tools, and synchronization software have their own data handling and permissions. Review those settings when deciding what the assistant may read or share.

TaskCarry does not change your model, repair the operating system, modify antivirus settings, bypass host approval, or install a schedule. CLI and MCP use one local engine, but connecting an AI host is a separate action. Generated configuration is not proof of a live connection.

### Reporting a problem

Use a small fictional reproduction and the [defect template](templates/defect-report.md). Share the command, expected result, and necessary error text after removing secrets, private contents, personal paths, full chat exports, and real project databases.

For a sensitive vulnerability, use the repository's private security-reporting feature if it is enabled. Otherwise request a private contact route from the maintainer without posting exploit details or sensitive data in a public issue. This document does not promise a channel that has not been enabled.

## 简体中文

TaskCarry 使用本地任务记录、选定文件快照和 Git 工作区。治理目录与备份可能包含工作材料、文件位置和决定，应像项目文件一样妥善保管。

### 在项目中使用

接收成果或更新工作区之前，先检查计划。准备接入敏感项目时，可以先在独立本地副本中熟悉流程。工具会在你选择的操作范围内创建快照、提交、引用和安装文件。

本地用户、Python 和 Git 是可信环境的一部分。路径检查、链接拒绝和操作锁有助于减少误写，但不构成容器、虚拟机或对抗恶意本地用户的安全边界。项目技能指导 AI 助手的行为，不能撤销它通过其他工具获得的权限。

选定快照可能保存敏感正文。不要纳入凭据或无权保存在这里的材料；文件名过滤只是补充保护，不能替代完整的敏感信息检查。材料引用记录位置，独立备份仍需要文件实际存在且内容匹配。

### AI 宿主与外部操作

TaskCarry 内核不会上传项目资料或推送远端 Git。你使用的 AI 宿主、提示词、已连接工具和同步软件各自有数据处理方式与权限，决定助手可以读取或分享什么时，应一并检查这些设置。

TaskCarry 不切换模型、不修复操作系统、不修改杀毒设置、不绕过宿主审批，也不安装定时任务。CLI 与 MCP 共用本地内核，但连接 AI 宿主需要单独完成；生成配置文件不等于连接已生效。

### 反馈问题

使用小范围虚构案例和[问题模板](templates/defect-report.md)，说明命令、预期与必要错误。分享前移除秘密信息、私有正文、个人路径、完整聊天和实际项目数据库。

敏感漏洞应使用仓库已启用的私密安全反馈功能。如果尚未启用，可先向维护者询问私密联系渠道，不要在公开 Issue 中发布利用细节或敏感资料。本文不承诺尚未启用的渠道。

## 繁體中文

TaskCarry 使用本機任務記錄、選定檔案快照與 Git 工作區。治理目錄與備份可能包含工作素材、檔案位置與決定，應像專案檔案一樣妥善保管。

### 在專案中使用

接收成果或更新工作區之前，先檢查計畫。準備接入敏感專案時，可以先在獨立本機副本中熟悉流程。工具會在你選擇的操作範圍內建立快照、提交、參照與安裝檔案。

本機使用者、Python 與 Git 是可信環境的一部分。路徑檢查、連結拒絕與操作鎖有助於減少誤寫，但不構成容器、虛擬機或對抗惡意本機使用者的安全邊界。專案技能指引 AI 助手的行為，不能撤銷它透過其他工具取得的權限。

選定快照可能儲存敏感正文。不要納入憑證或無權儲存在這裡的素材；檔名過濾只是補充保護，不能取代完整的敏感資訊檢查。素材參照記錄位置，獨立備份仍需要檔案實際存在且內容相符。

### AI 宿主與外部操作

TaskCarry 核心不會上傳專案資料或推送遠端 Git。你使用的 AI 宿主、提示詞、已連接工具與同步軟體各自有資料處理方式與權限，決定助手可以讀取或分享什麼時，應一併檢查這些設定。

TaskCarry 不切換模型、不修復作業系統、不修改防毒設定、不繞過宿主審批，也不安裝排程任務。CLI 與 MCP 共用本機核心，但連接 AI 宿主需要個別完成；產生設定檔不等於連線已生效。

### 回報問題

使用小範圍虛構案例與[問題範本](templates/defect-report.md)，說明指令、預期與必要錯誤。分享前移除機密資訊、私有正文、個人路徑、完整對話與實際專案資料庫。

敏感漏洞應使用儲存庫已啟用的私密安全回報功能。如果尚未啟用，可先向維護者詢問私密聯絡管道，不要在公開 Issue 中發布利用細節或敏感資料。本文不承諾尚未啟用的管道。
