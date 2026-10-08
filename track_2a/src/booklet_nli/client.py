import hashlib
import threading
import time
from datetime import UTC, datetime
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, ConfigDict

from booklet_nli.config import Settings

Mode = Literal["live", "replay"]


class MissingRecordingError(LookupError):
    pass


class ChatRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    model: str
    messages: tuple[tuple[str, str], ...]
    temperature: float
    max_tokens: int
    sample: int

    def key(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()


class RequestSummary(BaseModel):
    """What was asked, without the prompt: whole-booklet prompts would push the recordings past the size limits.

    The key is the hash of the full request, so a replay still checks that the prompt is unchanged.
    """

    model: str
    temperature: float
    max_tokens: int
    sample: int
    prompt_chars: int


class Recording(BaseModel):
    key: str
    request: RequestSummary
    content: str
    served_model: str | None
    usage: dict[str, int] | None
    endpoint: str
    latency_ms: int
    recorded_at: datetime


class RecordingClient:
    def __init__(self, settings: Settings, mode: Mode, api: OpenAI | None = None):
        self._settings = settings
        self._mode = mode
        self._path = settings.recording_path()
        self._lock = threading.Lock()
        self._recordings = self._load()
        self._api = api if api is not None or mode == "replay" else OpenAI(
            base_url=settings.base_url,
            api_key=settings.api_key.get_secret_value(),
            timeout=settings.timeout_s,
        )

    def _load(self) -> dict[str, Recording]:
        if not self._path.exists():
            return {}
        with self._path.open(encoding="utf-8") as f:
            records = (Recording.model_validate_json(line) for line in f if line.strip())
            return {r.key: r for r in records}

    def chat(self, request: ChatRequest) -> Recording:
        key = request.key()
        if key in self._recordings:
            return self._recordings[key]
        if self._mode == "replay":
            raise MissingRecordingError(f"no recording for {key} in {self._path}")

        started = time.perf_counter()
        response = self._api.chat.completions.create(
            model=request.model,
            messages=[{"role": role, "content": content} for role, content in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        recording = Recording(
            key=key,
            request=RequestSummary(
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                sample=request.sample,
                prompt_chars=sum(len(content) for _, content in request.messages),
            ),
            content=response.choices[0].message.content or "",
            served_model=response.model,
            usage=response.usage.model_dump(include={"prompt_tokens", "completion_tokens", "total_tokens"})
            if response.usage
            else None,
            endpoint=self._settings.base_url,
            latency_ms=round((time.perf_counter() - started) * 1000),
            recorded_at=datetime.now(UTC),
        )
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as f:
                f.write(recording.model_dump_json() + "\n")
            self._recordings[key] = recording
        return recording
