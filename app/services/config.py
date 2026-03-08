import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    storage_dir: str = os.getenv("STORAGE_DIR", "/app/storage")
    output_dir: str = os.getenv("OUTPUT_DIR", "/app/storage/outputs")
    checkpoints_dir: str = os.getenv("CHECKPOINTS_DIR", "/app/checkpoints_v2")
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "pt")


settings = Settings()
