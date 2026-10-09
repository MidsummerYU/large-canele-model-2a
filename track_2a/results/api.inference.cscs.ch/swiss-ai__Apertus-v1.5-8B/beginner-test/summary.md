# beginner-test · swiss-ai/Apertus-v1.5-8B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| all: all | 1192 | 0.934 | 0.96 / 0.95 / 0.89 | 1 | 74% | – | – | 2,388,019 | 522 / 1,135 |
| pairing: cross-language | 779 | 0.917 | 0.95 / 0.93 / 0.87 | 0 | 72% | – | – | 1,528,164 | 514 / 1,068 |
| pairing: same-language | 413 | 0.967 | 0.99 / 0.97 / 0.94 | 1 | 76% | – | – | 859,855 | 536 / 1,310 |
| claim_language: de | 396 | 0.956 | 0.96 / 0.98 / 0.93 | 0 | 68% | – | – | 771,789 | 584 / 1,153 |
| claim_language: fr | 398 | 0.906 | 0.95 / 0.92 / 0.84 | 1 | 84% | – | – | 817,641 | 475 / 1,008 |
| claim_language: it | 398 | 0.939 | 0.97 / 0.94 / 0.90 | 0 | 69% | – | – | 798,589 | 506 / 1,210 |
| reference_language: de | 364 | 0.907 | 0.96 / 0.92 / 0.84 | 0 | 79% | – | – | 694,582 | 510 / 1,173 |
| reference_language: fr | 455 | 0.953 | 0.97 / 0.96 / 0.93 | 1 | 66% | – | – | 865,220 | 509 / 1,045 |
| reference_language: it | 373 | 0.934 | 0.94 / 0.96 / 0.89 | 0 | 79% | – | – | 828,217 | 548 / 1,219 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 397 | 0 | 0 |
| neutral | 0 | 395 | 4 |
| contradiction | 33 | 40 | 323 |
