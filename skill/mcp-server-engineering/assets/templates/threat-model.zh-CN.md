# MCP server threat model

Source revision：`<full commit or immutable source identity>`<br>
Declared MCP revision：`<revision>`<br>
Transport(s)：`<stdio / Streamable HTTP / custom>`<br>
Intended reachability：`<subprocess / loopback / LAN / private / public>`<br>
Assessment date：`<ISO date>`

## Capability inventory

| Capability | Entry points | Caller/authority | Inputs | Effects | State owner | Resource budgets | Result consumers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<name>` | `<methods/routes>` | `<identity or possession model>` | `<schema>` | `<read/write/network/process>` | `<owner>` | `<bytes/time/concurrency/rate>` | `<model/component/user/operator>` |

## Trust boundaries

| Boundary | Owner | Untrusted input | Control | Enforcement point | Required evidence | Residual |
| --- | --- | --- | --- | --- | --- | --- |
| `<boundary>` | `<layer>` | `<input>` | `<control>` | `<before/after what>` | `<test/probe>` | `<remaining risk>` |

## Enforcement partial order

```text
<header/process input>
  -> <early framing/authority/policy>
  -> <bounded decode>
  -> <protocol classification>
  -> <capability authorization and arguments>
  -> <effect>
  -> <projection/serialization/write>
```

## State 与 retry

| State/effect | Identity | Concurrency model | Expiry/revocation | Retry/idempotency | Failure after commit |
| --- | --- | --- | --- | --- | --- |
| `<item>` | `<session/operation/handle>` | `<lock/actor/store>` | `<rule>` | `<rule>` | `<client-visible behavior>` |

## Deployment ownership

| Layer | Configured | Activated | Observed | Owner | Unknowns |
| --- | --- | --- | --- | --- | --- |
| process |  |  |  |  |  |
| container |  |  |  |  |  |
| host publication |  |  |  |  |  |
| proxy/tunnel/TLS |  |  |  |  |  |
| auth server |  |  |  |  |  |
| MCP host |  |  |  |  |  |
