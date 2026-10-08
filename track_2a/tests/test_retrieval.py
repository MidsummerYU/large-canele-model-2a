from booklet_nli.pages import locate, normalise
from booklet_nli.retrieve import bm25, language, top_pages


def test_hyphenation_across_line_breaks_is_joined():
    assert normalise("Volks-\ninitiative  ABGELEHNT") == "volksinitiative abgelehnt"


def test_a_reference_passage_is_placed_on_the_pages_that_contain_its_sentences():
    pages = ["Titelseite ohne Inhalt.", "Der Bundesrat empfiehlt, die Initiative abzulehnen, weil sie zu teuer ist.", "Anderes Thema."]
    assert locate("Der Bundesrat empfiehlt, die Initiative abzulehnen, weil sie zu teuer ist.", pages) == {2: 1}


def test_bm25_ranks_the_page_with_the_query_terms_first():
    pages = ["Jagdgesetz Wolf Schutz", "Steuern Kinderabzug Bundessteuer", "Kampfjet Armee"]
    scores = bm25("Kinderabzug Bundessteuer", pages)
    assert scores.index(max(scores)) == 1
    assert top_pages("Kinderabzug Bundessteuer", pages, k=1) == [2]


def test_language_is_one_of_the_booklet_languages():
    assert [language(t) for t in ("Der Bundesrat empfiehlt", "Le Conseil fédéral recommande", "Il Consiglio federale raccomanda")] == ["de", "fr", "it"]
