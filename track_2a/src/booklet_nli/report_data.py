import json
from pathlib import Path

from booklet_nli.config import Settings
from booklet_nli.runs import Manifest, run_name, run_settings


def model_label(model: str) -> str:
    return model.rsplit("-", 1)[-1]


def run_dirs(settings: Settings) -> dict[str, Path]:
    """"<model label>/<run name>" -> that run's results folder, for every run in the manifest."""
    manifest = Manifest.load(settings.runs_manifest)
    dirs = {}
    for run in manifest.runs:
        s = run_settings(settings, manifest, run)
        name = run_name(run.task, run.split, s)
        dirs[f"{model_label(run.model)}/{name}"] = s.results_dir / s.run_dir() / name
    return dirs


def all_scores(settings: Settings) -> dict[str, dict]:
    return {key: json.loads((d / "scores.json").read_text(encoding="utf-8")) for key, d in run_dirs(settings).items()}


def predicted_labels(run_dir: Path) -> dict[str, int]:
    with (run_dir / "predictions.jsonl").open(encoding="utf-8") as f:
        return {row["id"]: row["label"] for row in map(json.loads, filter(str.strip, f))}
