# Evidence discipline

## Claim ladder

Use the lowest claim supported by the observed boundary:

| Evidence | Permitted claim |
| --- | --- |
| source inspection | code appears to implement a behavior |
| unit test | tested function behavior in test conditions |
| handler/integration test | framework path behaved under the test harness |
| raw socket transcript | observed wire sequence in a named runtime |
| real-process smoke | activated local listener behaved for selected requests |
| container probe | built image/container behaved in named engine/network |
| proxy/tunnel probe | deployed intermediate path behaved as observed |
| host acceptance | named host discovered/rendered/invoked as observed |
| independent reproduction | a separate owner repeated a defined receipt |

Never skip levels in the written conclusion.

## Receipt provenance

- `original-observation`: evidence predated a durable receipt; reconstruction is labeled.
- `reproduced`: execution was deliberately repeated while recording the receipt.
- `independently-reproduced`: another owner repeated it without treating the first run as authority.
- sanitization/projection changes representation, not execution provenance.
- `independently-reproduced` is valid if and only if `independent_execution` is true and the owner relationship is independently stated.

## Minimum receipt fields

- receipt ID and schema version;
- claim under test;
- typed immutable source identity (`git-sha1`, `git-sha256`, or `content-sha256`);
- runtime/OS/architecture or service version;
- executed timestamp;
- command or test method;
- parameters and limits;
- expected observable;
- actual observable;
- exit/status;
- provenance status, required independence flag, execution owner class, owner relationship, and independence basis;
- representation (`raw`, `sanitized`, `projected`, or `reconstructed`) and omitted/raw-material note;
- residual boundary.

## Review reconciliation

For each reviewer suggestion:

1. translate prose into a falsifiable claim;
2. locate the enforcement owner;
3. reproduce against pinned source;
4. mark confirmed, contradicted, partially confirmed, or unknown;
5. adopt, adapt, defer, or reject with a reason;
6. add a regression test only if it protects the actual contract;
7. record new residuals created by the fix.

Elapsed thought time and model tier are provenance metadata, not evidence weight.
