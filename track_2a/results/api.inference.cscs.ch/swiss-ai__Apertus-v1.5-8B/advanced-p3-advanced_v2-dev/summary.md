# advanced-p3-advanced_v2-dev · swiss-ai/Apertus-v1.5-8B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | quote verbatim | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.850 | 0.89 / 0.86 / 0.80 | 0 | 53% | 86% | 67% | 83% | 635,257 | 808 / 1,656 |
| pairing: cross-language | 194 | 0.845 | 0.88 / 0.86 / 0.80 | 0 | 51% | 84% | 67% | 82% | 430,229 | 889 / 1,665 |
| pairing: same-language | 102 | 0.858 | 0.92 / 0.88 / 0.78 | 0 | 58% | 91% | 67% | 86% | 205,028 | 654 / 1,634 |
| claim_language: de | 99 | 0.808 | 0.84 / 0.81 / 0.77 | 0 | 48% | 85% | 70% | 90% | 217,473 | 864 / 1,914 |
| claim_language: fr | 99 | 0.887 | 0.94 / 0.90 / 0.83 | 0 | 62% | 86% | 65% | 84% | 213,416 | 814 / 1,617 |
| claim_language: it | 98 | 0.855 | 0.89 / 0.89 / 0.79 | 0 | 49% | 88% | 66% | 77% | 204,368 | 746 / 1,540 |
| reference_language: de | 91 | 0.832 | 0.86 / 0.89 / 0.75 | 0 | 52% | 88% | 68% | 88% | 190,646 | 839 / 1,902 |
| reference_language: fr | 114 | 0.824 | 0.89 / 0.81 / 0.77 | 0 | 57% | 84% | 70% | 82% | 250,882 | 788 / 1,658 |
| reference_language: it | 91 | 0.901 | 0.93 / 0.91 / 0.87 | 0 | 51% | 88% | 61% | 80% | 193,729 | 804 / 1,535 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 87 | 6 | 5 |
| neutral | 0 | 91 | 8 |
| contradiction | 10 | 15 | 74 |
