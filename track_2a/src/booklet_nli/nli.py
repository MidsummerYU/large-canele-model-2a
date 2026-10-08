import json
import re
from pydantic import BaseModel

from booklet_nli.data import LABELS


class Verdict(BaseModel):
    label: int | None
    evidence: str


def parse_verdict(text: str) -> Verdict:
    """The model's JSON reply; label None when no known label can be read."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        reply = json.loads(match.group()) if match else {}
    except json.JSONDecodeError:
        reply = {}
    name = str(reply.get("label", "")).strip().lower()
    if name not in LABELS:
        # A reply that is not valid JSON may still name exactly one label.
        named = [label for label in LABELS if label in text.lower()]
        name = named[0] if len(named) == 1 else ""
    evidence = reply.get("evidence", "")
    return Verdict(label=LABELS.index(name) if name else None, evidence=evidence if isinstance(evidence, str) else "")


def _normalise(text: str) -> str:
    return " ".join(text.split()).casefold()


def is_verbatim(evidence: str, source: str) -> bool:
    return bool(evidence.strip()) and _normalise(evidence) in _normalise(source)
