# Upgrade retirement inventory

Source profile: `<profile ID>`<br>
Target profile: `<profile ID>`<br>
Pinned source revision: `<typed immutable identity>`

Use exactly one disposition for every relevant item: `retained`, `replaced`, `retired`, or `not-applicable`.

| Item ID | Category | Active source path or claim | Target disposition | Replacement / removal evidence | Regression or absence test | Residual |
| --- | --- | --- | --- | --- | --- | --- |
| `UPG-001` | `<route-method/header/state-store/background-task/compatibility-adapter/test-fixture/documentation-claim/deployment-configuration>` | `<location and behavior>` | `<retained/replaced/retired/not-applicable>` | `<source diff or receipt>` | `<test/receipt>` | `<remaining limit>` |

## Completion rule

A passing target request is not retirement evidence. Search old entry points, callers, configuration, tests, and documentation; record any intentionally retained compatibility path and its removal condition.
