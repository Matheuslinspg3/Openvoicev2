from fastapi import APIRouter, HTTPException

from app.schemas.clone import CloneRequest, CloneResponse
from app.services.clone_service import clone_service
from app.services.storage import checkpoints_dir_exists, reference_file_exists
from app.services.config import settings

router = APIRouter()


@router.post("/clone", response_model=CloneResponse)
def clone(payload: CloneRequest) -> dict[str, str]:
    if not reference_file_exists(payload.speaker_wav_path):
        raise HTTPException(
            status_code=400,
            detail=f"Speaker reference file was not found: {payload.speaker_wav_path}",
        )

    if not checkpoints_dir_exists():
        raise HTTPException(
            status_code=400,
            detail=f"Missing checkpoints directory. Expected folder: {settings.checkpoints_dir}",
        )

    return clone_service.clone_voice(
        text=payload.text,
        speaker_wav_path=payload.speaker_wav_path,
        language=payload.language,
    )
