# advanced-p3-advanced_v2-test · swiss-ai/Apertus-v1.5-70B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | quote verbatim | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| all: all | 1192 | 0.832 | 0.93 / 0.77 / 0.79 | 0 | 58% | 90% | 72% | 83% | 2,651,209 | 1,771 / 3,712 |
| pairing: cross-language | 779 | 0.849 | 0.96 / 0.78 / 0.81 | 0 | 60% | 87% | 72% | 84% | 1,751,116 | 1,913 / 3,850 |
| pairing: same-language | 413 | 0.798 | 0.88 / 0.77 / 0.74 | 0 | 54% | 95% | 71% | 81% | 900,093 | 1,503 / 3,249 |
| claim_language: de | 396 | 0.798 | 0.93 / 0.70 / 0.76 | 0 | 58% | 89% | 77% | 85% | 871,132 | 1,872 / 3,763 |
| claim_language: fr | 398 | 0.840 | 0.87 / 0.84 / 0.80 | 0 | 60% | 92% | 71% | 82% | 901,363 | 1,663 / 3,371 |
| claim_language: it | 398 | 0.856 | 0.98 / 0.77 / 0.81 | 0 | 54% | 88% | 67% | 82% | 878,714 | 1,779 / 4,002 |
| reference_language: de | 364 | 0.842 | 0.94 / 0.77 / 0.81 | 0 | 60% | 92% | 69% | 83% | 757,527 | 1,742 / 3,843 |
| reference_language: fr | 455 | 0.821 | 0.89 / 0.79 / 0.79 | 0 | 60% | 88% | 71% | 82% | 1,019,633 | 1,713 / 3,519 |
| reference_language: it | 373 | 0.836 | 0.97 / 0.76 / 0.78 | 0 | 53% | 89% | 75% | 83% | 874,049 | 1,869 / 3,662 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 361 | 18 | 18 |
| neutral | 0 | 285 | 114 |
| contradiction | 17 | 34 | 345 |
