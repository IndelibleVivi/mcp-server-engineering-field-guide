# Upgrade retirement inventory

Source profile：`<profile ID>`<br>
Target profile：`<profile ID>`<br>
Pinned source revision：`<typed immutable identity>`

每个 relevant item 必须且只能选择一种 disposition：`retained`、`replaced`、`retired` 或 `not-applicable`。

| Item ID | Category | Active source path or claim | Target disposition | Replacement / removal evidence | Regression or absence test | Residual |
| --- | --- | --- | --- | --- | --- | --- |
| `UPG-001` | `<route-method/header/state-store/background-task/compatibility-adapter/test-fixture/documentation-claim/deployment-configuration>` | `<location 与 behavior>` | `<retained/replaced/retired/not-applicable>` | `<source diff 或 receipt>` | `<test/receipt>` | `<remaining limit>` |

## Completion rule

Target request 通过不等于已经证明 retirement。检查旧 entry points、callers、configuration、tests 与 documentation；记录任何有意保留的 compatibility path 及其 removal condition。
