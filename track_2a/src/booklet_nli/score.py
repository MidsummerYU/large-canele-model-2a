from statistics import mean, quantiles

from pydantic import BaseModel

from booklet_nli.data import LABELS, Case
from booklet_nli.predict import Prediction


class Scores(BaseModel):
    n: int
    macro_f1: float
    f1: dict[str, float]
    accuracy: float
    confusion: dict[str, dict[str, int]]
    unparsed: int
    evidence_verbatim: float
    input_tokens: int
    latency_mean_ms: float
    latency_p95_ms: float


def macro_f1(gold: list[int], predicted: list[int]) -> tuple[float, dict[str, float]]:
    per_class = {}
    for index, name in enumerate(LABELS):
        tp = sum(g == index and p == index for g, p in zip(gold, predicted))
        fp = sum(g != index and p == index for g, p in zip(gold, predicted))
        fn = sum(g == index and p != index for g, p in zip(gold, predicted))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        per_class[name] = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return mean(per_class.values()), per_class


def scores(cases: list[Case], predictions: list[Prediction]) -> Scores:
    by_id = {p.id: p for p in predictions}
    pairs = [(c, by_id[c.id]) for c in cases]
    gold, predicted = [c.label for c, _ in pairs], [p.label for _, p in pairs]
    overall, per_class = macro_f1(gold, predicted)
    latencies = [p.metrics.inference_time_ms for _, p in pairs]
    claimed = [p for _, p in pairs if p.label != LABELS.index("neutral")]
    return Scores(
        n=len(pairs),
        macro_f1=overall,
        f1=per_class,
        accuracy=sum(g == p for g, p in zip(gold, predicted)) / len(pairs),
        confusion={g: {p: sum(c.label == gi and q.label == pi for c, q in pairs) for pi, p in enumerate(LABELS)} for gi, g in enumerate(LABELS)},
        unparsed=sum(not p.parsed for _, p in pairs),
        evidence_verbatim=sum(p.evidence_verbatim for p in claimed) / len(claimed) if claimed else 0.0,
        input_tokens=sum(p.metrics.input_tokens or 0 for _, p in pairs),
        latency_mean_ms=mean(latencies),
        latency_p95_ms=quantiles(latencies, n=20)[-1] if len(latencies) > 1 else latencies[0],
    )


def breakdown(cases: list[Case], predictions: list[Prediction]) -> dict[str, dict[str, Scores]]:
    """Scores overall, for same- vs cross-language pairs, and per claim and reference language."""
    groups: dict[str, dict[str, list[Case]]] = {
        "all": {"all": cases},
        "pairing": {
            "same-language": [c for c in cases if c.claim_language == c.reference_language],
            "cross-language": [c for c in cases if c.claim_language != c.reference_language],
        },
        "claim_language": {},
        "reference_language": {},
    }
    for case in cases:
        groups["claim_language"].setdefault(case.claim_language, []).append(case)
        groups["reference_language"].setdefault(case.reference_language, []).append(case)
    return {field: {name: scores(members, predictions) for name, members in sorted(by.items())} for field, by in groups.items()}
