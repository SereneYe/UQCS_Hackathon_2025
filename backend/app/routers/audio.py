from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import crud
import models
import schemas
from database import get_db
from tts_service import tts_service

router = APIRouter(
    prefix="/audio",
    tags=["Audio"],
    responses={404: {"description": "Not found"}},
)

@router.post("/synthesize", response_model=schemas.Audio)
async def synthesize_audio(
    audio: schemas.AudioCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a text-to-speech audio synthesis request
    """
    try:
        audio_result = await tts_service.process_tts_request(db, audio)
        return audio_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")

@router.get("/", response_model=List[schemas.Audio])
def read_audios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get list of audio synthesis requests
    """
    audios = crud.get_audios(db, skip=skip, limit=limit)
    return audios

@router.get("/{audio_id}", response_model=schemas.Audio)
def read_audio(audio_id: int, db: Session = Depends(get_db)):
    """
    Get audio synthesis request by ID
    """
    db_audio = crud.get_audio(db, audio_id=audio_id)
    if db_audio is None:
        raise HTTPException(status_code=404, detail="Audio not found")
    return db_audio

@router.get("/user/{user_email}", response_model=List[schemas.Audio])
def read_audios_by_user(user_email: str, db: Session = Depends(get_db)):
    """
    Get audio synthesis requests by user email
    """
    audios = crud.get_audios_by_user_email(db, user_email=user_email)
    return audios

@router.get("/{audio_id}/download")
def download_audio(audio_id: int, db: Session = Depends(get_db)):
    """
    Download the generated audio file
    """
    db_audio = crud.get_audio(db, audio_id=audio_id)
    if db_audio is None:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    if db_audio.status != models.AudioStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Audio not ready for download")
    
    if not db_audio.file_path or not os.path.exists(db_audio.file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=db_audio.file_path,
        filename=f"audio_{audio_id}.{db_audio.audio_format.lower()}",
        media_type=f"audio/{db_audio.audio_format.lower()}"
    )

@router.get("/voices")
def get_available_voices(language_code: Optional[str] = None):
    """
    Get list of available voices from Google Cloud TTS
    """
    try:
        voices = tts_service.get_available_voices(language_code)
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")