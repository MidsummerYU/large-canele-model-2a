# beginner-dev · swiss-ai/Apertus-v1.5-70B

| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| all: all | 296 | 0.887 | 0.98 / 0.83 / 0.85 | 0 | 76% | – | – | 613,791 | 1,389 / 3,337 |
| pairing: cross-language | 194 | 0.917 | 0.97 / 0.89 / 0.89 | 0 | 77% | – | – | 401,118 | 1,323 / 3,012 |
| pairing: same-language | 102 | 0.829 | 1.00 / 0.72 / 0.77 | 0 | 74% | – | – | 212,673 | 1,513 / 3,890 |
| claim_language: de | 99 | 0.898 | 0.99 / 0.85 / 0.86 | 0 | 75% | – | – | 197,615 | 1,457 / 3,684 |
| claim_language: fr | 99 | 0.898 | 0.97 / 0.86 / 0.86 | 0 | 80% | – | – | 216,487 | 1,444 / 4,249 |
| claim_language: it | 98 | 0.865 | 0.98 / 0.78 / 0.83 | 0 | 74% | – | – | 199,689 | 1,264 / 3,296 |
| reference_language: de | 91 | 0.843 | 0.95 / 0.79 / 0.78 | 0 | 76% | – | – | 191,674 | 1,552 / 4,703 |
| reference_language: fr | 114 | 0.955 | 1.00 / 0.93 / 0.94 | 0 | 78% | – | – | 218,600 | 1,203 / 2,522 |
| reference_language: it | 91 | 0.846 | 0.98 / 0.75 / 0.81 | 0 | 74% | – | – | 203,517 | 1,458 / 3,890 |

Confusion (rows gold, columns predicted):

| | entailment | neutral | contradiction |
|---|---|---|---|
| entailment | 98 | 0 | 0 |
| neutral | 0 | 72 | 27 |
| contradiction | 4 | 2 | 93 |
