"""Bounded synchronous MCP stdio server; no network or arbitrary method dispatch."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from .cli import envelope_error

PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
MAX_LINE_BYTES = 1024 * 1024


from .contracts import SCHEMAS, validate


DESCRIPTIONS = {
    "status": "Read current tasks, deliveries and actionable issues without creating state.",
    "doctor": "Read runtime prerequisites and project support; no installation or repair.",
    "task": "Create or update a task's retained current state. This does not declare a delivery.",
    "checkpoint": "Save exact files and Git work layers for later continuation; not a submission.",
    "restore": "Restore an immutable checkpoint into an empty independent directory, preserving the original.",
    "artifact": "Register content identity, task relationship, optional verified backup and decision.",
    "experience": "Register a conditional recovery rule from the fixed allowed actions; no executable shell.",
    "workspace": "Register an existing local Git workspace for bounded governance operations.",
    "submit": "Explicitly deliver exact frozen commit changes. Cumulative replacement needs lineage evidence.",
    "reconcile": "Plan delivery acceptance, or execute an existing plan with exact baseline conditions. No push.",
    "adopt": "Plan or execute an exact baseline adoption while retaining workspace work. No push.",
}


def tools_list():
    return [{"name": "agct_" + action, "description": DESCRIPTIONS[action], "inputSchema": definition,
             "annotations": {"readOnlyHint": action in {"status", "doctor"}, "openWorldHint": False}}
            for action, definition in SCHEMAS.items()]


def rpc_error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


class Server:
    def __init__(self, project, invoke=None):
        self.project = Path(project).resolve()
        self.initialized = False
        self.invoke = invoke

    def handle(self, request):
        if not isinstance(request, dict):
            return rpc_error(None, -32600, "JSON-RPC batches and non-object messages are unsupported")
        request_id = request.get("id")
        if request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
            return rpc_error(request_id, -32600, "Invalid JSON-RPC request")
        if "id" in request and (isinstance(request_id, bool) or not isinstance(request_id, (str, int))):
            return rpc_error(None, -32600, "Request id must be a string or integer")
        method = request["method"]
        # Notifications never invoke tools or change project state.
        if "id" not in request:
            return None
        params = request.get("params", {})
        if not isinstance(params, dict):
            return rpc_error(request_id, -32602, "params must be an object")
        if method == "initialize":
            version = params.get("protocolVersion")
            if not isinstance(version, str) or not isinstance(params.get("capabilities"), dict) or not isinstance(params.get("clientInfo"), dict):
                return rpc_error(request_id, -32602, "initialize requires protocolVersion, capabilities and clientInfo")
            self.initialized = True
            from . import __version__
            result = {"protocolVersion": version if version in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
                      "capabilities": {"tools": {"listChanged": False}},
                      "serverInfo": {"name": "agent-co-governance-toolkit", "version": __version__},
                      "instructions": "Project root is fixed by server startup. Use exact task and file evidence. Plan before execute. Tool availability is not permission to expand user scope."}
        elif method == "ping":
            result = {}
        elif not self.initialized:
            return rpc_error(request_id, -32002, "Initialize the MCP session first")
        elif method == "tools/list":
            if params.get("cursor"):
                return rpc_error(request_id, -32602, "This server has no paginated tool cursor")
            result = {"tools": tools_list()}
        elif method == "tools/call":
            name = params.get("name")
            if not isinstance(name, str) or name not in {"agct_" + a for a in SCHEMAS}:
                return rpc_error(request_id, -32602, "Unknown tool")
            action = name[len("agct_"):]
            arguments = params.get("arguments", {})
            try:
                validate(arguments, SCHEMAS[action])
            except ValueError as exc:
                return rpc_error(request_id, -32602, str(exc))
            try:
                invoke = self.invoke
                if invoke is None:
                    from .api import invoke
                output = {"ok": True, "result": invoke(self.project, action, arguments)}
                failed = False
            except Exception as exc:
                output, failed = envelope_error(exc), True
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}], "isError": failed}
            if version_supports_structured(self):
                result["structuredContent"] = output
        else:
            return rpc_error(request_id, -32601, "Method not found")
        if method == "initialize":
            self.protocol = result["protocolVersion"]
        return {"jsonrpc": "2.0", "id": request_id, "result": result}


def version_supports_structured(server):
    return getattr(server, "protocol", "") in {"2025-06-18", "2025-11-25"}


def serve(project, stdin=None, stdout=None):
    input_stream = stdin or sys.stdin
    output_stream = stdout or sys.stdout
    server = Server(project)
    while True:
        line = input_stream.readline(MAX_LINE_BYTES + 1)
        if not line:
            return 0
        if len(line.encode("utf-8")) > MAX_LINE_BYTES or (len(line) > MAX_LINE_BYTES and not line.endswith("\n")):
            response = rpc_error(None, -32600, "Message exceeds 1 MiB limit")
            output_stream.write(json.dumps(response) + "\n")
            output_stream.flush()
            return 1
        try:
            response = server.handle(json.loads(line))
        except (json.JSONDecodeError, UnicodeError):
            response = rpc_error(None, -32700, "Invalid JSON")
        except Exception:
            response = rpc_error(None, -32603, "Internal protocol error")
        if response is not None:
            output_stream.write(json.dumps(response, ensure_ascii=False) + "\n")
            output_stream.flush()
