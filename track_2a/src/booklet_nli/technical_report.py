import json
from statistics import median

from booklet_nli.booklets import load_manifest
from booklet_nli.config import Settings
from booklet_nli.data import load_cases, split
from booklet_nli.pages import GoldPages, booklet_pages
from booklet_nli.client import RecordingClient
from booklet_nli.report_data import all_scores
from booklet_nli.retrieve import language, query_in_booklet_language, top_pages
from booklet_nli.runs import Manifest

# Context size at which the report compares retrieval with and without translating the claim.
RECALL_PAGES = 5


def _retrieval_recall(settings: Settings, cases, gold: dict[str, list[int]]) -> dict[str, dict[str, float]]:
    """Share of claims with a gold page in the top pages, same- vs cross-language, with the claim as is or translated."""
    translator = RecordingClient(settings.model_copy(update={"model": settings.translation_model}), "replay")
    hits: dict[str, dict[str, list[bool]]] = {"same": {"plain": [], "translated": []}, "cross": {"plain": [], "translated": []}}
    for case in cases:
        pages = booklet_pages(settings, case.booklet_url)
        translated, _ = query_in_booklet_language(case.claim, language(" ".join(pages)), translator, settings)
        group = "same" if case.claim_language == case.reference_language else "cross"
        for kind, claim in (("plain", case.claim), ("translated", translated)):
            hits[group][kind].append(bool(set(top_pages(f"{case.vote} {claim}", pages, RECALL_PAGES)) & set(gold[case.id])))
    return {g: {k: sum(v) / len(v) for k, v in kinds.items()} for g, kinds in hits.items()}


def report_context(settings: Settings) -> dict:
    scores = all_scores(settings)
    overall = {key: table["all"]["all"] for key, table in scores.items()}
    cases = load_cases(settings.dataset)
    parts = split(cases, settings.dev_share, settings.split_seed)
    booklets = load_manifest(settings.booklet_manifest)
    gold = GoldPages.load(settings.gold_pages)
    manifest = Manifest.load(settings.runs_manifest)
    tpc = {key: s["input_tokens"] / s["n"] for key, s in overall.items()}
    return {
        "r": scores,
        "o": overall,
        "tpc": tpc,
        "full_ratio": tpc["8B/advanced-full-advanced-dev"] / tpc["8B/advanced-p3-advanced-dev"],
        "recall": _retrieval_recall(settings.model_copy(update={"base_url": manifest.endpoint}), parts["dev"], gold),
        "recall_k": RECALL_PAGES,
        "endpoint": manifest.endpoint,
        "cases": len(cases),
        "dev": len(parts["dev"]),
        "test": len(parts["test"]),
        "cross": sum(c.claim_language != c.reference_language for c in cases) / len(cases),
        "booklets": len(booklets),
        "booklet_mb": sum(b.bytes for b in booklets) / 1e6,
        "pages_median": median(len(booklet_pages(settings, b.url)) for b in booklets),
        "located": sum(bool(pages) for pages in gold.values()) / len(gold),
        "settings": settings,
    }


def write_report(settings: Settings) -> None:
    text = settings.report_template.read_text(encoding="utf-8").format(**report_context(settings))
    settings.report_path.write_text(text, encoding="utf-8")
