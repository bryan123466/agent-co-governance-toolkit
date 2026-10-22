"""The single dispatch surface shared by CLI and MCP."""
from .core import Core
from .integration import Integration
from .store import GovernanceError
from .contracts import action_schema, validate


def invoke(project, action, arguments=None):
    args = {} if arguments is None else arguments
    if not isinstance(args, dict):
        raise GovernanceError("INVALID_ARGUMENT", "Arguments must be a JSON object")
    try:
        validate(args, action_schema(action, allow_fault=True))
    except (ValueError, KeyError) as exc:
        raise GovernanceError("INVALID_ARGUMENT", str(exc)) from exc
    if action == "init":
        return Core.initialize(project, **args)
    core_actions = {"status", "task", "checkpoint", "restore", "artifact", "experience"}
    git_actions = {"workspace", "submit", "reconcile", "adopt", "doctor"}
    if action not in core_actions | git_actions:
        raise GovernanceError("UNKNOWN_ACTION", f"Unknown action: {action}")
    obj = Core(project) if action in core_actions else Integration(project)
    if action == "checkpoint" and isinstance(args.get("workspace"), str):
        registered = obj.store.get("workspaces", args["workspace"])
        if registered:
            args = {**args, "workspace": str(Integration(project)._ws(args["workspace"]))}
    try:
        return getattr(obj, action)(**args)
    except TypeError as exc:
        raise GovernanceError("INVALID_ARGUMENT", str(exc)) from exc
