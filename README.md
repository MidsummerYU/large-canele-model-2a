# booklet-nli — multilingual NLI over Swiss voting booklets with Apertus

Submission for **Hack Apertus, Track 2A, OST challenge**: given a claim and a Swiss federal voting booklet (German,
French or Italian, in any combination with the claim), decide whether the booklet supports, does not address or
contradicts the claim, and quote the deciding passage with its page. Built on Apertus 1.5 8B and 70B.

- Report: [`track_2a/technical_report.md`](track_2a/technical_report.md), PDF [`track_2a/LargeCaneleModel_Report.pdf`](track_2a/LargeCaneleModel_Report.pdf)
- Results per run: [`track_2a/results/`](track_2a/results/) (`summary.md`, `scores.json`, `predictions.jsonl`)
- Challenge rules: [`track_2a/README.md`](track_2a/README.md)

## Reproduce

Requirements: Docker and `make`. No API key, no GPU, no model weights.

```bash
cd track_2a
make run     # download the booklets once, replay every run in data/runs.yaml, check every score, rebuild figure and report
make test    # run the test suite in the same image
```

`make run` fails if a recomputed score differs from the committed one in `results/`.

## Predict

```bash
cp .env.example .env    # set LLM_API_KEY
make predict INPUT=cases.jsonl OUTPUT=predictions.jsonl
```

`cases.jsonl` holds one item per line in the challenge's input format. A beginner item gives the passage:
`{"id": "case-0043", "reference": {"text": "..."}, "claim": {"text": "..."}}`. An advanced item gives the booklet:
`{"id": "case-0042", "booklet": {"path": "booklets/2024_11_24_de.pdf"}, "vote": "...", "claim": {"text": "..."}}`,
with the path inside the repository so the container can read it. Each output line is
`{"id", "label", "label_name", "evidence": [{"page", "text"}], "metrics": {"input_tokens", "output_tokens", "inference_time_ms"}}`.
Without Docker: `uv run booklet-nli predict cases.jsonl predictions.jsonl --mode live`.

## How it works

1. **Beginner:** the passage and the claim go into `data/prompts/beginner.txt`; Apertus answers with a label and a
   quote in JSON.
2. **Advanced:** the PDF is split into pages with pypdf (cached as JSON next to it). If the claim is in another
   language than the booklet, Apertus 8B translates it for retrieval only. BM25 over the pages with the vote title
   and the claim picks the top pages (3 by default), which go into `data/prompts/advanced_v2.txt` marked
   `[Page N]`; Apertus answers with a label, a page and a quote. The original claim is what the model judges.
3. **Evidence grounding:** each part of the model's quote is matched to the most similar span of the passage or the
   given pages; if the similarity reaches `evidence_min_similarity` the output evidence is that span, verbatim, with its page,
   otherwise the model's quote. A reply that names no label counts as neutral. The translation call is included in
   the reported tokens and time.
4. **Recording:** every call is stored in `data/recordings/` under a hash of the full request, with the answer,
   token usage and latency. Replays never touch the network.
5. **Evaluation:** `booklet-nli evaluate` scores a split of the public set (macro-F1, per-class F1, quote and
   evidence verbatim, evidence page among the gold pages, retrieval hit, tokens, latency mean and p95, by language);
   `booklet-nli reproduce` runs every entry of `data/runs.yaml` and then rebuilds the figure and the report.

## Layout

| Path (under `track_2a/`) | Contents |
|---|---|
| `src/booklet_nli/` | `data` (cases, split), `booklets` (download, checksums), `pages` (page text, gold pages), `retrieve` (language id, BM25, translation), `nli` (reply parsing), `evidence` (grounding quotes in the source), `predict`, `score`, `client` (recording), `runs`, `cli`, `figures`, `technical_report`, `pdf` |
| `data/ost/` | OST public set v1.1 (MIT), booklet checksums, gold pages located in the PDFs |
| `data/prompts/` | prompt templates |
| `data/runs.yaml` | every experiment: task, model, split, pages, prompt |
| `data/recordings/` | recorded model calls |
| `data/booklets/` | download cache, not committed |
| `results/` | per run: summary, scores, predictions in the challenge format |
| `docs/` | report template and figure |

## Extend it

- **A new experiment:** add a line to `data/runs.yaml` and run `uv run booklet-nli reproduce --mode live --update`.
- **A new prompt:** add `data/prompts/<name>.txt` with the same placeholders and use `prompt: <name>` in a run.
- **Another model or endpoint:** set `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_NAME`, or name the model in a run.

## Configuration

Settings are read from the environment or `track_2a/.env` (names from the Hack Apertus template: `LLM_NAME`,
`LLM_BASE_URL`, `LLM_API_KEY`). Every setting and its default is declared once in `track_2a/src/booklet_nli/config.py`.

## License

Code: Apache-2.0 ([LICENSE](LICENSE)). Report and documentation: CC-BY-4.0. The OST dataset is MIT; the booklets
are downloaded from the Swiss Federal Chancellery at run time and not redistributed.
