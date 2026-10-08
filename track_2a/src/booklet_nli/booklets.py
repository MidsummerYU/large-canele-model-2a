import hashlib
import json
import time
import urllib.request
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from pydantic import BaseModel

from booklet_nli.config import Settings


class Booklet(BaseModel):
    url: str
    file: str
    bytes: int
    sha256: str


def booklet_file(url: str) -> str:
    return PurePosixPath(urlparse(url).path).name


def fetch_booklets(settings: Settings, urls: list[str]) -> list[Booklet]:
    """Download every booklet once into the cache and check it against the committed manifest."""
    expected = {b.url: b for b in load_manifest(settings.booklet_manifest)}
    settings.booklets_dir.mkdir(parents=True, exist_ok=True)
    booklets = []
    for url in sorted(set(urls)):
        path = settings.booklets_dir / booklet_file(url)
        if not path.exists():
            request = urllib.request.Request(url, headers={"User-Agent": settings.user_agent})
            with urllib.request.urlopen(request, timeout=settings.timeout_s) as response:
                path.write_bytes(response.read())
            time.sleep(settings.fetch_delay_s)
        data = path.read_bytes()
        booklet = Booklet(url=url, file=path.name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        if url in expected and expected[url] != booklet:
            raise ValueError(f"{path.name} differs from the manifest; the publisher may have replaced it")
        booklets.append(booklet)
    return booklets


def load_manifest(path: Path) -> list[Booklet]:
    if not path.exists():
        return []
    return [Booklet.model_validate(b) for b in json.loads(path.read_text(encoding="utf-8"))]


def write_manifest(path: Path, booklets: list[Booklet]) -> None:
    path.write_text(json.dumps([b.model_dump() for b in booklets], indent=1) + "\n", encoding="utf-8")
