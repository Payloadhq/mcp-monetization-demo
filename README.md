# MCP Monetization Demo

*by Payload — a free, runnable demo of per-tool-call metering for MCP servers.*

A small, runnable MCP server that demonstrates **the core mechanic of the
paid MCP Monetization Engine**: per-tool-call metering with a free quota (default
2 calls in the guided demo; 5 when running `server.py` directly), then a
machine-readable `PAYMENT REQUIRED` response once the quota is exhausted.

Free tools stay free. After the quota, callers see exactly how a paywall
works — and the demo is hard-capped (200 total calls) so it can't be used
as a free service.

## Who it's for

Developers considering the MCP Monetization Engine who want to see the paywall mechanic run before buying.

## Try it (free, under a minute)

Python 3.8+, stdlib only, nothing to install:

```bash
python3 demo.py
```

Output: a free tool call, two premium calls inside the quota, a third that
returns `PAYMENT_REQUIRED` with the upgrade path.

Tune the demo: `DEMO_QUOTA=3 python3 demo.py`,
`PAYLOAD_HARD_CAP=500`.

## Files

| File | What it is |
|---|---|
| `server.py` | The demo MCP server (JSON-RPC over stdio, stdlib only) |
| `demo.py` | Guided client: spins up the server, exhausts the quota, shows the paywall |

## What this demo does NOT include (the paid kits)

This demo **proves the monetization mechanic works**. It does not replace the
paid products. Concretely, the demo has **no**:

- **Real payment collection.** The paid
  [**MCP Monetization Engine** ($69)](https://payloadtools.gumroad.com/l/mcp-monetization-kit)
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

## Price

**Free.** This demo costs nothing and needs no purchase. The paid kits it
demonstrates are $69 (MCP Monetization Engine) and $79 (MCP Launch Readiness Audit).

## Support

- Support: kylers.partners@gmail.com
- "Small software that earns its keep."

## Payload Tools ecosystem

- **MCP Monetization Engine** — charge per tool call: https://payloadtools.gumroad.com/l/mcp-monetization-kit
- **MCP Launch Readiness Audit** — scan, fix, and prove launch readiness: https://payloadtools.gumroad.com/l/mcp-launch-readiness-audit
- **All Payload products** — https://payloadtools.gumroad.com
- **More Payload repos** — https://github.com/Payloadhq

---

**Payload** — small, sharp tools for developers.
Developer portal: https://payloadhq.github.io/ ·
All products: https://payloadtools.gumroad.com/ ·
Contact: kylers.partners@gmail.com

---

**More from Payload** · [payloadhq.github.io](https://payloadhq.github.io/) · [all Payload repos](https://github.com/Payloadhq)

Related: [mcp-monetization-kit](https://github.com/Payloadhq/mcp-monetization-kit) · [payload-sample-mcp-server](https://github.com/Payloadhq/payload-sample-mcp-server)
