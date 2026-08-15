# Low-level HTTP server review

Use for direct socket code, standard-library handlers, or thin frameworks where the application owns significant HTTP behavior.

Normative sources:

- RFC 9110: <https://www.rfc-editor.org/rfc/rfc9110.html>
- RFC 9112: <https://www.rfc-editor.org/rfc/rfc9112.html>

## Framing

- Complete header parsing before choosing body framing.
- Reject `Transfer-Encoding` plus `Content-Length` ambiguity and close the connection.
- Decide and document policy for repeated `Content-Length`; stricter rejection may exceed RFC minimums.
- Reject unsupported transfer coding before dispatch.
- Check declared size before allocation and body consumption.
- Close after an early error that leaves unread body bytes unless drain/resynchronization is proven.
- Use strict required encoding and reject malformed JSON without replacement.

## Time and admission

Measure separately:

- header-completion deadline;
- absolute body-completion deadline;
- optional per-read idle timeout;
- listener backlog and connection/task/thread admission;
- capability deadline/concurrency/rate;
- response serialization/write deadline.

Test slow trickle. A renewable read timeout is not an absolute deadline. Test concurrency before headers complete; a tool limiter is too late.

## Target and authority

- Enumerate accepted request-target forms.
- Validate exact route and query policy.
- Derive effective authority consistently from target and Host according to the selected deployment architecture.
- Test malformed, duplicate, absolute-form, userinfo-bearing, percent-encoded, and keep-alive target/Host combinations.
- Include all raw inputs affecting a parsed-authority cache key or avoid cross-request caching.

## Pre-dispatch framework behavior

Probe actual wire behavior for:

- `Expect: 100-continue`;
- header size/count and timeout;
- automatic error responses;
- decoding/normalization before handler hooks;
- thread/task creation;
- disconnect exception logging.

Source-level handler guards do not prove what happens before the handler.

## Response boundary

- Serialize bounded results before header commit when practical.
- Distinguish execution failure, projection failure, serialization failure, and write failure.
- Catch expected disconnects without log amplification.
- Record whether a side effect committed before delivery failed and how retry avoids duplication.

## Essential wire probes

- duplicate/conflicting length;
- transfer coding plus length;
- huge decimal length;
- incomplete and slow-trickle headers/body;
- denied request with `Expect: 100-continue`;
- unread-body rejection followed by a second request;
- Host/absolute-form disagreement on keep-alive;
- concurrent incomplete connections;
- disconnect during result write.
