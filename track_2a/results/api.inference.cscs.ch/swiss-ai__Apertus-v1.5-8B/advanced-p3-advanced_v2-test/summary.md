# advanced-p3-advanced_v2-test · swiss-ai/Apertus-v1.5-8B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | quote verbatim | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|
| all: all | 1192 | 0.846 | 0.90 / 0.85 / 0.79 | 1 | 51% | 88% | 68% | 83% | 2,651,209 | 805 / 1,658 |
| pairing: cross-language | 779 | 0.846 | 0.90 / 0.86 / 0.78 | 1 | 50% | 88% | 70% | 84% | 1,751,116 | 915 / 1,675 |
| pairing: same-language | 413 | 0.847 | 0.89 / 0.85 / 0.80 | 0 | 52% | 89% | 62% | 81% | 900,093 | 598 / 1,554 |
| claim_language: de | 396 | 0.818 | 0.86 / 0.85 / 0.75 | 1 | 51% | 92% | 70% | 85% | 871,132 | 859 / 1,735 |
| claim_language: fr | 398 | 0.838 | 0.85 / 0.86 / 0.80 | 0 | 52% | 88% | 67% | 82% | 901,363 | 789 / 1,581 |
| claim_language: it | 398 | 0.883 | 0.97 / 0.86 / 0.82 | 0 | 50% | 85% | 65% | 82% | 878,714 | 768 / 1,560 |
| reference_language: de | 364 | 0.808 | 0.90 / 0.80 / 0.72 | 0 | 47% | 89% | 66% | 83% | 757,527 | 797 / 1,842 |
| reference_language: fr | 455 | 0.841 | 0.87 / 0.85 / 0.81 | 0 | 54% | 88% | 67% | 82% | 1,019,633 | 779 / 1,513 |
| reference_language: it | 373 | 0.890 | 0.92 / 0.92 / 0.83 | 1 | 51% | 88% | 69% | 83% | 874,049 | 846 / 1,717 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 355 | 25 | 17 |
| neutral | 2 | 368 | 29 |
| contradiction | 39 | 69 | 288 |
