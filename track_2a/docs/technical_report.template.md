# Technical report — Less is more: multilingual NLI over Swiss voting booklets with Apertus

- **Track:** Track 2A — OST: Multilingual Natural Language Inference over Swiss Official Voting Booklets
- **Event:** Online
- **Team:** Large Canelé Model — Yumeng Ye
- **Demo:** `make run` replays every experiment; `make predict INPUT=… OUTPUT=…` runs the CLI on the challenge's input format

## 1. Summary

Given a claim and a federal voting booklet, the system labels the claim as entailed, neutral or contradicted and quotes the deciding passage with its page. On the held-out {test} claims of the public set, Apertus 1.5 8B reaches macro-F1 **{o[8B/beginner-test][macro_f1]:.3f}** when the reference passage is given (beginner) and **{o[8B/advanced-p3-advanced_v2-test][macro_f1]:.3f}** from the whole PDF (advanced), with **{tpc[8B/advanced-p3-advanced_v2-test]:,.0f}** input tokens per claim; Apertus 70B is less accurate on the beginner task ({o[70B/beginner-test][macro_f1]:.3f}) and no more accurate on the advanced task ({o[70B/advanced-p3-advanced_v2-test][macro_f1]:.3f}, within the bootstrap interval of the difference) while taking {slower[advanced-p3-advanced_v2-test]:.1f} times as long, so the final system uses 8B. A matching step in code replaces each quote by the booklet text it paraphrases, so that {o[8B/advanced-p3-advanced_v2-test][evidence_verbatim]:.0%} of the advanced evidence is verbatim booklet text (the model's own quotes: {o[8B/advanced-p3-advanced_v2-test][quote_verbatim]:.0%}) at no extra tokens. The challenge asks whether less context can keep NLI reliable. In our measurements less context is *more* reliable: giving the model the whole booklet (≈{tpc[8B/advanced-full-advanced-dev]:,.0f} tokens) drops macro-F1 to {o[8B/advanced-full-advanced-dev][macro_f1]:.3f} on the dev set, against {o[8B/advanced-p3-advanced-dev][macro_f1]:.3f} with three retrieved pages, at {full_ratio:.0f} times the tokens.

## 2. Architecture

```
beginner:  reference passage + claim ─────────────────────────────────────► Apertus (JSON: label, evidence)
advanced:  booklet PDF ─► pages (pypdf) ─► language of booklet and claim
                              │              └─ different? Apertus 8B translates the claim (retrieval only)
                              └─► BM25 over pages (vote title + claim) ─► top 3 pages, marked "[Page N]"
                                                                           └─► Apertus (JSON: label, page, evidence)
both:      each quote matched to the closest span of the passage or the pages ─► that span, if similar enough
           ─► challenge output with evidence, page, token counts and time
```

Everything runs in one Python package (`booklet_nli`) with a CLI: `predict` reads the challenge's beginner or advanced input format and writes its output format; `evaluate` scores a split of the public set; `reproduce` replays every experiment in `data/runs.yaml`. Every model call goes through a recording client that stores the response, token usage and latency under a hash of the full request, so all results can be replayed without an API key.

## 3. Use of Apertus

- **Model:** `swiss-ai/Apertus-v1.5-8B` and `swiss-ai/Apertus-v1.5-70B`
- **How it is used:** inference (zero-shot NLI with a JSON answer) and claim translation for retrieval
- **Where it runs:** hosted endpoint, CSCS Inference Service (`{endpoint}`), chat completions with the server-side chat template, no system prompt, temperature {settings.temperature}, at most {settings.max_tokens} output tokens

The prompts are plain text files in `data/prompts/`. Each defines the three labels, tells the model to use only the given text even when it knows the facts, warns that claim and text may be in different languages, and asks for JSON only. The advanced prompt `advanced_v2` adds a point-by-point comparison of numbers, dates, recommendations, effects and negations, because the base prompt let contradictions pass as neutral. A reply that names no label falls back to neutral: asserting support or contradiction without evidence is the worse error.

**Evidence grounding.** Apertus rarely quotes character for character: it rewrites numbers ("10100" for "10 100"), drops soft hyphens and words split across lines, or changes a word. After the reply, code splits the quote at any ellipsis, finds for each part the most similar span of the passage or of the given pages (anchored on the longest common run of words, then grown or shrunk word by word, scored with `difflib`'s similarity ratio), and outputs that span with its page if the similarity is at least {settings.evidence_min_similarity}; the cited page wins a tie. Otherwise the model's quote is kept. The threshold was chosen on the dev set, where results barely change between 0.8 and 0.9; below it, matches are mostly quotes translated into the claim's language or stitched from several places. Grounding never changes a label and costs no model call. Claude (Anthropic) assisted with writing the code and this report; it played no part in predictions or scoring.

## 4. Data

- **Claims:** the OST public set v1.1 ({cases} claims, MIT licence, `data/ost/`), {cross:.0%} cross-language. A seeded split stratified by label and language pair gives {dev} dev claims, used for every design decision, and {test} test claims, scored once per final configuration.
- **Booklets:** {booklets} PDFs ({booklet_mb:.0f} MB, a median of {pages_median:.0f} pages) downloaded at run time from the Federal Chancellery and checked against SHA-256 sums in `data/ost/booklets.json`; they are not redistributed because `data/` is limited to 100 MB.
- **Gold pages:** the public set gives reference passages but no page numbers. We place each passage on its pages by matching its sentences against the page text; {located:.0%} of the passages are located (`data/ost/gold_pages.jsonl`). Long passages span several pages, so "a gold page" means any page holding part of the passage.
- No personal data is involved.

## 5. Evaluation

Macro-F1 over the three labels is the primary metric, with per-class F1, evidence verbatim (share of entailment and contradiction answers whose output evidence is found in the passage or on its page; the same share for the model's own quote is "quote verbatim"), evidence page (share of those answers citing a gold page), retrieval hit (share of contexts containing a gold page), input tokens and latency mean and p95.

**Final configurations, test set ({test} claims):**

| Task | Model | Macro-F1 | F1 entail / neutral / contra | Verbatim: quote → evidence | Evidence page | Tokens per claim | Latency mean / p95 |
|---|---|---|---|---|---|---|---|
| beginner | 8B | {o[8B/beginner-test][macro_f1]:.3f} | {o[8B/beginner-test][f1][entailment]:.2f} / {o[8B/beginner-test][f1][neutral]:.2f} / {o[8B/beginner-test][f1][contradiction]:.2f} | {o[8B/beginner-test][quote_verbatim]:.0%} → {o[8B/beginner-test][evidence_verbatim]:.0%} | – | {tpc[8B/beginner-test]:,.0f} | {o[8B/beginner-test][latency_mean_ms]:,.0f} / {o[8B/beginner-test][latency_p95_ms]:,.0f} ms |
| beginner | 70B | {o[70B/beginner-test][macro_f1]:.3f} | {o[70B/beginner-test][f1][entailment]:.2f} / {o[70B/beginner-test][f1][neutral]:.2f} / {o[70B/beginner-test][f1][contradiction]:.2f} | {o[70B/beginner-test][quote_verbatim]:.0%} → {o[70B/beginner-test][evidence_verbatim]:.0%} | – | {tpc[70B/beginner-test]:,.0f} | {o[70B/beginner-test][latency_mean_ms]:,.0f} / {o[70B/beginner-test][latency_p95_ms]:,.0f} ms |
| advanced, 3 pages | 8B | {o[8B/advanced-p3-advanced_v2-test][macro_f1]:.3f} | {o[8B/advanced-p3-advanced_v2-test][f1][entailment]:.2f} / {o[8B/advanced-p3-advanced_v2-test][f1][neutral]:.2f} / {o[8B/advanced-p3-advanced_v2-test][f1][contradiction]:.2f} | {o[8B/advanced-p3-advanced_v2-test][quote_verbatim]:.0%} → {o[8B/advanced-p3-advanced_v2-test][evidence_verbatim]:.0%} | {o[8B/advanced-p3-advanced_v2-test][evidence_page_hit]:.0%} | {tpc[8B/advanced-p3-advanced_v2-test]:,.0f} | {o[8B/advanced-p3-advanced_v2-test][latency_mean_ms]:,.0f} / {o[8B/advanced-p3-advanced_v2-test][latency_p95_ms]:,.0f} ms |
| advanced, 3 pages | 70B | {o[70B/advanced-p3-advanced_v2-test][macro_f1]:.3f} | {o[70B/advanced-p3-advanced_v2-test][f1][entailment]:.2f} / {o[70B/advanced-p3-advanced_v2-test][f1][neutral]:.2f} / {o[70B/advanced-p3-advanced_v2-test][f1][contradiction]:.2f} | {o[70B/advanced-p3-advanced_v2-test][quote_verbatim]:.0%} → {o[70B/advanced-p3-advanced_v2-test][evidence_verbatim]:.0%} | {o[70B/advanced-p3-advanced_v2-test][evidence_page_hit]:.0%} | {tpc[70B/advanced-p3-advanced_v2-test]:,.0f} | {o[70B/advanced-p3-advanced_v2-test][latency_mean_ms]:,.0f} / {o[70B/advanced-p3-advanced_v2-test][latency_p95_ms]:,.0f} ms |

Token counts include the translation call, since the organisers count tokens at a proxy.

**Is 8B really better?** A paired bootstrap ({settings.bootstrap_samples} resamples of the test claims, {settings.confidence:.0%} intervals) gives macro-F1 8B [{ci[beginner-test][first][0]:.3f}, {ci[beginner-test][first][1]:.3f}] and 70B [{ci[beginner-test][second][0]:.3f}, {ci[beginner-test][second][1]:.3f}] on the beginner task, a difference 8B − 70B of [{ci[beginner-test][difference][0]:+.3f}, {ci[beginner-test][difference][1]:+.3f}]; on the advanced task the difference is [{ci[advanced-p3-advanced_v2-test][difference][0]:+.3f}, {ci[advanced-p3-advanced_v2-test][difference][1]:+.3f}]. The beginner gap is real; on the advanced task the two models are equally accurate, and 70B takes {slower[advanced-p3-advanced_v2-test]:.1f} times as long.

**How much context is enough? Dev set ({dev} claims):**

![Macro-F1 against input tokens](docs/figures/tradeoff_dev.svg)

*Figure 1. Advanced task, dev set: macro-F1 against mean input tokens per claim. The line is Apertus 8B with the base prompt and 3, 5 or 8 retrieved pages or the whole booklet; the dashed line is the beginner score with the gold passage given.*

| Context (8B, base prompt) | Macro-F1 | F1 contradiction | Retrieval hit | Evidence page | Tokens per claim | Latency mean |
|---|---|---|---|---|---|---|
| 3 pages | {o[8B/advanced-p3-advanced-dev][macro_f1]:.3f} | {o[8B/advanced-p3-advanced-dev][f1][contradiction]:.2f} | {o[8B/advanced-p3-advanced-dev][retrieval_hit]:.0%} | {o[8B/advanced-p3-advanced-dev][evidence_page_hit]:.0%} | {tpc[8B/advanced-p3-advanced-dev]:,.0f} | {o[8B/advanced-p3-advanced-dev][latency_mean_ms]:,.0f} ms |
| 5 pages | {o[8B/advanced-p5-advanced-dev][macro_f1]:.3f} | {o[8B/advanced-p5-advanced-dev][f1][contradiction]:.2f} | {o[8B/advanced-p5-advanced-dev][retrieval_hit]:.0%} | {o[8B/advanced-p5-advanced-dev][evidence_page_hit]:.0%} | {tpc[8B/advanced-p5-advanced-dev]:,.0f} | {o[8B/advanced-p5-advanced-dev][latency_mean_ms]:,.0f} ms |
| 8 pages | {o[8B/advanced-p8-advanced-dev][macro_f1]:.3f} | {o[8B/advanced-p8-advanced-dev][f1][contradiction]:.2f} | {o[8B/advanced-p8-advanced-dev][retrieval_hit]:.0%} | {o[8B/advanced-p8-advanced-dev][evidence_page_hit]:.0%} | {tpc[8B/advanced-p8-advanced-dev]:,.0f} | {o[8B/advanced-p8-advanced-dev][latency_mean_ms]:,.0f} ms |
| whole booklet (baseline) | {o[8B/advanced-full-advanced-dev][macro_f1]:.3f} | {o[8B/advanced-full-advanced-dev][f1][contradiction]:.2f} | {o[8B/advanced-full-advanced-dev][retrieval_hit]:.0%} | {o[8B/advanced-full-advanced-dev][evidence_page_hit]:.0%} | {tpc[8B/advanced-full-advanced-dev]:,.0f} | {o[8B/advanced-full-advanced-dev][latency_mean_ms]:,.0f} ms |

Four findings decided the final design:

1. **Fewer pages are better, not just cheaper.** More pages raise the chance that a gold page is in the context (retrieval hit) but lower macro-F1: extra pages on other votes or other aspects of the same vote distract the model, and with the whole booklet it misses most contradictions.
2. **Cross-language retrieval needs translation.** BM25 matches words, and {cross:.0%} of the claims are in another language than their booklet. Translating the claim into the booklet's language before retrieval raised the dev share of cross-language claims with a gold page in the top {recall_k} from {recall[cross][plain]:.0%} to {recall[cross][translated]:.0%} (same-language claims: {recall[same][plain]:.0%}).
3. **A point-by-point prompt helps the small model.** With three pages, the `advanced_v2` prompt lifts Apertus 8B from {o[8B/advanced-p3-advanced-dev][macro_f1]:.3f} to {o[8B/advanced-p3-advanced_v2-dev][macro_f1]:.3f} (contradiction F1 {o[8B/advanced-p3-advanced-dev][f1][contradiction]:.2f} → {o[8B/advanced-p3-advanced_v2-dev][f1][contradiction]:.2f}); Apertus 70B goes from {o[70B/advanced-p3-advanced-dev][macro_f1]:.3f} to {o[70B/advanced-p3-advanced_v2-dev][macro_f1]:.3f}.

4. **The larger model over-reads contradictions.** On the dev set Apertus 70B was ahead on the advanced task, but on the larger test set ({test} claims) it labels {r[70B/advanced-p3-advanced_v2-test][all][all][confusion][neutral][contradiction]} of the {gold_count[70B/advanced-p3-advanced_v2-test][neutral]} neutral claims as contradictions (8B: {r[8B/advanced-p3-advanced_v2-test][all][all][confusion][neutral][contradiction]}), and on the beginner task {r[70B/beginner-test][all][all][confusion][neutral][contradiction]} (8B: {r[8B/beginner-test][all][all][confusion][neutral][contradiction]}): it treats a booklet that does not mention something as a booklet that denies it.

**By language, test set, advanced 8B:** same-language {r[8B/advanced-p3-advanced_v2-test][pairing][same-language][macro_f1]:.3f}, cross-language {r[8B/advanced-p3-advanced_v2-test][pairing][cross-language][macro_f1]:.3f}; booklet in German {r[8B/advanced-p3-advanced_v2-test][reference_language][de][macro_f1]:.3f}, French {r[8B/advanced-p3-advanced_v2-test][reference_language][fr][macro_f1]:.3f}, Italian {r[8B/advanced-p3-advanced_v2-test][reference_language][it][macro_f1]:.3f}.

## 6. Limitations

- **Test set.** The organisers' test set is not public; our test numbers come from a held-out part of the public set, which shares booklets and votes with the dev part.
- **Gold pages are approximate.** They come from sentence matching; a passage split over pages counts every page it touches.
- **Evidence quality.** After grounding, {o[8B/advanced-p3-advanced_v2-test][evidence_verbatim]:.0%} of the 8B advanced evidence is verbatim; the rest are mostly quotes the model translated into the claim's language or stitched from table cells, which string similarity cannot match. Verbatim text is not proof of relevance: {o[8B/advanced-p3-advanced_v2-test][evidence_page_hit]:.0%} of the answers cite a gold page.
- **Latency** was measured on the shared CSCS endpoint and includes queueing; the translation step adds a second call for cross-language claims.
- **Retrieval misses.** With three pages, {o[8B/advanced-p3-advanced_v2-test][retrieval_hit]:.0%} of the test contexts contain a gold page; the rest are decided without the evidence.

## 7. Reproducibility

- **Run:** `make run` (Docker, no API key, CPU only) downloads the booklets once, replays the recorded calls in `data/recordings/` for every run in `data/runs.yaml`, recomputes the scores and fails if one differs from `results/`. `make test` runs the tests.
- **Predict:** `make predict INPUT=cases.jsonl OUTPUT=predictions.jsonl` with `LLM_API_KEY` in `.env` (advanced inputs need the booklet path inside the repository). The default is the final configuration: 3 pages and `advanced_v2`.
- **Determinism:** temperature 0 on the endpoint; replays are exact. Recordings store a summary of each request instead of the prompt, to stay within the 100 MB limit of `data/`; the hash still checks that the prompt is unchanged.

## 8. Next steps

Hybrid retrieval with multilingual embeddings instead of translation, a reranker that chooses pages per claim instead of a fixed three, translating cross-language quotes back before grounding them, retrieval over page images for tables, and a small fine-tuned Apertus 8B for the contradiction cases.

## License

Creative Commons Attribution 4.0 (CC-BY-4.0). Code: Apache-2.0. OST dataset: MIT.

## References

- OST, *MNLI over Swiss Voting Booklets*, Hugging Face dataset, v1.1. https://huggingface.co/datasets/OSTswiss/MNLIoverSwissVotingBooklets
- Robertson and Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond*, 2009.
- Swiss Federal Chancellery, explanatory booklets for federal votes. https://www.bk.admin.ch
