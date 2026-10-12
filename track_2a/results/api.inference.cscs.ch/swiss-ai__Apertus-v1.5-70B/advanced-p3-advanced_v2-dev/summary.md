# advanced-p3-advanced_v2-dev · swiss-ai/Apertus-v1.5-70B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | quote verbatim | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.869 | 0.94 / 0.82 / 0.85 | 0 | 63% | 93% | 76% | 83% | 635,257 | 1,708 / 3,465 |
| pairing: cross-language | 194 | 0.892 | 0.94 / 0.85 / 0.89 | 0 | 64% | 90% | 74% | 82% | 430,229 | 1,767 / 3,558 |
| pairing: same-language | 102 | 0.823 | 0.94 / 0.76 / 0.77 | 0 | 62% | 99% | 79% | 86% | 205,028 | 1,595 / 3,206 |
| claim_language: de | 99 | 0.859 | 0.92 / 0.78 / 0.88 | 0 | 69% | 96% | 81% | 90% | 217,473 | 1,794 / 3,783 |
| claim_language: fr | 99 | 0.890 | 0.94 / 0.88 / 0.86 | 0 | 66% | 93% | 79% | 84% | 213,416 | 1,684 / 3,982 |
| claim_language: it | 98 | 0.856 | 0.97 / 0.79 / 0.81 | 0 | 55% | 92% | 68% | 77% | 204,368 | 1,645 / 3,241 |
| reference_language: de | 91 | 0.900 | 0.95 / 0.87 / 0.87 | 0 | 65% | 95% | 77% | 88% | 190,646 | 1,696 / 3,686 |
| reference_language: fr | 114 | 0.878 | 0.92 / 0.85 / 0.86 | 0 | 67% | 95% | 79% | 82% | 250,882 | 1,646 / 3,410 |
| reference_language: it | 91 | 0.828 | 0.96 / 0.71 / 0.81 | 0 | 57% | 90% | 72% | 80% | 193,729 | 1,797 / 3,808 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 90 | 6 | 2 |
| neutral | 0 | 76 | 23 |
| contradiction | 3 | 5 | 91 |
