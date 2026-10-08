from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel

from booklet_nli.client import ChatRequest, RecordingClient
from booklet_nli.config import Settings
from booklet_nli.data import LABELS
from booklet_nli.nli import is_verbatim, parse_verdict

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


def predict_beginner(item: dict, client: RecordingClient, settings: Settings, prompt: str) -> Prediction:
    reference, claim = item["reference"]["text"], item["claim"]["text"]
    request = ChatRequest(
        model=settings.model,
        messages=(("user", prompt.format(reference=reference, claim=claim)),),
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        sample=0,
    )
    recording = client.chat(request)
    verdict = parse_verdict(recording.content)
    label = FALLBACK_LABEL if verdict.label is None else verdict.label
    usage = recording.usage or {}
    return Prediction(
        id=item["id"],
        label=label,
        label_name=LABELS[label],
        evidence=[Evidence(text=verdict.evidence)] if verdict.evidence.strip() else [],
        metrics=Metrics(
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            inference_time_ms=recording.latency_ms,
        ),
        parsed=verdict.label is not None,
        evidence_verbatim=is_verbatim(verdict.evidence, reference),
    )


def predict_all(items: list[dict], settings: Settings, mode: str, prompt: str) -> list[Prediction]:
    client = RecordingClient(settings, mode)
    with ThreadPoolExecutor(max_workers=settings.concurrency) as pool:
        return list(pool.map(lambda item: predict_beginner(item, client, settings, prompt), items))
