from pydantic import BaseModel, Field

from app.services.config import settings


class CloneRequest(BaseModel):
    text: str = Field(..., min_length=1)
    speaker_wav_path: str
    language: str = Field(default=settings.default_language)


class CloneResponse(BaseModel):
    status: str
    output_file: str
    output_path: str
