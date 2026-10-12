import re
import unicodedata
from difflib import Match as Run, SequenceMatcher
from typing import NamedTuple

# pypdf writes a hyphenated line break as "Verrech-\n" or "Verrech -\n"; booklets also contain soft hyphens.
HYPHENATED_BREAK = re.compile(r"(\w) ?-[ \t]*\n\s*(\w)")
ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…)\s*")


def clean(text: str) -> str:
    """Text as it reads: format characters removed, hyphenated line breaks joined, whitespace collapsed."""
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    return " ".join(HYPHENATED_BREAK.sub(r"\1\2", text).split())


def is_verbatim(evidence: str, source: str) -> bool:
    return bool(evidence.strip()) and clean(evidence).casefold() in clean(source).casefold()


class Match(NamedTuple):
    similarity: float
    page: int | None
    text: str


# Only the pages sharing the longest run of words with a quote are refined word by word, which is the slow step.
REFINED_PAGES = 3


def _folded(words: list[str]) -> list[str]:
    return [w.casefold() for w in words]


def _longest_run(quote: list[str], words: list[str]) -> Run:
    """The longest run of words shared by the page and the quote: its start on the page (a), in the quote (b), its length."""
    return SequenceMatcher(None, _folded(words), _folded(quote), autojunk=False).find_longest_match()


def _closest_span(quote: list[str], words: list[str], run: Run) -> tuple[float, str]:
    """The run of `words` most similar to `quote`: placed on their longest common run, then grown or shrunk word by word."""
    folded, target = _folded(words), " ".join(_folded(quote))
    start = max(0, run.a - run.b)
    end = min(len(words), start + len(quote))

    def similarity(s: int, e: int) -> float:
        return SequenceMatcher(None, target, " ".join(folded[s:e]), autojunk=False).ratio()

    best, improved = similarity(start, end), True
    while improved:
        improved = False
        for s, e in ((start - 1, end), (start + 1, end), (start, end - 1), (start, end + 1)):
            if 0 <= s < e <= len(words) and (score := similarity(s, e)) > best:
                best, start, end, improved = score, s, e, True
    return best, " ".join(words[start:end])


def ground(quote: str, sources: dict[int | None, str], min_similarity: float) -> list[Match] | None:
    """The source text closest to each part of the quote (parts split at an ellipsis), or None if a part has no close match.

    `sources` maps a page number (None for a passage) to its text; on a tie the first source wins.
    """
    parts = [p.split() for p in ELLIPSIS.split(clean(quote)) if p.strip()]
    if not parts:
        return None
    pages = {page: clean(text).split() for page, text in sources.items()}
    matches = []
    for part in parts:
        runs = {page: _longest_run(part, words) for page, words in pages.items()}
        candidates = sorted((page for page in runs if runs[page].size), key=lambda page: -runs[page].size)[:REFINED_PAGES]
        spans = ((page, *_closest_span(part, pages[page], runs[page])) for page in candidates)
        best = max((Match(similarity, page, text) for page, similarity, text in spans), key=lambda m: m.similarity, default=None)
        if best is None or best.similarity < min_similarity:
            return None
        matches.append(best)
    return matches
