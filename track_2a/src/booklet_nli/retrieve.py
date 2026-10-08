import math
import re
from collections import Counter
from statistics import mean

from py3langid.langid import MODEL_FILE, LanguageIdentifier

from booklet_nli.client import ChatRequest, Recording, RecordingClient
from booklet_nli.config import Settings
from booklet_nli.pages import normalise

LANGUAGES = {"de": "German", "fr": "French", "it": "Italian"}
TRANSLATE_PROMPT = "Translate this sentence into {language}. Reply with the translation only.\n\n{text}"

# One identifier restricted once at import: py3langid's module-level set_languages is not safe across threads.
_IDENTIFIER = LanguageIdentifier.from_model_file(MODEL_FILE)
_IDENTIFIER.set_languages(list(LANGUAGES))


def language(text: str) -> str:
    """The most likely of the booklet languages."""
    return _IDENTIFIER.classify(text)[0]


def tokens(text: str) -> list[str]:
    return re.findall(r"\w{3,}", normalise(text))


def bm25(query: str, documents: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    docs = [tokens(d) for d in documents]
    average = mean(len(d) for d in docs) or 1
    frequency = Counter(word for d in docs for word in set(d))
    terms = set(tokens(query))
    scores = []
    for doc in docs:
        counts, score = Counter(doc), 0.0
        for word in terms & counts.keys():
            idf = math.log(1 + (len(docs) - frequency[word] + 0.5) / (frequency[word] + 0.5))
            score += idf * counts[word] * (k1 + 1) / (counts[word] + k1 * (1 - b + b * len(doc) / average))
        scores.append(score)
    return scores


def query_in_booklet_language(
    claim: str, booklet_language: str, client: RecordingClient, settings: Settings
) -> tuple[str, Recording | None]:
    """The claim as used for retrieval, translated when it is not in the booklet's language, and the translation call."""
    if language(claim) == booklet_language:
        return claim, None
    request = ChatRequest(
        model=settings.translation_model,
        messages=(("user", TRANSLATE_PROMPT.format(language=LANGUAGES[booklet_language], text=claim)),),
        temperature=0.0,
        max_tokens=settings.translation_max_tokens,
        sample=0,
    )
    recording = client.chat(request)
    return recording.content.strip(), recording


def top_pages(query: str, pages: list[str], k: int) -> list[int]:
    """1-based numbers of the k best pages, in page order."""
    scores = bm25(query, pages)
    return sorted(i + 1 for i in sorted(range(len(pages)), key=lambda i: -scores[i])[:k])
