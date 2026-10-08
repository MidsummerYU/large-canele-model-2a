# Beginner · dev · swiss-ai/Apertus-v1.5-8B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.928 | 0.97 / 0.93 / 0.89 | 0 | 81% | 613,791 | 569 / 1,287 |
| pairing: cross-language | 194 | 0.927 | 0.96 / 0.93 / 0.89 | 0 | 80% | 401,118 | 538 / 1,130 |
| pairing: same-language | 102 | 0.929 | 0.99 / 0.92 / 0.88 | 0 | 82% | 212,673 | 628 / 1,709 |
| claim_language: de | 99 | 0.917 | 0.97 / 0.91 / 0.87 | 0 | 79% | 197,615 | 619 / 1,677 |
| claim_language: fr | 99 | 0.927 | 0.94 / 0.96 / 0.88 | 0 | 90% | 216,487 | 591 / 1,264 |
| claim_language: it | 98 | 0.939 | 1.00 / 0.91 / 0.91 | 0 | 73% | 199,689 | 496 / 1,021 |
| reference_language: de | 91 | 0.873 | 0.97 / 0.87 / 0.78 | 0 | 91% | 191,674 | 599 / 1,619 |
| reference_language: fr | 114 | 0.973 | 0.99 / 0.97 / 0.96 | 0 | 67% | 218,600 | 536 / 1,139 |
| reference_language: it | 91 | 0.923 | 0.95 / 0.94 / 0.88 | 0 | 90% | 203,517 | 581 / 1,257 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 98 | 0 | 0 |
| neutral | 0 | 96 | 3 |
| contradiction | 6 | 12 | 81 |
