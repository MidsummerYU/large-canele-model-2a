# advanced-p3-advanced-dev · swiss-ai/Apertus-v1.5-8B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.834 | 0.90 / 0.86 / 0.75 | 0 | 39% | 72% | 83% | 607,433 | 823 / 1,688 |
| pairing: cross-language | 194 | 0.809 | 0.88 / 0.83 / 0.72 | 0 | 35% | 73% | 82% | 411,993 | 924 / 2,116 |
| pairing: same-language | 102 | 0.882 | 0.93 / 0.91 / 0.80 | 0 | 47% | 71% | 86% | 195,440 | 629 / 1,335 |
| claim_language: de | 99 | 0.812 | 0.84 / 0.85 / 0.75 | 0 | 35% | 85% | 90% | 208,167 | 879 / 2,167 |
| claim_language: fr | 99 | 0.862 | 0.94 / 0.87 / 0.78 | 0 | 41% | 71% | 84% | 204,110 | 795 / 1,418 |
| claim_language: it | 98 | 0.825 | 0.91 / 0.86 / 0.71 | 0 | 41% | 59% | 77% | 195,156 | 794 / 1,624 |
| reference_language: de | 91 | 0.816 | 0.91 / 0.87 / 0.67 | 0 | 38% | 79% | 88% | 182,092 | 810 / 1,764 |
| reference_language: fr | 114 | 0.810 | 0.88 / 0.81 / 0.73 | 0 | 38% | 75% | 82% | 240,166 | 825 / 1,958 |
| reference_language: it | 91 | 0.876 | 0.90 / 0.90 / 0.83 | 0 | 40% | 62% | 80% | 185,175 | 832 / 1,603 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 91 | 7 | 0 |
| neutral | 0 | 99 | 0 |
| contradiction | 14 | 26 | 59 |
