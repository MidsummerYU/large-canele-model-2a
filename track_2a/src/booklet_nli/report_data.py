import json
from booklet_nli.config import Settings
from booklet_nli.runs import Manifest, run_name, run_settings


def model_label(model: str) -> str:
    return model.rsplit("-", 1)[-1]


def all_scores(settings: Settings) -> dict[str, dict]:
    """"<model label>/<run name>" -> that run's scores.json, for every run in the manifest."""
    manifest = Manifest.load(settings.runs_manifest)
    table = {}
    for run in manifest.runs:
        s = run_settings(settings, manifest, run)
        name = run_name(run.task, run.split, s)
        table[f"{model_label(run.model)}/{name}"] = json.loads((s.results_dir / s.run_dir() / name / "scores.json").read_text(encoding="utf-8"))
    return table
