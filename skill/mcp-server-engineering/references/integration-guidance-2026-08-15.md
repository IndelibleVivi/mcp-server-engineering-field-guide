---
profile_id: mcp-apps-and-openai-hosts-2026-08-15
profile_version: 1
assessed_at: 2026-08-15
status: moving-guidance
language: en
language_peer: integration-guidance-2026-08-15.zh-CN.md
---

# Moving integration guidance: MCP Apps and OpenAI hosts

This profile records integration guidance as observed on `2026-08-15`. It is deliberately separate from the normative protocol profiles because host behavior, product names, metadata aliases, submission rules, and documentation URLs can change on a different schedule.

## Sources assessed

- [MCP Apps overview](https://modelcontextprotocol.io/extensions/apps/overview)
- [MCP Apps specification and SDK documentation](https://apps.extensions.modelcontextprotocol.io/)
- [OpenAI: Add UI to an MCP server](https://developers.openai.com/plugins/build/chatgpt-ui)
- [OpenAI: Authenticate users](https://developers.openai.com/plugins/build/auth)
- [OpenAI: Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)

Re-check these sources before claiming current host support or publishing an integration.

## Two consumers, separate views

An MCP App result serves at least two consumers:

1. the assistant/model, which needs compact, semantically useful tool content and structured data;
2. the human-facing component, which needs renderable data and may receive additional UI-only metadata.

Treat the projection into each view as a security and correctness boundary. Do not assume a field hidden from the model is secret from the user, or that a field visible to the component is safe to render as HTML.

Test model-visible content, component-visible `structuredContent`, UI-only metadata, and the final DOM separately.

## Portable MCP Apps foundation

At this assessment date, the shared MCP Apps pattern uses:

- `_meta.ui.resourceUri` on a tool description to identify a `ui://` resource;
- a UI resource containing the HTML application, commonly with JavaScript and CSS bundled;
- the `ui/*` JSON-RPC bridge over `postMessage` for host/app communication;
- `tools/call` through the host rather than direct access from the sandbox to server authority;
- `_meta.ui.csp`, permissions, and related UI resource metadata for sandbox policy.

Build against the shared MCP Apps fields first. Treat host-specific aliases or globals as optional compatibility extensions, feature-detect them, and provide a fallback where practical.

## Tool and resource contracts

- Keep a tool useful without its UI when the workflow can be represented portably.
- Consider separating data tools from render tools. A data tool returns chainable `structuredContent`; a render tool attaches the final UI resource only when display is intended.
- Give tool names, descriptions, schemas, annotations, and output metadata the same review seriousness as executable code: they influence model routing and user consent.
- Treat a UI resource URI as a cache/version identity. Publish a new URI for a breaking HTML, JavaScript, or CSS change and update every referring tool.
- Declare only the exact external origins needed in CSP: API connections, static resources, and nested frames have distinct allowlists.

## Widget trust boundaries

- Assume all tool results and `postMessage` payloads are untrusted input to the widget.
- Check `event.source`, message shape, JSON-RPC version, expected method, request correlation, and payload schema before use.
- Render dynamic text with safe DOM APIs or framework escaping; do not concatenate untrusted content into HTML.
- Keep durable business data on the server or an authoritative service. UI-instance state is ephemeral; cross-session preferences need explicitly owned durable storage.
- The host sandbox limits parent-page access, but it does not validate your application data, prevent unsafe tool calls, or authorize external network requests on your behalf.

## OpenAI host compatibility

At this assessment date, OpenAI guidance prefers shared MCP Apps fields and bridge methods where available, while retaining ChatGPT compatibility aliases for existing integrations. New code should feature-detect any `window.openai` extension instead of branching on a product name.

For authenticated remote MCP servers, the documented model is OAuth 2.1 aligned with the MCP authorization specification:

- the MCP server is the resource server and verifies tokens on each request;
- protected-resource metadata identifies the canonical resource and authorization server;
- the authorization server publishes OAuth/OIDC discovery metadata;
- Resource Indicators bind tokens to the intended resource;
- issuer, audience, expiration, and scopes are verified before capability execution;
- Client ID Metadata Documents are preferred where supported, while other registration modes remain compatibility choices.

Do not invent a token header or partial “auth-like” mechanism and describe it as MCP OAuth.

## Tunnels and deployment

A tunnel changes reachability; it does not repair implementation invariants. Keep these owners separate:

| Layer | Typical owner | What it can establish |
| --- | --- | --- |
| local listener | server process | bind address, local admission, parsing |
| tunnel client | operator/infrastructure | authenticated private path or public reachability |
| edge/gateway | platform/operator | TLS, routing, selected auth and rate policy |
| MCP application | project | protocol classification, tool authority, arguments, state, effects, result contract |
| host | product | discovery, consent UI, sandbox behavior, compatibility |

A tunnel being connected is not evidence that Origin policy, protocol validation, authorization scopes, or tool side effects are correct.

## Integration test matrix

- host discovers exactly the intended tools and UI resources;
- tool remains useful in a non-UI client where promised;
- the component renders only the intended result fields;
- untrusted text cannot become active markup or script;
- widget-to-host calls are restricted to declared tools and validated arguments;
- CSP allows only observed required domains and blocks undeclared destinations;
- resource URI version changes invalidate the correct cache surface;
- OAuth discovery, challenge, PKCE, resource, issuer, audience, scopes, expiry, and reauthorization work end to end;
- the same build is exercised through the actual tunnel/edge/host route, not only localhost;
- error, disconnect, retry, and duplicate-effect behavior are visible and bounded.

## Known unknowns

- Host support matrices and review requirements are moving facts.
- Product-specific aliases may remain available without being the preferred portable contract.
- Sandbox and CSP enforcement details can differ by host.
- Secure MCP Tunnel availability, permissions, and supported flows are account- and organization-dependent.
- A local successful rendering does not prove submission or production-host acceptance.
