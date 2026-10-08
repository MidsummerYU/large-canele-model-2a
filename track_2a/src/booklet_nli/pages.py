import json
import re
from pathlib import Path

from pypdf import PdfReader

from booklet_nli.booklets import booklet_file
from booklet_nli.config import Settings
from booklet_nli.data import Case

# Sentences shorter than this are too generic ("Ja", headings) to place a passage on a page.
MIN_SENTENCE_CHARS = 40


def normalise(text: str) -> str:
    # Booklets hyphenate across line breaks; joining them lets passages from the dataset match page text.
    return " ".join(re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text).split()).casefold()


def booklet_pages(settings: Settings, url: str) -> list[str]:
    return pdf_pages(settings.booklets_dir / booklet_file(url))


def pdf_pages(pdf: Path) -> list[str]:
    """The text of every page, cached next to the PDF because parsing all booklets takes a while."""
    cache = pdf.with_suffix(".pages.json")
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    pages = [page.extract_text() or "" for page in PdfReader(pdf).pages]
    cache.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    return pages


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?:])\s+", normalise(text)) if len(s) >= MIN_SENTENCE_CHARS]


def locate(reference: str, pages: list[str]) -> dict[int, int]:
    """1-based page number -> how many sentences of the reference passage it contains."""
    normalised = [normalise(p) for p in pages]
    hits = {}
    for number, page in enumerate(normalised, start=1):
        count = sum(sentence in page for sentence in sentences(reference))
        if count:
            hits[number] = count
    return hits


class GoldPages(dict):
    @classmethod
    def load(cls, path: Path) -> "GoldPages":
        with path.open(encoding="utf-8") as f:
            return cls({row["id"]: row["pages"] for row in map(json.loads, filter(str.strip, f))})


def write_gold_pages(settings: Settings, cases: list[Case]) -> dict[str, float]:
    """Locate every reference passage in its booklet; returns how many could be placed."""
    rows = []
    for case in cases:
        hits = locate(case.reference, booklet_pages(settings, case.booklet_url))
        rows.append({"id": case.id, "pages": sorted(hits), "sentence_hits": hits})
    with settings.gold_pages.open("w", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    located = sum(bool(r["pages"]) for r in rows)
    return {"cases": len(rows), "located": located, "share": located / len(rows)}
