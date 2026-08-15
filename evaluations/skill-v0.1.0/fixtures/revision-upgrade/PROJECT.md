# Synthetic revision upgrade

- Source MCP revision: `2025-11-25`.
- Target MCP revision: `2026-07-28`.
- The target request path is implemented and covered by one positive test.
- The old session registry and GET SSE route remain reachable through the legacy dispatcher.
- The upgrade is complete only when superseded behavior is removed and its absence is tested.
- Evidence included here: source and unit-test text only; the tests have not been executed in this fixture.
