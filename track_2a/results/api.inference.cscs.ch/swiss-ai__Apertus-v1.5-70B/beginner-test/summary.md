# beginner-test · swiss-ai/Apertus-v1.5-70B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| all: all | 1192 | 0.870 | 0.99 / 0.79 / 0.83 | 0 | 74% | – | – | 2,388,019 | 1,297 / 3,172 |
| pairing: cross-language | 779 | 0.878 | 0.99 / 0.79 / 0.85 | 0 | 73% | – | – | 1,528,164 | 1,254 / 2,851 |
| pairing: same-language | 413 | 0.856 | 0.99 / 0.78 / 0.80 | 0 | 74% | – | – | 859,855 | 1,377 / 3,881 |
| claim_language: de | 396 | 0.865 | 0.99 / 0.77 / 0.83 | 0 | 74% | – | – | 771,789 | 1,488 / 3,715 |
| claim_language: fr | 398 | 0.901 | 0.99 / 0.85 / 0.86 | 0 | 72% | – | – | 817,641 | 1,169 / 2,920 |
| claim_language: it | 398 | 0.844 | 1.00 / 0.73 / 0.81 | 0 | 75% | – | – | 798,589 | 1,233 / 3,170 |
| reference_language: de | 364 | 0.836 | 0.99 / 0.73 / 0.79 | 0 | 81% | – | – | 694,582 | 1,386 / 3,881 |
| reference_language: fr | 455 | 0.881 | 0.99 / 0.80 / 0.85 | 0 | 77% | – | – | 865,220 | 1,227 / 2,756 |
| reference_language: it | 373 | 0.889 | 0.99 / 0.82 / 0.85 | 0 | 62% | – | – | 828,217 | 1,295 / 3,073 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 397 | 0 | 0 |
| neutral | 0 | 264 | 135 |
| contradiction | 8 | 8 | 380 |
