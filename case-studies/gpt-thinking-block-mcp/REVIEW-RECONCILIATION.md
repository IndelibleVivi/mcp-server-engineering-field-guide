---
case_study_id: gpt-thinking-block-mcp
document: review-reconciliation
version: 1
language: en
language_peer: REVIEW-RECONCILIATION.zh-CN.md
---

# Review reconciliation

This record compares independent review lanes without treating model rank, elapsed thinking time, or confident prose as assurance.

[简体中文](REVIEW-RECONCILIATION.zh-CN.md) · English

## Review shape

| Lane | Input boundary | Primary attack surface |
| --- | --- | --- |
| Implementation lane | upstream baseline, initial threat model, tests written with the patch | capability authority, JSON-RPC shapes, request bounds, capture, deployment docs |
| Review lane A | actual hardened source/diff and tests | low-level parser/runtime behavior, Unicode/numeric edges, error exits, response framing |
| Review lane B | fresh public pinned commits and independent brief | wire-level composition, effective authority, auth metadata, review-bundle integrity, residual deployment claims |
| Runtime-probe lane | pinned fork revision in a real local process | behavior inherited before handler dispatch or outside unit-test seams |

The two review lanes had overlapping context but different prompts and execution histories. They are useful as orthogonal instruments, not statistically independent samples.

## Finding ledger

| ID | Finding | First strong signal | Reproduction | Disposition |
| --- | --- | --- | --- | --- |
| R-001 | equivalent MCP and REST actions need one validator and limiter | implementation | focused unit/integration tests | adopted |
| R-002 | notifications and client responses must not execute request-only tool methods | implementation + lane A | classifier tests | adopted |
| R-003 | huge decimal `Content-Length` can consume parser work before ordinary size comparison | lane A | direct handler test | adopted with bounded decimal policy |
| R-004 | malformed/lone-surrogate/non-finite JSON needed an explicit accepted-language boundary | lane A | HTTP and classifier tests | adopted |
| R-005 | framing errors were being collapsed into JSON-RPC parse errors | lane B | transport-error tests | adopted; HTTP and JSON-RPC domains separated |
| R-006 | absolute-form authority and `Host` could disagree across route and policy layers | lane B | raw request-target tests | adopted |
| R-007 | parsed-authority caching by path alone could reuse a previous Host decision | implementation regression test after R-006 | two-request keep-alive test | adopted; cache key includes target and Host values |
| R-008 | configured bearer mode disagreed with `WWW-Authenticate`, tool metadata, or OpenAPI | lane B | runtime-mode metadata tests | adopted |
| R-009 | invalid forwarded authority and generated public base needed one trust model | lane A + lane B | configuration/request tests | adopted in code where enforceable; deployment ownership clarified |
| R-010 | a renewable body idle timeout did not guarantee a whole-body deadline | lane A | slow-trickle body test | adopted as absolute body deadline |
| R-011 | header parsing remained outside that absolute body deadline | lane B / runtime probe | `WIRE-HDR-001` | recorded residual |
| R-012 | thread-per-connection admission occurs before the tool limiter | lane B / runtime probe | `WIRE-ADMISSION-001` | recorded residual; deployment perimeter remains required |
| R-013 | `Expect: 100-continue` was emitted before application Origin denial | runtime probe | `WIRE-EXPECT-001` | recorded residual |
| R-014 | remote disconnects could emit full `BrokenPipeError` tracebacks | runtime probe | `WIRE-DISCONNECT-001` | recorded residual |
| R-015 | capture failure could leak raw thinking through diagnostics | lane A | forced-failure tests | adopted; only bounded metadata is logged |
| R-016 | capture-on annotations still claimed read-only behavior | implementation | schema/runtime-mode tests | adopted |
| R-017 | `204 No Content` response framing needed a wire-correct path | lane A | preflight test | adopted |
| R-018 | the widget was ChatGPT-bridge-specific, not a standard portable MCP Apps bridge | lane B | source/docs inspection | documentation corrected; portable bridge deferred |
| R-019 | Docker runtime and non-root behavior were not executed locally | lane B | tool/runtime inventory | kept `unverified`; no invented receipt |
| R-020 | fractional numeric IDs are discouraged by JSON-RPC but not universally invalid | later protocol reconciliation | normative-source check | recorded as deliberate compatibility narrowing, not a spec claim |

## Where the reviews disagreed or overreached

### Proxy identity

One review inferred that enabling trusted forwarded headers implied validation of the immediate network peer. The application had no enforceable peer identity signal. The finding was not “fixed” with a cosmetic check; documentation was changed to say the operator must ensure untrusted clients cannot bypass the proxy and that the proxy overwrites forwarded headers.

This is the correct response when the application layer lacks the authority needed to implement a proposed control.

### `Expect: 100-continue`

Source inspection alone suggested the handler policy might reject before body transfer. The raw socket transcript showed the inherited framework emitted `100 Continue` first. The observed wire sequence overruled the source-level assumption.

### Protocol IDs

Review correctly required JSON-RPC error codes to be integers. Request IDs are different: base JSON-RPC permits Number while discouraging fractional parts. The fork chose string/integer-only interoperability. The general guide must preserve the normative distinction rather than turning one project's accepted-language policy into a universal rule.

### Portable widget work

A standard MCP Apps `postMessage` bridge would improve portability, but it changes product and host-compatibility scope and needs real host tests. It was not smuggled into a transport-hardening patch. The existing compatibility boundary was documented precisely.

## Review-bundle integrity incident

One uploaded ZIP reached a reviewer with irreversible `U+FFFD` replacement characters even though the local manifest and strict-UTF-8 source set were intact. The review recovered by reading the public pinned commit instead of treating corrupted attachment text as authority.

Reusable handling:

1. retain the original source identity and manifest outside the upload transformation;
2. after ingestion, check strict UTF-8, replacement-character count, file count, and pinned revision;
3. if a binary archive path has been transcoded, do not reconstruct exact code from damaged text;
4. prefer a delimited strict-UTF-8 text bundle for manual model upload when archive handling is uncertain;
5. let the reviewer fetch a public pinned commit when disclosure policy permits;
6. record which source was actually reviewed.

## What “independent” means here

- The review prompts and analysis lanes were separate.
- The implementation tests were still authored in the same development effort and therefore are not independent assurance.
- The local wire receipts were re-executed and recorded, but not executed by an unrelated owner; their status is `reproduced`, not `independently-reproduced`.
- Public CI executed the test suite on additional runtimes, but it did not run the local raw-socket probe suite.

The combined evidence is stronger because the lanes failed differently, not because any one lane was declared superior.
