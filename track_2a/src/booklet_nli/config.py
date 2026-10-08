from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

TRACK_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Variable names follow the Hack Apertus template: LLM_NAME, LLM_BASE_URL, LLM_API_KEY.
    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=TRACK_DIR / ".env", extra="ignore", populate_by_name=True)

    base_url: str = ""
    api_key: SecretStr = SecretStr("")
    model: str = Field(validation_alias="LLM_NAME")
    temperature: float = 0.0
    max_tokens: int = 400
    concurrency: int = 4
    timeout_s: float = 300.0

    dataset: Path = TRACK_DIR / "data" / "ost" / "v1.1.jsonl"
    beginner_prompt: Path = TRACK_DIR / "data" / "prompts" / "beginner.txt"
    # The booklets exceed the 100 MB limit of data/, so they are downloaded into this cache and checked against the manifest.
    booklets_dir: Path = TRACK_DIR / "data" / "booklets"
    booklet_manifest: Path = TRACK_DIR / "data" / "ost" / "booklets.json"
    gold_pages: Path = TRACK_DIR / "data" / "ost" / "gold_pages.jsonl"
    # Retrieval: a cross-language claim is translated into the booklet's language before BM25 over the pages.
    translation_model: str = "swiss-ai/Apertus-v1.5-8B"
    translation_max_tokens: int = 200
    user_agent: str = "booklet-nli/0.1 (Hack Apertus 2A)"
    fetch_delay_s: float = 1.0
    # Share of the public set used to develop the prompts; the rest is only scored.
    dev_share: float = 0.2
    split_seed: int = 20261008
    recordings_dir: Path = TRACK_DIR / "data" / "recordings"
    results_dir: Path = TRACK_DIR / "results"

    def run_dir(self) -> Path:
        # One folder per endpoint: providers spell model ids with different casing,
        # which collides on case-insensitive filesystems (macOS).
        return Path(urlparse(self.base_url).hostname or "unknown-endpoint") / self.model.replace("/", "__")

    def recording_path(self) -> Path:
        run_dir = self.run_dir()
        return self.recordings_dir / run_dir.parent / f"{run_dir.name}.jsonl"
