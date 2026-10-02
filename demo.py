#!/usr/bin/env python3
"""Guided metering demo: starts server.py, exhausts the free quota,
and shows the PAYMENT REQUIRED response. Python 3.8+, stdlib only."""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SAMPLE = (
    "Model Context Protocol servers are useful. Useful servers deserve to be "
    "paid for. This demo shows a free quota of premium tool calls, then a "
    "machine-readable payment requirement. Developers can wrap each tool "
    "with a price while keeping free tools free."
)


class Client:
    def __init__(self, quota):
        env = dict(os.environ)
        env["PAYLOAD_FREE_QUOTA"] = str(quota)
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(HERE, "server.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )
        self.seq = 0

    def call(self, method, params=None, notify=False):
        self.seq += 1
        msg = {"jsonrpc": "2.0", "method": method}
        if not notify:
            msg["id"] = self.seq
        if params is not None:
            msg["params"] = params
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        return json.loads(self.proc.stdout.readline())

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=5)


def tool_text(resp):
    return resp["result"]["content"][0]["text"]


def main():
    quota = int(os.environ.get("DEMO_QUOTA", "2"))
    c = Client(quota)
    try:
        init = c.call(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "demo-client", "version": "1.0.0"},
            },
        )
        print("connected to:", init["result"]["serverInfo"]["name"])
        c.call("notifications/initialized", notify=True)

        tools = c.call("tools/list")["result"]["tools"]
        print("tools:", ", ".join(t["name"] for t in tools))

        r = c.call("tools/call", {"name": "word_count", "arguments": {"text": SAMPLE}})
        print("\n[word_count — FREE, unlimited]\n" + tool_text(r))

        print("\n--- premium calls (free quota: %d) ---" % quota)
        for i in range(quota + 1):
            r = c.call(
                "tools/call",
                {"name": "extract_keywords", "arguments": {"text": SAMPLE, "limit": 5}},
            )
            text = tool_text(r)
            is_err = r["result"].get("isError")
            print("\n[premium call %d — %s]" % (i + 1, "PAYMENT REQUIRED" if is_err else "ok"))
            print(text[:600])
    finally:
        c.close()
    print("\nDemo complete. The mechanic works: free quota, then payment required.")


if __name__ == "__main__":
    main()
