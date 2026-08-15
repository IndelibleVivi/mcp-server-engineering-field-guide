# Deployment ownership map

Use when code, container, proxy, tunnel, authentication, and host behavior are being discussed as if they were one boundary.

| Layer | Evidence to inspect | Typical responsibilities |
| --- | --- | --- |
| source checkout | revision, diff, tests | declared behavior and implementation |
| process runtime | args/env names, listener, logs | bind, parser/runtime version, in-process state |
| container | image, user, health, namespace | filesystem/process isolation and internal bind |
| host publication | port mapping, firewall | LAN/loopback/public reachability |
| reverse proxy/tunnel | route, TLS, peer/auth config | ingress identity, header rewriting, edge limits |
| authorization server | discovery, issuer, keys, scopes | identities, tokens, consent, revocation |
| MCP host/client | discovery, capabilities, rendering | compatibility, user consent surfaces, sandbox |

## Proof rules

- `127.0.0.1` in direct-run code does not prove a container's host port is loopback-only.
- `0.0.0.0` inside a container does not by itself mean host-public exposure.
- a connected tunnel proves a path exists, not that application auth or parsing is safe.
- Host/Origin checks do not authenticate a user.
- trusting `X-Forwarded-*` needs an enforceable network owner that blocks bypass and overwrites headers.
- a static Compose parse does not prove the container built, became healthy, or published the expected socket.
- a successful local curl does not prove a remote host can discover, authenticate, or render.

## Reporting

For each layer, report separately:

- configured;
- activated;
- observed;
- unverified;
- owner;
- rollback/stop mechanism.

Do not write “secure deployment” without naming the topology and the controls actually observed.
