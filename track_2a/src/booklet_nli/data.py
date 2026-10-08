import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

LABELS = ("entailment", "neutral", "contradiction")
Split = Literal["dev", "test"]


class Case(BaseModel):
    id: str
    claim: str
    claim_language: str
    reference: str
    reference_language: str
    label: int
    vote: str
    booklet_url: str

    @property
    def pair(self) -> str:
        return f"{self.claim_language}-{self.reference_language}"


def load_cases(path: Path) -> list[Case]:
    cases = []
    with path.open(encoding="utf-8") as f:
        for number, line in enumerate(filter(str.strip, f), start=1):
            row = json.loads(line)
            cases.append(Case(
                id=f"ost-{number:04d}",
                claim=row["claim"],
                claim_language=row["claim_language"],
                reference=row["reference_string"],
                reference_language=row["reference_language"],
                label=int(row["entailment_label"]),
                vote=row["vote"],
                booklet_url=row["booklet_url"],
            ))
    return cases


def split(cases: list[Case], dev_share: float, seed: int) -> dict[Split, list[Case]]:
    """Seeded split stratified by label and language pair, so the dev set covers every combination."""
    strata: dict[tuple[int, str], list[Case]] = defaultdict(list)
    for case in cases:
        strata[case.label, case.pair].append(case)
    rng = random.Random(seed)
    dev_ids = set()
    for key in sorted(strata):
        members = sorted(strata[key], key=lambda c: c.id)
        dev_ids |= {c.id for c in rng.sample(members, round(dev_share * len(members)))}
    return {"dev": [c for c in cases if c.id in dev_ids], "test": [c for c in cases if c.id not in dev_ids]}


def beginner_input(case: Case) -> dict:
    """The challenge's beginner input format."""
    return {"id": case.id, "reference": {"text": case.reference}, "claim": {"text": case.claim}}
