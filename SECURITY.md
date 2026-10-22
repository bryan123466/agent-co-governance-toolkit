# Security and data boundaries / 安全与数据边界

If you are unfamiliar with the workflow or are connecting a sensitive project, you may first use a separate local clone to become familiar with it. This is an optional precaution, not a required onboarding step. The tool can create snapshots, commits, refs, and managed project files within explicit operations. Review a plan before execution.

## Threat model

- The trusted local user and Git/Python executables are part of the environment. This release is not a hardened service for hostile concurrent users.
- Project separation, exact paths, symlink rejection, and operation locks reduce accidental cross-project writes. They are **not a virtual machine, container, or operating-system security boundary**.
- Skills and project rules guide an agent; they cannot revoke permissions granted to the agent's other tools.
- Checkpoints contain selected file bytes and Git metadata. Do not include secrets, personal records, proprietary files, or other data you cannot safely store locally. Filename filters are defense in depth, not complete secret detection.
- The toolkit performs no remote push or upload. A user's subsequent Codex prompt, Git command, or synchronization software has its own effects.
- The tool does not repair the host OS, modify antivirus settings, bypass native permissions, change the selected model, or install scheduled tasks.

## Reporting

Do not publish credentials, private file contents, entire chat exports, or a real project database in an issue. Use the sanitized [defect template](templates/defect-report.md) and reproduce with fictional data. For a sensitive vulnerability, use the hosting platform's private security-reporting feature if the repository owner enables it; otherwise contact the maintainer privately before sharing technical details. No private reporting address is promised until a real publisher supplies one.

## 中文说明

如果尚不熟悉工作流，或准备接入敏感项目，可以先用独立的本地副本熟悉操作；这是可选的保护措施，不是必做的接入步骤。工具在明确操作范围内可能创建快照、提交、引用和项目文件，执行前应检查计划。

本版假定本地用户和 Python/Git 可执行程序可信，不是面向恶意多租户的加固服务。目录隔离、精确路径、符号链接拒绝和操作锁可以减少误写，**不等于虚拟机、容器或操作系统级安全隔离**。Skill 无法收回 Agent 其他工具已有的权限。

检查点会保留指定文件字节和 Git 元数据。不要纳入密钥、个人信息或无法妥善存储的资料；文件名过滤不能代替完整敏感信息检查。工具不推送或上传，不修复宿主系统、不更改杀毒配置、不绕过原生权限、不切换模型、不安装定时任务。

反馈时使用虚构资料复现，不公开实际项目数据库或完整聊天。敏感漏洞优先使用仓库启用的私密安全反馈渠道；尚未启用时先私下联系实际维护者。本候选版不虚构维护者联系方式。
