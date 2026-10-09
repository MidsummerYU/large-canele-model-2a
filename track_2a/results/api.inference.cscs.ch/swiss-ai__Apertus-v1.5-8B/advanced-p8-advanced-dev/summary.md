# advanced-p8-advanced-dev · swiss-ai/Apertus-v1.5-8B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.817 | 0.89 / 0.85 / 0.71 | 0 | 32% | 66% | 100% | 1,258,074 | 2,472 / 2,308 |
| pairing: cross-language | 194 | 0.773 | 0.88 / 0.79 / 0.65 | 0 | 29% | 62% | 100% | 838,452 | 2,746 / 2,467 |
| pairing: same-language | 102 | 0.904 | 0.92 / 0.96 / 0.83 | 0 | 38% | 73% | 100% | 419,622 | 1,952 / 2,149 |
| claim_language: de | 99 | 0.793 | 0.85 / 0.87 / 0.65 | 0 | 26% | 66% | 100% | 414,388 | 5,187 / 4,546 |
| claim_language: fr | 99 | 0.853 | 0.90 / 0.87 / 0.79 | 0 | 48% | 75% | 100% | 426,541 | 1,154 / 2,260 |
| claim_language: it | 98 | 0.805 | 0.93 / 0.81 / 0.68 | 0 | 21% | 56% | 100% | 417,145 | 1,062 / 2,180 |
| reference_language: de | 91 | 0.724 | 0.85 / 0.76 / 0.56 | 0 | 20% | 70% | 100% | 378,859 | 2,201 / 3,393 |
| reference_language: fr | 114 | 0.829 | 0.90 / 0.87 / 0.71 | 0 | 35% | 73% | 100% | 487,189 | 2,871 / 2,364 |
| reference_language: it | 91 | 0.888 | 0.92 / 0.92 / 0.82 | 0 | 40% | 55% | 100% | 392,026 | 2,244 / 2,226 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 95 | 3 | 0 |
| neutral | 2 | 94 | 3 |
| contradiction | 18 | 25 | 56 |
