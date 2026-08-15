## `[severity]` Finding title

Finding ID：`<stable ID>`<br>
Source identity：`<type>:<full immutable value>`<br>
Protocol profile：`<profile ID>`<br>
Status：`<confirmed / contradicted / partial / unknown>`

### Claim

用一句可 falsify 的话说明 behavior 与 impact。

### Evidence

- Source：`<file:line or public link>`
- Executed check：`<command/test/probe>`
- Observed：`<exact observable>`
- Provenance：`<original-observation / reproduced / independently-reproduced>`

### Boundary 与 impact

命名受影响的 capability、resource、state、identity 或 output。说明 evidence 能证明和不能证明什么。

### Recommended disposition

`<adopt / adapt / defer / reject>` — 指定最小、符合 owner 边界的 change。

### Verification

列出 change 后需要的 regression test 或 runtime receipt。

### Residual

说明仍未验证或超出 selected scope 的部分。
