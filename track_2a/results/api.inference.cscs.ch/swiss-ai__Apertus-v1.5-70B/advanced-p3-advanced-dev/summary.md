# advanced-p3-advanced-dev · swiss-ai/Apertus-v1.5-70B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | quote verbatim | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.866 | 0.94 / 0.82 / 0.83 | 0 | 68% | 94% | 78% | 83% | 607,433 | 1,616 / 3,552 |
| pairing: cross-language | 194 | 0.888 | 0.94 / 0.84 / 0.88 | 0 | 64% | 91% | 76% | 82% | 411,993 | 1,685 / 3,622 |
| pairing: same-language | 102 | 0.823 | 0.93 / 0.79 / 0.75 | 0 | 75% | 97% | 81% | 86% | 195,440 | 1,487 / 3,323 |
| claim_language: de | 99 | 0.850 | 0.92 / 0.78 / 0.86 | 0 | 77% | 97% | 86% | 90% | 208,167 | 1,620 / 3,543 |
| claim_language: fr | 99 | 0.879 | 0.94 / 0.88 / 0.82 | 0 | 68% | 93% | 78% | 84% | 204,110 | 1,683 / 4,128 |
| claim_language: it | 98 | 0.868 | 0.95 / 0.83 / 0.82 | 0 | 60% | 91% | 69% | 77% | 195,156 | 1,546 / 3,611 |
| reference_language: de | 91 | 0.878 | 0.95 / 0.84 / 0.84 | 0 | 69% | 95% | 78% | 88% | 182,092 | 1,558 / 3,607 |
| reference_language: fr | 114 | 0.860 | 0.89 / 0.85 / 0.84 | 0 | 70% | 92% | 82% | 82% | 240,166 | 1,628 / 3,690 |
| reference_language: it | 91 | 0.862 | 0.98 / 0.78 / 0.82 | 0 | 66% | 94% | 72% | 80% | 185,175 | 1,661 / 3,367 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 90 | 6 | 2 |
| neutral | 0 | 80 | 19 |
| contradiction | 4 | 9 | 86 |
