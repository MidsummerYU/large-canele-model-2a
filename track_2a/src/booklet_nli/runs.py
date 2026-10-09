from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict

from booklet_nli.config import Settings


class Run(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task: Literal["beginner", "advanced"]
    model: str
    split: Literal["dev", "test"]
    pages: int | None = None
    # File stem in data/prompts/ of the advanced prompt.
    prompt: str = "advanced"


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    endpoint: str
    runs: tuple[Run, ...]

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        with path.open(encoding="utf-8") as f:
            return cls.model_validate(yaml.safe_load(f))


def run_settings(settings: Settings, manifest: Manifest, run: Run) -> Settings:
    return settings.model_copy(update={
        "base_url": manifest.endpoint,
        "model": run.model,
        "context_pages": run.pages,
        "advanced_prompt": settings.prompts_dir / f"{run.prompt}.txt",
    })
