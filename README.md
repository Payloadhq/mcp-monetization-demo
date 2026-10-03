# MCP Monetization Demo — by Payload

A small, runnable MCP server that demonstrates **the core mechanic of the
paid MCP Monetization Kit**: per-tool-call metering with a free quota, then a
machine-readable `PAYMENT REQUIRED` response once the quota is exhausted.

Free tools stay free. Premium tools get a free quota (default 5 calls). After
that, callers see exactly how a paywall works — and the demo is hard-capped
(200 total calls) so it can't be used as a free service.

Run it in under a minute — Python 3.8+, stdlib only, nothing to install:

```bash
python3 demo.py
```

Output: a free tool call, two premium calls inside the quota, a third that
returns `PAYMENT_REQUIRED` with the upgrade path.

## What's deliberately missing (the paid kits)

This demo **proves the monetization mechanic works**. It does not replace the
paid products. Concretely, the demo has **no**:

- **Real payment collection.** The paid
  [**MCP Monetization Kit** ($69)](https://payloadtools.gumroad.com/l/mcp-monetization-kit)
  collects actual per-call USDC payments via the x402 flow, with two verifiers
  (HMAC dev verifier for testing, facilitator verifier for production) —
  non-custodial, it verifies payment then runs your tool.
- **Persistent usage ledger.** The demo's meter is in-memory and resets on
  restart. The kit ships a paid tool registry (registerTool / callTool /
  listTools) with per-tool pricing, free-quota logic, and an append-only
  usage ledger.
- **Official SDK adapter.** The kit adapts the real `@modelcontextprotocol/sdk`
  Server over the stdio transport (payment travels on
  `params._meta["x402/payment"]`, verified against SDK v1.32.0) and includes
  15 automated tests plus working example server and paying example client.
- **Security hardening.** The demo is intentionally unauthenticated. The
  [**MCP Launch Readiness Audit** ($79)](https://payloadtools.gumroad.com/l/mcp-launch-readiness-audit)
  gives you a 48-rule scanner with concrete fixes, hardened server templates
  (Python and TypeScript) with bearer-token auth, per-tool scopes and rate
  limits, a reliability stress-test harness, a deployment readiness verifier,
  CI wiring, a regression suite, and a branded audit PDF report.
- **No artificial caps.** The demo stops at 200 calls. The paid kits are yours
  to run unlimited — you set your own prices and quotas.

## Files

| File | What it is |
|---|---|
| `server.py` | The demo MCP server (JSON-RPC over stdio, stdlib only) |
| `demo.py` | Guided client: spins up the server, exhausts the quota, shows the paywall |
| `PUSH_CHECKLIST.md` | Internal push status (not part of the product) |

Tune the demo: `PAYLOAD_FREE_QUOTA=3 python3 demo.py`,
`PAYLOAD_HARD_CAP=500`.

## Payload Tools ecosystem

- **MCP Monetization Kit** — charge per tool call: https://payloadtools.gumroad.com/l/mcp-monetization-kit
- **MCP Launch Readiness Audit** — scan, fix, and prove launch readiness: https://payloadtools.gumroad.com/l/mcp-launch-readiness-audit
- **All Payload products** — https://payloadtools.gumroad.com
- **More Payload repos** — https://github.com/Payloadhq

Support: kylers.partners@gmail.com · "Small software that earns its keep."

---

**Payload** — small, sharp tools for developers.
Developer portal: https://payloadhq.github.io/ ·
All products: https://payloadtools.gumroad.com/ ·
Contact: kylers.partners@gmail.com
