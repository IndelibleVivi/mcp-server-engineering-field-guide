# Review-bundle integrity

Exact-code review requires exact source identity.

## Before transfer

- Pin repository URL and full commit hash.
- Inventory intended files and byte sizes.
- Ensure text files decode as strict UTF-8 and contain no `U+FFFD`.
- Exclude secrets, credentials, account/session data, private chats, unrelated logs, and private local paths.
- Record a manifest or use the public commit as canonical identity.
- Prefer the smallest file set containing the truth.
- Exclude generated caches and compiled artifacts. A portable text review bundle should contain strict UTF-8 text only.
- Before reading a ZIP member, bound member count, per-member uncompressed size, total uncompressed size, and compression ratio.

## After ingestion

- Recount files/sections.
- Recheck strict UTF-8 and `U+FFFD`.
- Compare pinned revision and manifest.
- Inspect whether archive members were flattened, renamed, truncated, or transcoded.
- Ask the reviewer to state the source it actually used.

## Recovery

If archive text is corrupted:

1. stop exact-line/code claims from the damaged representation;
2. retain the damaged artifact only as transfer evidence;
3. use the public pinned commit when authorized;
4. otherwise send a delimited strict-UTF-8 text bundle with paths and boundaries;
5. rerun integrity checks after ingestion;
6. label any conclusions based only on partial or reconstructed source.

Checksums can establish byte identity only when both endpoints preserve bytes and a comparison decision actually uses the checksum. Do not compute them as ceremony.

The bundled scanner rejects binary members by default. If a review genuinely requires a binary, name each exact member with `--allow-binary`; the result will report that those members were explicitly excluded from text inspection rather than claiming a fully strict-text scan.
