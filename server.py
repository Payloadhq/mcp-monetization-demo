#!/usr/bin/env python3
"""
Payload MCP Monetization Demo
=============================

A small, runnable MCP server that demonstrates the *core mechanic* of the
paid MCP Monetization Kit: per-tool-call metering with a free quota, then a
machine-readable PAYMENT REQUIRED response once the quota is exhausted.

This is a teaching demo on purpose. It proves the monetization model works,
but it is NOT the paid product: the metering here is in-memory (no persistent
ledger), payment is not actually collected (no x402 flow, no USDC verifier),
and there is a hard call cap so the demo cannot replace the real kit.

Tools
-----
* word_count       (FREE, unlimited)  — count words / characters / lines.
* summarize        (PREMIUM)          — naive extractive summary of text.
* extract_keywords (PREMIUM)          — naive keyword extraction from text.

Metering
--------
* FREE_QUOTA (env PAYLOAD_FREE_QUOTA, default 5): number of premium tool
  calls allowed before the server starts answering with PAYMENT REQUIRED.
* HARD_CAP (env PAYLOAD_HARD_CAP, default 200): total calls (free + premium)
  before every call is rejected. This demo is not a free ride.

Run it
------
    python3 server.py
    # then speak MCP over stdio (initialize -> notifications/initialized ->
    # tools/list -> tools/call). Or run the guided demo:
    python3 demo.py

Requires only the Python 3 standard library (3.8+). No pip install.
"""

import json
import os
import re
import sys
from collections import Counter

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "payload-mcp-monetization-demo"
SERVER_VERSION = "1.0.0"

UPGRADE_URL = "https://payloadtools.gumroad.com/l/mcp-monetization-kit"
READINESS_URL = "https://payloadtools.gumroad.com/l/mcp-launch-readiness-audit"

FREE_QUOTA = int(os.environ.get("PAYLOAD_FREE_QUOTA", "5"))
HARD_CAP = int(os.environ.get("PAYLOAD_HARD_CAP", "200"))

# In-memory meter. A real deployment needs the paid kit's persistent,
# append-only usage ledger (this demo resets on every restart — see README).
premium_calls_used = 0
total_calls = 0


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def err_response(req_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": code, "message": message},
    }


def tool_result(req_id, text, meta=None):
    payload = {"content": [{"type": "text", "text": text}], "isError": False}
    if meta:
        payload["_meta"] = meta
    return {"jsonrpc": "2.0", "id": req_id, "result": payload}


def tool_error(req_id, text, meta=None):
    payload = {"content": [{"type": "text", "text": text}], "isError": True}
    if meta:
        payload["_meta"] = meta
    return {"jsonrpc": "2.0", "id": req_id, "result": payload}


def payment_required_payload(tool_name):
    """The monetization mechanic: a machine-readable refusal, not a crash."""
    detail = {
        "status": "PAYMENT_REQUIRED",
        "tool": tool_name,
        "free_quota": FREE_QUOTA,
        "premium_calls_used": premium_calls_used,
        "message": (
            "Free quota exhausted (%d/%d premium calls used). "
            "Attach payment to continue, or get the full MCP Monetization "
            "Kit to collect real per-call USDC payments with the x402 flow: %s"
        )
        % (premium_calls_used, FREE_QUOTA, UPGRADE_URL),
    }
    return detail


TOOLS = [
    {
        "name": "word_count",
        "description": "Count words, characters, and lines in text. Free and unlimited in this demo.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "Text to analyze"}},
            "required": ["text"],
        },
    },
    {
        "name": "summarize",
        "description": "Return a short extractive summary of text. PREMIUM: consumes 1 free-quota call.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to summarize"},
                "sentences": {"type": "integer", "description": "Max sentences (default 3)"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "extract_keywords",
        "description": "Return the most frequent significant words in text. PREMIUM: consumes 1 free-quota call.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"},
                "limit": {"type": "integer", "description": "Max keywords (default 10)"},
            },
            "required": ["text"],
        },
    },
]

PREMIUM_TOOLS = {"summarize", "extract_keywords"}


def do_word_count(text):
    return (
        "words: %d\ncharacters: %d\nlines: %d"
        % (len(text.split()), len(text), text.count("\n") + (1 if text else 0))
    )


def do_summarize(text, sentences=3):
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    return " ".join(parts[: max(1, sentences)]) or "(empty input)"


STOPWORDS = set(
    "a an the and or but of to in on for with is are was were be been it its "
    "this that these those as at by from we you they he she his her our your "
    "their not no do does did can will would should could have has had".split()
)


def do_keywords(text, limit=10):
    words = [w.lower() for w in re.findall(r"[a-zA-Z]{3,}", text)]
    counts = Counter(w for w in words if w not in STOPWORDS)
    top = counts.most_common(max(1, limit))
    return "\n".join("%s (%d)" % (w, c) for w, c in top) or "(no keywords found)"


def handle_call(req):
    global premium_calls_used, total_calls
    req_id = req.get("id")
    params = req.get("params") or {}
    name = params.get("name")
    args = params.get("arguments") or {}

    tool = next((t for t in TOOLS if t["name"] == name), None)
    if tool is None:
        return err_response(req_id, -32602, "Unknown tool: %r" % name)

    # Hard cap: the demo cannot be used as a free service.
    if total_calls >= HARD_CAP:
        return tool_error(
            req_id,
            "HARD CAP REACHED (%d total calls). This demo is capped on purpose. "
            "The full kit has no artificial cap — you set your own prices and quotas: %s"
            % (HARD_CAP, UPGRADE_URL),
        )
    total_calls += 1

    if name in PREMIUM_TOOLS:
        if premium_calls_used >= FREE_QUOTA:
            return tool_error(
                req_id,
                json.dumps(payment_required_payload(name), indent=2),
            )
        premium_calls_used += 1
        remaining = FREE_QUOTA - premium_calls_used
        meter_note = "\n\n[metered: %d/%d free premium calls used, %d remaining]" % (
            premium_calls_used,
            FREE_QUOTA,
            remaining,
        )
    else:
        meter_note = "\n\n[free tool: no quota consumed]"

    try:
        if name == "word_count":
            out = do_word_count(str(args.get("text", "")))
        elif name == "summarize":
            out = do_summarize(str(args.get("text", "")), int(args.get("sentences", 3)))
        elif name == "extract_keywords":
            out = do_keywords(str(args.get("text", "")), int(args.get("limit", 10)))
        return tool_result(req_id, out + meter_note)
    except Exception as exc:  # keep the demo alive on bad input
        return err_response(req_id, -32603, "Tool failed: %s" % exc)


def handle(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        return handle_call(req)
    if method and method.startswith("notifications/"):
        return None  # notifications get no response
    return err_response(req_id, -32601, "Method not found: %s" % method)


def main():
    sys.stderr.write(
        "[%s] running on stdio. FREE_QUOTA=%d HARD_CAP=%d. See demo.py for a guided run.\n"
        % (SERVER_NAME, FREE_QUOTA, HARD_CAP)
    )
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            send(err_response(None, -32700, "Parse error"))
            continue
        resp = handle(req)
        if resp is not None:
            send(resp)


if __name__ == "__main__":
    main()
