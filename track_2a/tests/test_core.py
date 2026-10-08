import pytest

from booklet_nli.cli import OUTPUT_EXCLUDE
from booklet_nli.config import Settings
from booklet_nli.data import LABELS, load_cases, split
from booklet_nli.nli import is_verbatim, parse_verdict
from booklet_nli.predict import Evidence, Metrics, Prediction
from booklet_nli.score import macro_f1

SETTINGS = Settings(model="")


@pytest.mark.parametrize(("reply", "label"), [
    ('{"label": "contradiction", "evidence": "x"}', LABELS.index("contradiction")),
    ("```json\n{\"label\": \"Neutral\", \"evidence\": \"\"}\n```", LABELS.index("neutral")),
    ("The answer is entailment.", LABELS.index("entailment")),
    ("entailment or contradiction?", None),
])
def test_the_label_is_read_from_json_or_a_single_named_label(reply, label):
    assert parse_verdict(reply).label == label


def test_evidence_must_appear_in_the_source_up_to_whitespace_and_case():
    assert is_verbatim("der  Bundesrat lehnt", "Text. Der Bundesrat\nlehnt die Initiative ab.")
    assert not is_verbatim("Der Nationalrat lehnt", "Der Bundesrat lehnt die Initiative ab.")
    assert not is_verbatim(" ", "anything")


def test_macro_f1_averages_the_three_classes():
    overall, per_class = macro_f1([0, 1, 2, 2], [0, 1, 2, 1])
    assert per_class["entailment"] == 1.0
    assert per_class["contradiction"] == pytest.approx(2 / 3)
    assert overall == pytest.approx((1.0 + 2 / 3 + 2 / 3) / 3)


def test_the_split_is_seeded_and_covers_every_label_and_language_pair():
    cases = load_cases(SETTINGS.dataset)
    first, second = split(cases, SETTINGS.dev_share, SETTINGS.split_seed), split(cases, SETTINGS.dev_share, SETTINGS.split_seed)
    assert [c.id for c in first["dev"]] == [c.id for c in second["dev"]]
    assert len(first["dev"]) + len(first["test"]) == len(cases)
    assert {(c.label, c.pair) for c in first["dev"]} == {(c.label, c.pair) for c in cases}


def test_written_predictions_keep_only_the_challenge_fields():
    prediction = Prediction(
        id="x", label=0, label_name="entailment", evidence=[Evidence(text="t")],
        metrics=Metrics(input_tokens=1, output_tokens=1, inference_time_ms=1), parsed=True, evidence_verbatim=True,
    )
    assert set(prediction.model_dump(exclude=OUTPUT_EXCLUDE, exclude_none=True)) == {"id", "label", "label_name", "evidence", "metrics"}
