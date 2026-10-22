# Agent Co-Governance Toolkit development

Build an independent, reusable toolkit. Use synthetic projects for all examples and tests. Keep private project data, real host paths, credentials, and production receipts out of this repository. Do not change user-level Codex configuration or run production scheduled tasks during validation.

Python 3.11+ standard library runtime; Git is an optional runtime prerequisite for Git operations. Public entrypoints share one engine. Preserve user files and Git index/worktree state; explicit plans precede mutations. A checkpoint is not a delivery, and a delivery is not business acceptance. Record actual effects before claiming completion. Tests must exercise observable outcomes and failure recovery.

Development ownership is assigned per task. Do not edit another contributor's files without coordinating. Use project-local temporary directories for synthetic data, or an explicitly assigned external sandbox. Release archives use a positive file allowlist and exclude local runtime state.
