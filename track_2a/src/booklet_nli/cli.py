import argparse
import json
from pathlib import Path

from booklet_nli.config import Settings
from booklet_nli.booklets import booklet_file, fetch_booklets
from booklet_nli.data import Case, beginner_input, load_cases, split
from booklet_nli.pages import GoldPages
from booklet_nli.predict import Prediction, predict_all
from booklet_nli.runs import Manifest, run_settings
from booklet_nli.score import Scores, breakdown

OUTPUT_EXCLUDE = {"parsed", "evidence_verbatim", "context_pages"}


def _summary(table: dict[str, dict[str, Scores]], title: str) -> str:
    lines = [f"# {title}", "", "| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | evidence page | retrieval hit | input tokens | latency mean / p95 ms |", "|---|---|---|---|---|---|---|---|---|---|"]
    for field, by_name in table.items():
        for name, s in by_name.items():
            f1 = " / ".join(f"{v:.2f}" for v in s.f1.values())
            lines.append(
                f"| {field}: {name} | {s.n} | {s.macro_f1:.3f} | {f1} | {s.unparsed} | {s.evidence_verbatim:.0%} "
                f"| {_share(s.evidence_page_hit)} | {_share(s.retrieval_hit)} "
                f"| {s.input_tokens:,} | {s.latency_mean_ms:,.0f} / {s.latency_p95_ms:,.0f} |"
            )
    confusion = table["all"]["all"].confusion
    lines += ["", "Confusion (rows gold, columns predicted):", "", "| | " + " | ".join(confusion) + " |", "|---|" + "---|" * len(confusion)]
    lines += [f"| {gold} | " + " | ".join(str(n) for n in row.values()) + " |" for gold, row in confusion.items()]
    return "\n".join(lines) + "\n"


def _share(value: float | None) -> str:
    return "–" if value is None else f"{value:.0%}"


def advanced_input(case: Case, settings: Settings) -> dict:
    """The challenge's advanced input format, pointing at the cached booklet."""
    path = settings.booklets_dir / booklet_file(case.booklet_url)
    return {"id": case.id, "booklet": {"path": str(path)}, "vote": case.vote, "claim": {"text": case.claim}}


def _write_predictions(predictions: list[Prediction], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for p in predictions:
            f.write(json.dumps(p.model_dump(exclude=OUTPUT_EXCLUDE, exclude_none=True), ensure_ascii=False) + "\n")


class ScoresMismatchError(AssertionError):
    pass


def run_evaluation(settings: Settings, task: str, split_name: str, mode: str, prompts: dict[str, str], update: bool) -> Path:
    """Predict and score one split; unless `update`, the scores must equal the committed ones."""
    cases = split(load_cases(settings.dataset), settings.dev_share, settings.split_seed)[split_name]
    if task == "beginner":
        items, gold, run = [beginner_input(c) for c in cases], None, f"beginner-{split_name}"
    else:
        fetch_booklets(settings, [c.booklet_url for c in cases])
        items, gold = [advanced_input(c, settings) for c in cases], GoldPages.load(settings.gold_pages)
        context = "full" if settings.context_pages is None else f"p{settings.context_pages}"
        run = f"advanced-{context}-{settings.advanced_prompt.stem}-{split_name}"
    predictions = predict_all(items, settings, mode, prompts)
    out_dir = settings.results_dir / settings.run_dir() / run
    table = breakdown(cases, predictions, gold)
    document = json.dumps({f: {n: s.model_dump() for n, s in by.items()} for f, by in table.items()}, indent=2) + "\n"
    scores_path = out_dir / "scores.json"
    if scores_path.exists() and not update and scores_path.read_text(encoding="utf-8") != document:
        raise ScoresMismatchError(f"recomputed scores differ from {scores_path}; rerun with --update if the change is intended")
    _write_predictions(predictions, out_dir / "predictions.jsonl")
    scores_path.write_text(document, encoding="utf-8")
    (out_dir / "summary.md").write_text(_summary(table, f"{run} · {settings.model}"), encoding="utf-8")
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(prog="booklet-nli", description="NLI of claims against Swiss voting booklets.")
    commands = parser.add_subparsers(dest="command", required=True)
    predict_parser = commands.add_parser("predict", help="predict labels for an input file in the challenge format")
    predict_parser.add_argument("input", type=Path)
    predict_parser.add_argument("output", type=Path)
    evaluate_parser = commands.add_parser("evaluate", help="predict and score a split of the public dataset")
    evaluate_parser.add_argument("--split", choices=["dev", "test"], default="dev")
    evaluate_parser.add_argument("--task", choices=["beginner", "advanced"], default="beginner")
    reproduce_parser = commands.add_parser("reproduce", help="replay every run in data/runs.yaml and check the scores")
    reproduce_parser.add_argument("--mode", choices=["live", "replay"], default="replay", help="replay never calls the API")
    reproduce_parser.add_argument("--update", action="store_true", help="overwrite the committed scores instead of checking them")
    for sub in (predict_parser, evaluate_parser):
        sub.add_argument("--mode", choices=["live", "replay"], default="replay", help="replay never calls the API")
        sub.add_argument("--model", help="overrides LLM_NAME")
        context = sub.add_mutually_exclusive_group()
        context.add_argument("--pages", type=int, help="advanced task: retrieve this many pages (overrides LLM_CONTEXT_PAGES)")
        context.add_argument("--full", action="store_true", help="advanced task: give the whole booklet (the baseline)")
        sub.add_argument("--advanced-prompt", type=Path, help="advanced prompt template (overrides LLM_ADVANCED_PROMPT)")
    args = parser.parse_args()

    if args.command == "reproduce":
        # The manifest names every model, so LLM_NAME is not needed here.
        base = Settings(model="")
        manifest = Manifest.load(base.runs_manifest)
        for run in manifest.runs:
            settings = run_settings(base, manifest, run)
            prompts = {"beginner": settings.beginner_prompt.read_text(encoding="utf-8"), "advanced": settings.advanced_prompt.read_text(encoding="utf-8")}
            out_dir = run_evaluation(settings, run.task, run.split, args.mode, prompts, args.update)
            print(f"checked {out_dir.relative_to(base.results_dir)}")
        return

    overrides = {"model": args.model} if args.model else {}
    if args.full:
        overrides["context_pages"] = None
    elif args.pages:
        overrides["context_pages"] = args.pages
    if args.advanced_prompt:
        overrides["advanced_prompt"] = args.advanced_prompt
    settings = Settings(**overrides)
    prompts = {"beginner": settings.beginner_prompt.read_text(encoding="utf-8"), "advanced": settings.advanced_prompt.read_text(encoding="utf-8")}

    if args.command == "predict":
        with args.input.open(encoding="utf-8") as f:
            items = [json.loads(line) for line in f if line.strip()]
        _write_predictions(predict_all(items, settings, args.mode, prompts), args.output)
        print(f"wrote {args.output}")
        return

    out_dir = run_evaluation(settings, args.task, args.split, args.mode, prompts, update=True)
    print((out_dir / "summary.md").read_text(encoding="utf-8"))
