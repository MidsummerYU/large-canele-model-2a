# advanced-p5-advanced-dev · swiss-ai/Apertus-v1.5-8B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.829 | 0.90 / 0.86 / 0.73 | 0 | 36% | 72% | 95% | 873,991 | 922 / 1,786 |
| pairing: cross-language | 194 | 0.802 | 0.89 / 0.82 / 0.70 | 0 | 30% | 74% | 97% | 585,713 | 993 / 1,965 |
| pairing: same-language | 102 | 0.882 | 0.93 / 0.92 / 0.79 | 0 | 48% | 68% | 92% | 288,278 | 788 / 1,678 |
| claim_language: de | 99 | 0.767 | 0.84 / 0.81 / 0.65 | 0 | 27% | 75% | 97% | 287,313 | 987 / 2,371 |
| claim_language: fr | 99 | 0.885 | 0.94 / 0.90 / 0.81 | 0 | 41% | 75% | 95% | 298,363 | 946 / 2,077 |
| claim_language: it | 98 | 0.834 | 0.93 / 0.87 / 0.71 | 0 | 40% | 65% | 94% | 288,315 | 833 / 1,583 |
| reference_language: de | 91 | 0.805 | 0.90 / 0.87 / 0.65 | 0 | 41% | 78% | 97% | 259,309 | 935 / 2,049 |
| reference_language: fr | 114 | 0.796 | 0.90 / 0.81 / 0.68 | 0 | 31% | 73% | 96% | 340,038 | 901 / 2,214 |
| reference_language: it | 91 | 0.889 | 0.92 / 0.91 / 0.84 | 0 | 39% | 65% | 92% | 274,644 | 937 / 1,700 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 94 | 4 | 0 |
| neutral | 0 | 95 | 4 |
| contradiction | 16 | 24 | 59 |
