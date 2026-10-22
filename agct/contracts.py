"""Shared typed public contracts for CLI, API and MCP. No runtime dependencies."""
from copy import deepcopy

def string(description="", **kwargs):
    return {"type": "string", "description": description, **kwargs}


def schema(properties=None, required=()):
    return {"type": "object", "properties": properties or {}, "required": list(required), "additionalProperties": False}


PATHS = {"type": "array", "items": string("Exact workspace-relative file path"), "minItems": 1, "uniqueItems": True}
BOOL = {"type": "boolean"}
SCHEMAS = {
    "status": schema(),
    "doctor": schema(),
    "task": schema({"task_id": string(), "title": string(), "workstream": string(), "state": string(enum=["active", "paused", "waiting", "complete"])}, ["task_id"]),
    "checkpoint": schema({"task_id": string(), "workspace": string(), "paths": PATHS, "next_step": string(), "decision": string(), "paused": BOOL}, ["task_id", "workspace", "paths", "next_step"]),
    "restore": schema({"checkpoint_id": string(), "destination": string("Absent or empty independent destination directory")}, ["checkpoint_id", "destination"]),
    "artifact": schema({"task_id": string(), "path": string(), "role": string(), "backup": string(), "decision": string()}, ["task_id", "path"]),
    "experience": schema({"rule_id": string(), "code": string(), "operation": string(), "action": string(enum=["verify_and_finalize", "refresh_plan"]), "task_id": string(), "version": string(), "enabled": BOOL}, ["rule_id", "code", "operation", "action"]),
    "workspace": schema({"name": string(), "path": string("Existing local Git worktree")}, ["name", "path"]),
    "submit": schema({"task_id": string(), "workspace": string(), "commit": string(), "base": string(), "paths": PATHS, "stage_id": string(), "relation": string(enum=["independent", "cumulative"]), "supersedes": {"type": "array", "items": string(), "uniqueItems": True}}, ["task_id", "workspace", "commit", "base", "paths"]),
    "reconcile": schema({"baseline": string(), "execute": BOOL, "plan_id": string()}, ["baseline"]),
    "adopt": schema({"workspace": string(), "baseline": string(), "execute": BOOL, "plan_id": string()}, ["workspace", "baseline"]),
}
def validate(value, definition, location="arguments"):
    """Validate the deliberately small schema subset used by these public tools."""
    kind = definition.get("type")
    if kind == "object":
        if not isinstance(value, dict):
            raise ValueError(f"{location} must be an object")
        props = definition.get("properties", {})
        extra = set(value) - set(props)
        missing = set(definition.get("required", [])) - set(value)
        if extra:
            raise ValueError(f"{location} has unknown fields: {', '.join(sorted(extra))}")
        if missing:
            raise ValueError(f"{location} lacks required fields: {', '.join(sorted(missing))}")
        for name, item in value.items():
            validate(item, props[name], f"{location}.{name}")
    elif kind == "string" and not isinstance(value, str):
        raise ValueError(f"{location} must be a string")
    elif kind == "boolean" and not isinstance(value, bool):
        raise ValueError(f"{location} must be a boolean")
    elif kind == "array":
        if not isinstance(value, list):
            raise ValueError(f"{location} must be an array")
        if len(value) < definition.get("minItems", 0):
            raise ValueError(f"{location} requires at least one item")
        for index, item in enumerate(value):
            validate(item, definition["items"], f"{location}[{index}]")
        if definition.get("uniqueItems") and len(value) != len(set(value)):
            raise ValueError(f"{location} must contain unique items")
    if "enum" in definition and value not in definition["enum"]:
        raise ValueError(f"{location} is outside the supported values")


def action_schema(action, allow_fault=False):
    if action == "init":
        return schema({"name": string()})
    if action not in SCHEMAS:
        raise ValueError("Unknown action: " + str(action))
    definition = deepcopy(SCHEMAS[action])
    if allow_fault and action in {"reconcile", "adopt"}:
        choices = ["after_candidate", "after_effect"] if action == "reconcile" else ["after_stash", "after_adopt", "after_restore"]
        definition["properties"]["fault"] = string(enum=choices)
    return definition


