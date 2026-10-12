from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel

from booklet_nli.client import ChatRequest, RecordingClient
from booklet_nli.config import Settings
from booklet_nli.data import LABELS
from booklet_nli.evidence import ground, is_verbatim
from booklet_nli.nli import Verdict, parse_verdict
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
    """The challenge's output format, plus diagnostics the scorer reads."""

    id: str
    label: int
    label_name: str
    evidence: list[Evidence]
    metrics: Metrics
    parsed: bool
    # The model's own quote is found in the passage or on the page it cites.
    quote_verbatim: bool
    # Every output evidence is found on its page, after grounding.
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


def _evidence(quote: str, cited: int | None, sources: dict[int | None, str], settings: Settings) -> list[Evidence]:
    """The quote replaced by the closest source text when every part of it has a close match, else as the model wrote it."""
    if not quote.strip():
        return []
    matches = ground(quote, sources, settings.evidence_min_similarity)
    if matches is None:
        return [Evidence(text=quote, page=cited)]
    return [Evidence(text=m.text, page=m.page) for m in matches]


def _verbatim(evidence: list[Evidence], sources: dict[int | None, str]) -> bool:
    return bool(evidence) and all(e.page in sources and is_verbatim(e.text, sources[e.page]) for e in evidence)


def predict_beginner(item: dict, client: RecordingClient, settings: Settings, prompt: str) -> Prediction:
    reference = item["reference"]["text"]
    verdict, metrics = _ask(prompt.format(reference=reference, claim=item["claim"]["text"]), client, settings)
    label = FALLBACK_LABEL if verdict.label is None else verdict.label
    sources = {None: reference}
    evidence = _evidence(verdict.evidence, None, sources, settings)
    return Prediction(
        id=item["id"],
        label=label,
        label_name=LABELS[label],
        evidence=evidence,
        metrics=metrics,
        parsed=verdict.label is not None,
        quote_verbatim=is_verbatim(verdict.evidence, reference),
        evidence_verbatim=_verbatim(evidence, sources),
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
    cited = verdict.page if verdict.page in chosen else None
    # The cited page first, so that it wins a tie with another page holding the same sentence.
    sources = {n: pages[n - 1] for n in sorted(chosen, key=lambda n: n != cited)}
    evidence = _evidence(verdict.evidence, cited, sources, settings)
    return Prediction(
        id=item["id"],
        label=label,
        label_name=LABELS[label],
        evidence=evidence,
        metrics=metrics,
        parsed=verdict.label is not None,
        quote_verbatim=cited is not None and is_verbatim(verdict.evidence, pages[cited - 1]),
        evidence_verbatim=_verbatim(evidence, sources),
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
