# Stable core invariants

Apply these across protocol revisions, then specialize with the selected profile.

## Capability authority

- Map every externally reachable route to a capability.
- Equivalent routes share validation, authorization, budgets, effects, and result semantics.
- Reject unknown tool names and arguments before any effect.
- Treat descriptions, schemas, annotations, and resource metadata as runtime contracts.

## Accepted language

- Define exact transport framing, UTF-8 policy, JSON grammar, JSON-RPC kinds, method domain, ID domain, and parameter schema.
- Reject ambiguity before partial execution.
- Preserve the distinction between HTTP/transport errors, JSON parse errors, JSON-RPC errors, MCP method errors, and tool execution errors.

## Resource surfaces

Budget independently:

- header completion;
- connection/thread/task admission;
- body bytes and completion time;
- decode/parse/schema work;
- capability concurrency/rate/time;
- durable state and file writes;
- result serialization size/time;
- response write/backpressure;
- log volume.

Later controls do not protect earlier consumption.

## Trust and identity

- Reachability, Host authority, Origin, CORS, authentication, authorization, and proxy trust are separate.
- Do not trust forwarded fields without an enforceable proxy owner.
- Authentication must name issuer/resource/audience/scope or explicitly identify a limited non-OAuth possession model.
- A tunnel is a path, not a capability policy.

## State and effects

- Assign each mutable object one owner and synchronization model.
- Do not use transport session identity as an operation/idempotency identity.
- An annotation claiming read-only/destructive/idempotent behavior matches actual effects.
- Define failure after effect but before result delivery.

## Egress

- Project results separately for model, component, human, operator, and logs.
- Bound serialization and output.
- Treat disconnect, cancellation, retry, and duplicate effects as first-class behavior.
- Do not log sensitive raw arguments on ordinary failures.

## Deployment

- Distinguish process bind, container namespace bind, host publication, edge reachability, and host acceptance.
- Static config proof is not activated-runtime proof.
- State which layer owns TLS, authentication, admission, logs, and lifecycle.

## Documentation truthfulness

Examples and reference implementations still create runnable contracts. Documentation may limit scope but cannot make observable unsafe behavior disappear. Say exactly what is provided, omitted, operator-owned, and unverified.
