from __future__ import annotations

import importlib
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.services.config import settings
from app.services.storage import checkpoints_dir_exists, generate_output_file_path


@dataclass
class OpenVoiceRuntime:
    tts_model: Any
    tone_color_converter: Any
    source_se_path: Path


class CloneService:
    """Lazy-loading wrapper around OpenVoice V2 components.

    Notes:
    - OpenVoice V2 integration is sensitive to checkpoint layout and naming.
    - The official repo uses MeloTTS + ToneColorConverter + speaker embeddings.
    - This service keeps loading logic centralized so route handlers stay simple.
    """

    def __init__(self) -> None:
        self._runtime: OpenVoiceRuntime | None = None
        self._lock = threading.Lock()

    def _find_converter_checkpoint(self, checkpoints_dir: Path) -> Path:
        candidates = [
            checkpoints_dir / "converter" / "config.json",
            checkpoints_dir / "converter" / "checkpoint.pth",
            checkpoints_dir / "converter" / "checkpoint_se.pth",
            checkpoints_dir / "checkpoint.pth",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise HTTPException(
            status_code=500,
            detail=(
                "OpenVoice V2 converter checkpoints were not found in "
                f"{settings.checkpoints_dir}."
            ),
        )

    def _find_source_se(self, checkpoints_dir: Path, language: str) -> Path:
        candidates = [
            checkpoints_dir / "base_speakers" / "ses" / f"{language}.pth",
            checkpoints_dir / "base_speakers" / "ses" / "en-newest.pth",
            checkpoints_dir / "base_speakers" / "ses" / "default.pth",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise HTTPException(
            status_code=500,
            detail=(
                "OpenVoice V2 speaker embedding files were not found in "
                f"{settings.checkpoints_dir}/base_speakers/ses."
            ),
        )

    def _load_runtime(self, language: str) -> OpenVoiceRuntime:
        if not checkpoints_dir_exists():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Missing checkpoints directory. Expected folder: "
                    f"{settings.checkpoints_dir}"
                ),
            )

        checkpoints_dir = Path(settings.checkpoints_dir)

        try:
            openvoice_api = importlib.import_module("openvoice.api")
            se_extractor = importlib.import_module("openvoice.se_extractor")
            melo_api = importlib.import_module("melo.api")
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to import OpenVoice/MeloTTS dependencies: {exc}",
            ) from exc

        converter_ckpt = self._find_converter_checkpoint(checkpoints_dir)
        source_se_path = self._find_source_se(checkpoints_dir, language)

        # OpenVoice V2 commonly uses ToneColorConverter + MeloTTS TTS frontend.
        # Some checkpoint layouts include separate config/checkpoint files; we try
        # to initialize against the detected converter path and fail clearly.
        try:
            tone_color_converter = openvoice_api.ToneColorConverter(str(converter_ckpt))
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to initialize ToneColorConverter from "
                    f"{converter_ckpt}: {exc}"
                ),
            ) from exc

        try:
            tts_model = melo_api.TTS(language=language)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize MeloTTS for language '{language}': {exc}",
            ) from exc

        self._se_extractor = se_extractor
        return OpenVoiceRuntime(
            tts_model=tts_model,
            tone_color_converter=tone_color_converter,
            source_se_path=source_se_path,
        )

    def _get_runtime(self, language: str) -> OpenVoiceRuntime:
        if self._runtime is not None:
            return self._runtime

        with self._lock:
            if self._runtime is None:
                self._runtime = self._load_runtime(language)
        return self._runtime

    def clone_voice(self, text: str, speaker_wav_path: str, language: str | None = None) -> dict[str, str]:
        selected_language = language or settings.default_language
        runtime = self._get_runtime(selected_language)
        output_path = generate_output_file_path()

        # The default OpenVoice flow: TTS to temp speaker, extract target speaker
        # embedding from reference wav, then run tone color conversion.
        tmp_tts_path = output_path.with_suffix(".tts.wav")
        try:
            runtime.tts_model.tts_to_file(text, speaker_id=0, output_path=str(tmp_tts_path))
            target_se, _ = self._se_extractor.get_se(speaker_wav_path, runtime.tone_color_converter)
            runtime.tone_color_converter.convert(
                audio_src_path=str(tmp_tts_path),
                src_se=str(runtime.source_se_path),
                tgt_se=target_se,
                output_path=str(output_path),
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"OpenVoice V2 cloning failed: {exc}") from exc
        finally:
            if tmp_tts_path.exists():
                tmp_tts_path.unlink(missing_ok=True)

        return {
            "status": "ok",
            "output_file": output_path.name,
            "output_path": str(output_path),
        }


clone_service = CloneService()
