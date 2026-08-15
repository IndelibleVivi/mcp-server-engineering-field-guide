---
case_study_id: gpt-thinking-block-mcp
document: public-evidence-index
version: 1
language: zh-CN
language_peer: PUBLIC-EVIDENCE-INDEX.md
---

# Public evidence index

简体中文 · [English](PUBLIC-EVIDENCE-INDEX.md)

本 index 区分 canonical public source、executed evidence、projected public receipts 与 unverified claims。

## Source identity

| ID | Source | Role |
| --- | --- | --- |
| SRC-UPSTREAM-681B991 | [`681b99124234628ad9fb01703925a2cd4396c002`](https://github.com/sibylsea-hub/gpt-thinking-block-mcp/commit/681b99124234628ad9fb01703925a2cd4396c002) | upstream comparison baseline |
| SRC-FORK-D43EBFB | [`d43ebfb`](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/commit/d43ebfb) | first hardened code / tests |
| SRC-FORK-E204360 | [`e204360`](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/commit/e204360) | deployment / support-boundary documentation |
| SRC-FORK-B533B84 | [`b533b84`](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/commit/b533b84) | independent-review follow-up |
| SRC-FORK-EC1379A | [`ec1379aa141a02a150ef7ce82ea4f5e92f55c72b`](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/commit/ec1379aa141a02a150ef7ce82ea4f5e92f55c72b) | assessed fork revision |

## Receipt vocabulary

- `original-observation`：durable receipt 前已有 evidence；后来 reconstruction 必须明示。
- `reproduced`：记录 receipt 时刻意再次执行 observation。
- `independently-reproduced`：独立 execution owner 在不把 original run 当 authority 的情况下复现。
- `representation: projected`：从 private raw receipt 派生的 public-safe representation；省略具名 material，但保留 typed source identity、environment、parameters、observables、provenance status 与 residual boundary。

Representation 与 execution provenance 相互正交。Sanitization/projection 不会使 execution 自动 independent；receipt schema v2 要求显式记录 independence flag、owner relationship、independence basis 与 omitted-material note。

## Executed receipts

| Receipt | Status | 支持什么 | Public representation |
| --- | --- | --- | --- |
| CI-PUBLIC-31888232847 | public CI | Python 3.9 / 3.12 compile + 60 tests | [GitHub Actions](https://github.com/IndelibleVivi/gpt-thinking-block-mcp/actions/runs/31888232847) |
| CI-EC1379A-001 | reproduced | CPython 3.13.3 / macOS arm64 上 60 tests | [`projected JSON receipt`](receipts/CI-EC1379A-001.public.json) |
| WIRE-HDR-001 | reproduced | renewable header idle timeout 不构成 absolute deadline | [`projected JSON receipt set`](receipts/WIRE-RECEIPTS-2026-08-15.public.json) |
| WIRE-ADMISSION-001 | reproduced | incomplete connections 在 tool limiting 前消耗 handler threads | same projected receipt set |
| WIRE-EXPECT-001 | reproduced | `100 Continue` 先于 application Origin denial | same projected receipt set |
| WIRE-DISCONNECT-001 | reproduced | ordinary disconnect 会产生 BrokenPipe traceback | same projected receipt set |

## Public receipts 刻意省略什么

- private absolute filesystem paths；
- raw model-review transcripts；
- user/account/session information；
- 含 local runtime paths 的 raw stderr；
- unrelated environment state；
- 任何声称 execution owner independent 的说法。

Public JSON 保留足够 observables 让读者质疑 inference，但不是 private raw receipt 的 byte-for-byte copy。

## Unverified boundaries

- Docker image build 与 container runtime；
- deployed reverse proxy、TLS、OAuth、tunnel 或 public-edge behavior；
- Python 3.9/3.12 或 non-macOS 上的 raw wire probes；
- current ChatGPT host rendering 与 submission acceptance；
- standard MCP Apps portability；
- sustained hostile scheduling 下的 availability behavior。

Future receipt 必须使用新 ID，保留 typed immutable source identity 与 environment；只有 execution provenance 真正变化时才能改变 status。
