from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel

from booklet_nli.client import ChatRequest, RecordingClient
from booklet_nli.config import Settings
from booklet_nli.data import LABELS
from booklet_nli.nli import Verdict, is_verbatim, parse_verdict
from booklet_nli.pages import pdf_pages
from booklet_nli.retrieve import language, query_in_booklet_language, top_pages

# Label given when the reply names no label: claiming support or contradiction without evidence is the worse error.
FALLBACK_LABEL = LABELS.index("neutral")


class Evidence(BaseModel):
    text: str
    page: int | None = None


class Metrics(BaseModel):
    input_tokens: int | None
    output_tokens: int | None
    inference_time_ms: int


class Prediction(BaseModel):
    """The challenge's output format, plus two diagnostics the scorer reads."""

    id: str
    label: int
    label_name: str
    evidence: list[Evidence]
    metrics: Metrics
    parsed: bool
    evidence_verbatim: bool
    # Advanced task only: the pages given to the model.
    context_pages: list[int] | None = None


def _ask(prompt: str, client: RecordingClient, settings: Settings) -> tuple[Verdict, Metrics]:
    request = ChatRequest(
        model=settings.model,
        messages=(("user", prompt),),
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        sample=0,
    )
    recording = client.chat(request)
    usage = recording.usage or {}
    metrics = Metrics(
        input_tokens=usage.get("prompt_tokens"),
        output_tokens=usage.get("completion_tokens"),
        inference_time_ms=recording.latency_ms,
    )
    return parse_verdict(recording.content), metrics


def predict_beginner(item: dict, client: RecordingClient, settings: Settings, prompt: str) -> Prediction:
    reference = item["reference"]["text"]
    verdict, metrics = _ask(prompt.format(reference=reference, claim=item["claim"]["text"]), client, settings)
    label = FALLBACK_LABEL if verdict.label is None else verdict.label
    return Prediction(
        id=item["id"],
        label=label,
        label_name=LABELS[label],
        evidence=[Evidence(text=verdict.evidence)] if verdict.evidence.strip() else [],
        metrics=metrics,
        parsed=verdict.label is not None,
        evidence_verbatim=is_verbatim(verdict.evidence, reference),
    )


def predict_advanced(
    item: dict, client: RecordingClient, translator: RecordingClient, settings: Settings, prompt: str
) -> Prediction:
    pages = pdf_pages(Path(item["booklet"]["path"]))
    claim, vote = item["claim"]["text"], item.get("vote", "")
    translation = None
    if settings.context_pages is None:
        chosen = list(range(1, len(pages) + 1))
    else:
        query, translation = query_in_booklet_language(claim, language(" ".join(pages)), translator, settings)
        chosen = top_pages(f"{vote} {query}", pages, settings.context_pages)
    context = "\n\n".join(f"[Page {n}]\n{pages[n - 1]}" for n in chosen)
    verdict, metrics = _ask(prompt.format(vote=vote, pages=context, claim=claim), client, settings)
    if translation is not None:
        # The organisers count tokens at a proxy, so the translation call is part of the cost.
        usage = translation.usage or {}
        metrics = Metrics(
            input_tokens=(metrics.input_tokens or 0) + usage.get("prompt_tokens", 0),
            output_tokens=(metrics.output_tokens or 0) + usage.get("completion_tokens", 0),
            inference_time_ms=metrics.inference_time_ms + translation.latency_ms,
        )
    label = FALLBACK_LABEL if verdict.label is None else verdict.label
    page = verdict.page if verdict.page in chosen else None
    return Prediction(
        id=item["id"],
        label=label,
        label_name=LABELS[label],
        evidence=[Evidence(text=verdict.evidence, page=page)] if verdict.evidence.strip() else [],
        metrics=metrics,
        parsed=verdict.label is not None,
        evidence_verbatim=page is not None and is_verbatim(verdict.evidence, pages[page - 1]),
        context_pages=chosen,
    )


def predict_all(items: list[dict], settings: Settings, mode: str, prompts: dict[str, str]) -> list[Prediction]:
    """Predict every item; an item with a booklet is the advanced task, one with a reference the beginner task."""
    client = RecordingClient(settings, mode)
    translator = RecordingClient(settings.model_copy(update={"model": settings.translation_model}), mode)

    def one(item: dict) -> Prediction:
        if "booklet" in item:
            return predict_advanced(item, client, translator, settings, prompts["advanced"])
        return predict_beginner(item, client, settings, prompts["beginner"])

    with ThreadPoolExecutor(max_workers=settings.concurrency) as pool:
        return list(pool.map(one, items))
