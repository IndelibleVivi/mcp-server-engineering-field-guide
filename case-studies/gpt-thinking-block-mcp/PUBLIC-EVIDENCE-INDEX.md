---
case_study_id: gpt-thinking-block-mcp
document: public-evidence-index
version: 1
language: en
language_peer: PUBLIC-EVIDENCE-INDEX.zh-CN.md
---

# Public evidence index

[简体中文](PUBLIC-EVIDENCE-INDEX.zh-CN.md) · English

This index distinguishes canonical public source, executed evidence, projected public receipts, and unverified claims.

## Source identity

| ID | Source | Role |
| --- | --- | --- |
| SRC-UPSTREAM-681B991 | [`681b99124234628ad9fb01703925a2cd4396c002`](https://github.com/sibylsea-hub/gpt-thinking-block-mcp/commit/681b99124234628ad9fb01703925a2cd4396c002) | upstream comparison baseline |
| SRC-FORK-D43EBFB | [`d43ebfb`](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/commit/d43ebfb) | first hardened code and tests |
| SRC-FORK-E204360 | [`e204360`](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/commit/e204360) | deployment and support-boundary documentation |
| SRC-FORK-B533B84 | [`b533b84`](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/commit/b533b84) | independent-review follow-up |
| SRC-FORK-EC1379A | [`ec1379aa141a02a150ef7ce82ea4f5e92f55c72b`](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/commit/ec1379aa141a02a150ef7ce82ea4f5e92f55c72b) | assessed fork revision |

## Receipt vocabulary

- `original-observation`: evidence existed before a durable receipt; a later reconstruction must say so.
- `reproduced`: the observation was deliberately executed again while recording the receipt.
- `independently-reproduced`: a separate execution owner reproduced it without relying on the original run as authority.
- `representation: projected`: a public-safe representation derived from a private raw receipt. It omits named material while preserving typed source identity, environment, parameters, observables, provenance status, and residual boundary.

Representation and execution provenance are orthogonal. Sanitizing or projecting a receipt does not make its execution independent; receipt schema v2 requires the independence flag, owner relationship, independence basis, and omitted-material note to be explicit.

## Executed receipts

| Receipt | Status | What it supports | Public representation |
| --- | --- | --- | --- |
| CI-PUBLIC-31888232847 | public CI | compile + 60 tests on Python 3.9 and 3.12 | [GitHub Actions](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/actions/runs/31888232847) |
| CI-EC1379A-001 | reproduced | 60 tests on CPython 3.13.3 / macOS arm64 | [`projected JSON receipt`](receipts/CI-EC1379A-001.public.json) |
| WIRE-HDR-001 | reproduced | renewable header idle timeout does not form an absolute deadline | [`projected JSON receipt set`](receipts/WIRE-RECEIPTS-2026-08-15.public.json) |
| WIRE-ADMISSION-001 | reproduced | incomplete connections consume handler threads before tool limiting | same projected receipt set |
| WIRE-EXPECT-001 | reproduced | `100 Continue` precedes application Origin denial | same projected receipt set |
| WIRE-DISCONNECT-001 | reproduced | ordinary disconnects can emit BrokenPipe tracebacks | same projected receipt set |

## What the public receipts intentionally omit

- private absolute filesystem paths;
- raw model-review transcripts;
- user/account/session information;
- raw stderr containing local runtime paths;
- unrelated environment state;
- any claim that the execution owner was independent.

The public JSON contains enough observables to challenge the stated inference, but it is not a byte-for-byte copy of the private raw receipt.

## Unverified boundaries

- Docker image build and container runtime;
- deployed reverse proxy, TLS, OAuth, tunnel, or public-edge behavior;
- raw wire probes on Python 3.9/3.12 or non-macOS systems;
- current ChatGPT host rendering and submission acceptance;
- standard MCP Apps portability;
- availability behavior under sustained hostile scheduling.

Any future receipt should use a new ID, retain its typed immutable source identity and environment, and change the status only when the execution provenance truly changes.
