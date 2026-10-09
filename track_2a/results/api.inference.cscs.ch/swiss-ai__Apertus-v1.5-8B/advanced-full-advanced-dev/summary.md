# advanced-full-advanced-dev · swiss-ai/Apertus-v1.5-8B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.578 | 0.71 / 0.78 / 0.24 | 0 | 17% | 46% | 100% | 10,786,344 | 15,954 / 22,133 |
| pairing: cross-language | 194 | 0.535 | 0.68 / 0.75 / 0.17 | 0 | 12% | 42% | 100% | 7,443,776 | 16,936 / 22,212 |
| pairing: same-language | 102 | 0.661 | 0.77 / 0.83 / 0.38 | 0 | 27% | 55% | 100% | 3,342,568 | 14,086 / 25,363 |
| claim_language: de | 99 | 0.575 | 0.70 / 0.83 / 0.20 | 0 | 9% | 33% | 100% | 3,550,828 | 31,915 / 303,694 |
| claim_language: fr | 99 | 0.624 | 0.75 / 0.77 / 0.36 | 0 | 18% | 53% | 100% | 3,256,439 | 6,938 / 13,426 |
| claim_language: it | 98 | 0.533 | 0.68 / 0.76 / 0.16 | 0 | 27% | 55% | 100% | 3,979,077 | 8,938 / 18,511 |
| reference_language: de | 91 | 0.515 | 0.72 / 0.71 / 0.12 | 0 | 13% | 54% | 100% | 3,002,456 | 13,642 / 20,051 |
| reference_language: fr | 114 | 0.546 | 0.70 / 0.74 / 0.20 | 0 | 15% | 52% | 100% | 4,330,395 | 21,728 / 29,036 |
| reference_language: it | 91 | 0.682 | 0.72 / 0.93 / 0.40 | 0 | 23% | 36% | 100% | 3,453,493 | 11,033 / 18,587 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 82 | 7 | 9 |
| neutral | 6 | 93 | 0 |
| contradiction | 45 | 39 | 15 |
