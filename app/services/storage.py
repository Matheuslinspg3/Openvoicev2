from pathlib import Path
import uuid

from app.services.config import settings


def ensure_output_dir() -> Path:
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_output_file_path() -> Path:
    output_dir = ensure_output_dir()
    filename = f"{uuid.uuid4()}.wav"
    return output_dir / filename


def reference_file_exists(speaker_wav_path: str) -> bool:
    return Path(speaker_wav_path).is_file()


def checkpoints_dir_exists() -> bool:
    return Path(settings.checkpoints_dir).is_dir()
