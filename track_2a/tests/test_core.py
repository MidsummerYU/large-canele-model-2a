import pytest

from booklet_nli.cli import OUTPUT_EXCLUDE
from booklet_nli.config import Settings
from booklet_nli.data import LABELS, load_cases, split
from booklet_nli.evidence import clean, ground, is_verbatim
from booklet_nli.nli import parse_verdict
from booklet_nli.predict import Evidence, Metrics, Prediction
from booklet_nli.score import macro_f1, paired_bootstrap

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


def test_clean_joins_both_kinds_of_hyphenated_line_break_and_drops_soft_hyphens():
    assert clean("Verrech -\nnungssteuer und gül-\ntig, Geschäfts\u00adlokal") == "Verrechnungssteuer und gültig, Geschäftslokal"


def test_a_close_quote_is_replaced_by_the_source_text_it_matches():
    page = "Abstimmung. Bundesrat und Parlament möchten den Abzug von 10 100 auf 25 000 Franken pro Kind erhöhen. Weiter."
    (match,) = ground("Bundesrat und Parlament möchten den Abzug von 10100 auf 25000 Franken pro Kind erhöhen.", {4: page}, 0.85)
    assert match.page == 4
    assert match.text == "Bundesrat und Parlament möchten den Abzug von 10 100 auf 25 000 Franken pro Kind erhöhen."


def test_each_part_of_a_quote_with_an_ellipsis_is_matched_on_its_own():
    page = "Bundesrat und Parlament empfehlen, am 7. März 2021 wie folgt zu stimmen: Verhüllungsverbot Nein"
    matches = ground("Bundesrat und Parlament empfehlen, ... Verhüllungsverbot Nein", {2: page}, 0.85)
    assert [m.text for m in matches] == ["Bundesrat und Parlament empfehlen,", "Verhüllungsverbot Nein"]


def test_a_quote_without_a_close_match_is_not_grounded():
    page = "Le Conseil fédéral et le Parlement recommandent d’accepter la loi."
    assert ground("Consiglio federale e Parlamento raccomandano di accettare la legge.", {1: page}, 0.85) is None


def test_on_a_tie_the_first_source_wins():
    sentence = "Die Emissionsabgabe beträgt ein Prozent des aufgenommenen Kapitals."
    (match,) = ground(sentence, {37: sentence, 8: sentence}, 0.85)
    assert match.page == 37


def test_macro_f1_averages_the_three_classes():
    overall, per_class = macro_f1([0, 1, 2, 2], [0, 1, 2, 1])
    assert per_class["entailment"] == 1.0
    assert per_class["contradiction"] == pytest.approx(2 / 3)
    assert overall == pytest.approx((1.0 + 2 / 3 + 2 / 3) / 3)


def test_the_bootstrap_interval_of_identical_systems_is_zero_and_a_better_system_is_ahead():
    gold = [0, 1, 2] * 20
    same = paired_bootstrap(gold, gold, gold, 200, SETTINGS.bootstrap_seed, SETTINGS.confidence)
    assert same["difference"] == (0.0, 0.0)
    worse = [1, 1, 2] * 20
    ahead = paired_bootstrap(gold, gold, worse, 200, SETTINGS.bootstrap_seed, SETTINGS.confidence)
    assert ahead["difference"][0] > 0
    assert ahead == paired_bootstrap(gold, gold, worse, 200, SETTINGS.bootstrap_seed, SETTINGS.confidence)


def test_the_split_is_seeded_and_covers_every_label_and_language_pair():
    cases = load_cases(SETTINGS.dataset)
    first, second = split(cases, SETTINGS.dev_share, SETTINGS.split_seed), split(cases, SETTINGS.dev_share, SETTINGS.split_seed)
    assert [c.id for c in first["dev"]] == [c.id for c in second["dev"]]
    assert len(first["dev"]) + len(first["test"]) == len(cases)
    assert {(c.label, c.pair) for c in first["dev"]} == {(c.label, c.pair) for c in cases}


def test_written_predictions_keep_only_the_challenge_fields():
    prediction = Prediction(
        id="x", label=0, label_name="entailment", evidence=[Evidence(text="t")],
        metrics=Metrics(input_tokens=1, output_tokens=1, inference_time_ms=1), parsed=True, quote_verbatim=True, evidence_verbatim=True,
    )
    assert set(prediction.model_dump(exclude=OUTPUT_EXCLUDE, exclude_none=True)) == {"id", "label", "label_name", "evidence", "metrics"}
