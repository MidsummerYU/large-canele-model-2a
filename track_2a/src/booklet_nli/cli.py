import argparse
import json
from pathlib import Path

from booklet_nli.config import Settings
from booklet_nli.data import beginner_input, load_cases, split
from booklet_nli.predict import Prediction, predict_all
from booklet_nli.score import Scores, breakdown

OUTPUT_EXCLUDE = {"parsed", "evidence_verbatim"}


def _summary(table: dict[str, dict[str, Scores]], title: str) -> str:
    lines = [f"# {title}", "", "| group | n | macro-F1 | F1 entail / neutral / contra | unparsed | evidence verbatim | input tokens | latency mean / p95 ms |", "|---|---|---|---|---|---|---|---|"]
    for field, by_name in table.items():
        for name, s in by_name.items():
            f1 = " / ".join(f"{v:.2f}" for v in s.f1.values())
            lines.append(
                f"| {field}: {name} | {s.n} | {s.macro_f1:.3f} | {f1} | {s.unparsed} | {s.evidence_verbatim:.0%} "
                f"| {s.input_tokens:,} | {s.latency_mean_ms:,.0f} / {s.latency_p95_ms:,.0f} |"
            )
    confusion = table["all"]["all"].confusion
    lines += ["", "Confusion (rows gold, columns predicted):", "", "| | " + " | ".join(confusion) + " |", "|---|" + "---|" * len(confusion)]
    lines += [f"| {gold} | " + " | ".join(str(n) for n in row.values()) + " |" for gold, row in confusion.items()]
    return "\n".join(lines) + "\n"


def _write_predictions(predictions: list[Prediction], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for p in predictions:
            f.write(json.dumps(p.model_dump(exclude=OUTPUT_EXCLUDE, exclude_none=True), ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(prog="booklet-nli", description="NLI of claims against Swiss voting booklets.")
    commands = parser.add_subparsers(dest="command", required=True)
    predict_parser = commands.add_parser("predict", help="predict labels for an input file in the challenge format")
    predict_parser.add_argument("input", type=Path)
    predict_parser.add_argument("output", type=Path)
    evaluate_parser = commands.add_parser("evaluate", help="predict and score a split of the public dataset")
    evaluate_parser.add_argument("--split", choices=["dev", "test"], default="dev")
    for sub in (predict_parser, evaluate_parser):
        sub.add_argument("--mode", choices=["live", "replay"], default="replay", help="replay never calls the API")
        sub.add_argument("--model", help="overrides LLM_NAME")
        sub.add_argument("--prompt", type=Path, help="prompt template; default data/prompts/beginner.txt")
    args = parser.parse_args()

    overrides = {"model": args.model} if args.model else {}
    settings = Settings(**overrides)
    prompt = (args.prompt or settings.beginner_prompt).read_text(encoding="utf-8")

    if args.command == "predict":
        with args.input.open(encoding="utf-8") as f:
            items = [json.loads(line) for line in f if line.strip()]
        _write_predictions(predict_all(items, settings, args.mode, prompt), args.output)
        print(f"wrote {args.output}")
        return

    cases = split(load_cases(settings.dataset), settings.dev_share, settings.split_seed)[args.split]
    predictions = predict_all([beginner_input(c) for c in cases], settings, args.mode, prompt)
    out_dir = settings.results_dir / settings.run_dir() / f"beginner-{args.split}"
    _write_predictions(predictions, out_dir / "predictions.jsonl")
    table = breakdown(cases, predictions)
    (out_dir / "scores.json").write_text(json.dumps({f: {n: s.model_dump() for n, s in by.items()} for f, by in table.items()}, indent=2) + "\n", encoding="utf-8")
    summary = _summary(table, f"Beginner · {args.split} · {settings.model}")
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    print(summary)
