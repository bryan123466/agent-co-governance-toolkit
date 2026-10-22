"""Small real stdio client for synthetic integration tests, not a Codex mock."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def call(project, tool, arguments):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    proc = subprocess.Popen([sys.executable, "-m", "agct", "--project", str(project), "mcp"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", env=env)
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "synthetic-test-client", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": arguments}},
    ]
    output, error = proc.communicate("".join(json.dumps(m) + "\n" for m in messages), timeout=90)
    if proc.returncode:
        raise RuntimeError(error)
    replies = [json.loads(line) for line in output.splitlines() if line]
    return next(r for r in replies if r.get("id") == 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("tool")
    parser.add_argument("--json", default="{}")
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    arguments = json.loads(args.input.read_text(encoding="utf-8-sig") if args.input else args.json)
    print(json.dumps(call(args.project, args.tool, arguments), ensure_ascii=False))
