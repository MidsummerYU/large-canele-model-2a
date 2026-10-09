import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from booklet_nli.client import ChatRequest, RecordingClient
from booklet_nli.config import Settings

REQUEST = ChatRequest(model="org/model", messages=(("user", "?"),), temperature=0.0, max_tokens=8, sample=0)


class SlowApi:
    def __init__(self):
        self.calls = 0
        self._lock = threading.Lock()
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **_):
        with self._lock:
            self.calls += 1
            answer = f"answer {self.calls}"
        time.sleep(0.05)
        return SimpleNamespace(model="m", choices=[SimpleNamespace(message=SimpleNamespace(content=answer))], usage=None)


def _settings(tmp_path) -> Settings:
    return Settings(model="org/model", base_url="http://example.invalid", recordings_dir=tmp_path)


def test_concurrent_identical_requests_call_the_endpoint_once(tmp_path):
    api = SlowApi()
    client = RecordingClient(_settings(tmp_path), "live", api=api)
    with ThreadPoolExecutor(max_workers=8) as pool:
        answers = list(pool.map(lambda _: client.chat(REQUEST).content, range(8)))
    assert api.calls == 1 and set(answers) == {"answer 1"}


def test_a_request_recorded_twice_replays_its_first_record(tmp_path):
    settings = _settings(tmp_path)
    first = RecordingClient(settings, "live", api=SlowApi()).chat(REQUEST)
    path = settings.recording_path()
    path.write_text(path.read_text() + first.model_copy(update={"content": "later"}).model_dump_json() + "\n")
    assert RecordingClient(settings, "replay").chat(REQUEST).content == first.content
