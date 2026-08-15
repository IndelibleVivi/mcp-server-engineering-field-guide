# MCP Apps review

Moving sources; recheck before current compatibility claims:

- <https://modelcontextprotocol.io/extensions/apps/overview>
- <https://apps.extensions.modelcontextprotocol.io/>

## Dual-consumer contract

An MCP App serves both model and human-facing component. Model-visible content, `structuredContent`, UI-only metadata, and final DOM are separate views. Define a projection policy for each.

## Portable foundation

As assessed on `2026-08-15`, portable MCP Apps commonly use:

- `_meta.ui.resourceUri` pointing to a `ui://` resource;
- HTML resource with `text/html;profile=mcp-app` or the then-current specified media type;
- `ui/*` JSON-RPC bridge over `postMessage`;
- host-mediated `tools/call`;
- `_meta.ui.csp`, permissions, and UI metadata.

Verify the current extension specification. Treat host globals/aliases as optional extensions, not the portable base.

## Audit checklist

- Tool remains useful without UI if promised.
- Data tool and render tool are separated when repeated iframe rendering would be wasteful.
- Resource URI changes for breaking UI changes and functions as cache identity.
- `postMessage` handler validates source, protocol shape, method, correlation, and payload schema.
- Untrusted tool content is escaped and never concatenated into active HTML.
- CSP declares exact connect/resource/frame domains.
- Widget can call only intended tools with validated arguments.
- UI state, durable business state, and cross-session preference state have explicit owners.
- Model-visible data excludes UI-only or sensitive fields by construction.
- Component-visible data is still treated as untrusted.
- Host compatibility is tested in the named host/version.

A sandbox prevents parent-page access; it does not validate data, authorize tools, or make external calls safe.
