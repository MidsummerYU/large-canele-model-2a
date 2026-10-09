# Technical report — Less is more: multilingual NLI over Swiss voting booklets with Apertus

- **Track:** Track 2A — OST: Multilingual Natural Language Inference over Swiss Official Voting Booklets
- **Event:** Online
- **Team:** Large Canelé Model — Yumeng Ye
- **Demo:** `make run` replays every experiment; `make predict INPUT=… OUTPUT=…` runs the CLI on the challenge's input format

## 1. Summary

Given a claim and a federal voting booklet, the system labels the claim as entailed, neutral or contradicted and quotes the deciding passage with its page. On the held-out 1192 claims of the public set, Apertus 1.5 8B reaches macro-F1 **0.934** when the reference passage is given (beginner) and **0.846** from the whole PDF (advanced), with **2,224** input tokens per claim; Apertus 70B is both slower and less accurate on both tasks (0.870 and 0.832), so the final system uses 8B. The challenge asks whether less context can keep NLI reliable. In our measurements less context is *more* reliable: giving the model the whole booklet (≈36,440 tokens) drops macro-F1 to 0.578 on the dev set, against 0.834 with three retrieved pages, at 18 times the tokens.

## 2. Architecture

```
beginner:  reference passage + claim ─────────────────────────────────────► Apertus (JSON: label, evidence)
advanced:  booklet PDF ─► pages (pypdf) ─► language of booklet and claim
                              │              └─ different? Apertus 8B translates the claim (retrieval only)
                              └─► BM25 over pages (vote title + claim) ─► top 3 pages, marked "[Page N]"
                                                                           └─► Apertus (JSON: label, page, evidence)
both:      evidence checked verbatim against the passage or the cited page ─► challenge output with token counts and time
```

Everything runs in one Python package (`booklet_nli`) with a CLI: `predict` reads the challenge's beginner or advanced input format and writes its output format; `evaluate` scores a split of the public set; `reproduce` replays every experiment in `data/runs.yaml`. Every model call goes through a recording client that stores the response, token usage and latency under a hash of the full request, so all results can be replayed without an API key.

## 3. Use of Apertus

- **Model:** `swiss-ai/Apertus-v1.5-8B` and `swiss-ai/Apertus-v1.5-70B`
- **How it is used:** inference (zero-shot NLI with a JSON answer) and claim translation for retrieval
- **Where it runs:** hosted endpoint, CSCS Inference Service (`https://api.inference.cscs.ch/v1`), chat completions with the server-side chat template, no system prompt, temperature 0.0, at most 400 output tokens

The prompts are plain text files in `data/prompts/`. Each defines the three labels, tells the model to use only the given text even when it knows the facts, warns that claim and text may be in different languages, and asks for JSON only. The advanced prompt `advanced_v2` adds a point-by-point comparison of numbers, dates, recommendations, effects and negations, because the base prompt let contradictions pass as neutral. A reply that names no label falls back to neutral: asserting support or contradiction without evidence is the worse error. Claude (Anthropic) assisted with writing the code and this report; it played no part in predictions or scoring.

## 4. Data

- **Claims:** the OST public set v1.1 (1488 claims, MIT licence, `data/ost/`), 65% cross-language. A seeded split stratified by label and language pair gives 296 dev claims, used for every design decision, and 1192 test claims, scored once per final configuration.
- **Booklets:** 60 PDFs (76 MB, a median of 52 pages) downloaded at run time from the Federal Chancellery and checked against SHA-256 sums in `data/ost/booklets.json`; they are not redistributed because `data/` is limited to 100 MB.
- **Gold pages:** the public set gives reference passages but no page numbers. We place each passage on its pages by matching its sentences against the page text; 100% of the passages are located (`data/ost/gold_pages.jsonl`). Long passages span several pages, so "a gold page" means any page holding part of the passage.
- No personal data is involved.

## 5. Evaluation

Macro-F1 over the three labels is the primary metric, with per-class F1, evidence quoted verbatim (share of entailment and contradiction answers whose evidence is found in the passage or on the cited page), evidence page (share of those answers citing a gold page), retrieval hit (share of contexts containing a gold page), input tokens and latency mean and p95.

**Final configurations, test set (1192 claims):**

| Task | Model | Macro-F1 | F1 entail / neutral / contra | Evidence verbatim | Evidence page | Tokens per claim | Latency mean / p95 |
|---|---|---|---|---|---|---|---|
| beginner | 8B | 0.934 | 0.96 / 0.95 / 0.89 | 74% | – | 2,003 | 522 / 1,135 ms |
| beginner | 70B | 0.870 | 0.99 / 0.79 / 0.83 | 74% | – | 2,003 | 1,297 / 3,172 ms |
| advanced, 3 pages | 8B | 0.846 | 0.90 / 0.85 / 0.79 | 39% | 67% | 2,224 | 805 / 1,658 ms |
| advanced, 3 pages | 70B | 0.832 | 0.93 / 0.77 / 0.79 | 42% | 71% | 2,224 | 1,771 / 3,712 ms |

Token counts include the translation call, since the organisers count tokens at a proxy.

**How much context is enough? Dev set (296 claims):**

![Macro-F1 against input tokens](docs/figures/tradeoff_dev.svg)

*Figure 1. Advanced task, dev set: macro-F1 against mean input tokens per claim. The line is Apertus 8B with the base prompt and 3, 5 or 8 retrieved pages or the whole booklet; the dashed line is the beginner score with the gold passage given.*

| Context (8B, base prompt) | Macro-F1 | F1 contradiction | Retrieval hit | Evidence page | Tokens per claim | Latency mean |
|---|---|---|---|---|---|---|
| 3 pages | 0.834 | 0.75 | 83% | 72% | 2,052 | 823 ms |
| 5 pages | 0.829 | 0.73 | 95% | 72% | 2,953 | 922 ms |
| 8 pages | 0.817 | 0.71 | 100% | 66% | 4,250 | 2,472 ms |
| whole booklet (baseline) | 0.578 | 0.24 | 100% | 46% | 36,440 | 15,954 ms |

Four findings decided the final design:

1. **Fewer pages are better, not just cheaper.** More pages raise the chance that a gold page is in the context (retrieval hit) but lower macro-F1: extra pages on other votes or other aspects of the same vote distract the model, and with the whole booklet it misses most contradictions.
2. **Cross-language retrieval needs translation.** BM25 matches words, and 65% of the claims are in another language than their booklet. Translating the claim into the booklet's language before retrieval raised the dev share of cross-language claims with a gold page in the top 5 from 63% to 97% (same-language claims: 92%).
3. **A point-by-point prompt helps the small model.** With three pages, the `advanced_v2` prompt lifts Apertus 8B from 0.834 to 0.850 (contradiction F1 0.75 → 0.80); Apertus 70B goes from 0.866 to 0.869.

4. **The larger model over-reads contradictions.** On the dev set Apertus 70B was ahead on the advanced task, but on the larger test set (1192 claims) it labels 114 of the 399 neutral claims as contradictions (8B: 29), and on the beginner task 135 (8B: 4): it treats a booklet that does not mention something as a booklet that denies it.

**By language, test set, advanced 8B:** same-language 0.847, cross-language 0.846; booklet in German 0.808, French 0.841, Italian 0.890.

## 6. Limitations

- **Test set.** The organisers' test set is not public; our test numbers come from a held-out part of the public set, which shares booklets and votes with the dev part.
- **Gold pages are approximate.** They come from sentence matching; a passage split over pages counts every page it touches.
- **Evidence quality.** With retrieved pages the model often paraphrases or translates instead of quoting; evidence is verbatim for 39% of the 8B advanced answers. A second pass that picks the closest sentence on the cited page would raise this.
- **Latency** was measured on the shared CSCS endpoint and includes queueing; the translation step adds a second call for cross-language claims.
- **Retrieval misses.** With three pages, 83% of the test contexts contain a gold page; the rest are decided without the evidence.

## 7. Reproducibility

- **Run:** `make run` (Docker, no API key, CPU only) downloads the booklets once, replays the recorded calls in `data/recordings/` for every run in `data/runs.yaml`, recomputes the scores and fails if one differs from `results/`. `make test` runs the tests.
- **Predict:** `make predict INPUT=cases.jsonl OUTPUT=predictions.jsonl` with `LLM_API_KEY` in `.env` (advanced inputs need the booklet path inside the repository). The default is the final configuration: 3 pages and `advanced_v2`.
- **Determinism:** temperature 0 on the endpoint; replays are exact. Recordings store a summary of each request instead of the prompt, to stay within the 100 MB limit of `data/`; the hash still checks that the prompt is unchanged.

## 8. Next steps

Hybrid retrieval with multilingual embeddings instead of translation, a reranker that chooses pages per claim instead of a fixed three, a second pass to quote the evidence exactly, retrieval over page images for tables, and a small fine-tuned Apertus 8B for the contradiction cases.

## License

Creative Commons Attribution 4.0 (CC-BY-4.0). Code: Apache-2.0. OST dataset: MIT.

## References

- OST, *MNLI over Swiss Voting Booklets*, Hugging Face dataset, v1.1. https://huggingface.co/datasets/OSTswiss/MNLIoverSwissVotingBooklets
- Robertson and Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond*, 2009.
- Swiss Federal Chancellery, explanatory booklets for federal votes. https://www.bk.admin.ch
