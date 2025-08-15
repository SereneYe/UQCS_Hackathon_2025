from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import crud, models, schemas
from database import SessionLocal, engine, get_db
from tts_service import tts_service

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hackathon Backend API", 
    description="FastAPI backend with SQLite for UQCS Hackathon 2025",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hackathon Backend API is alive 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/videos/", response_model=schemas.Video, tags=["Videos"])
def create_video(video: schemas.VideoCreate, db: Session = Depends(get_db)):
    return crud.create_video(db=db, video=video)

@app.get("/videos/", response_model=List[schemas.Video], tags=["Videos"])
def read_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    videos = crud.get_videos(db, skip=skip, limit=limit)
    return videos

@app.get("/videos/{video_id}", response_model=schemas.Video, tags=["Videos"])
def read_video(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@app.get("/videos/user/{user_email}", response_model=List[schemas.Video], tags=["Videos"])
def read_videos_by_user(user_email: str, db: Session = Depends(get_db)):
    videos = crud.get_videos_by_user_email(db, user_email=user_email)
    return videos

@app.get("/videos/task/{video_task_id}", response_model=schemas.Video, tags=["Videos"])
def read_video_by_task_id(video_task_id: str, db: Session = Depends(get_db)):
    db_video = crud.get_video_by_task_id(db, video_task_id=video_task_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video task not found")
    return db_video

@app.put("/videos/{video_id}", response_model=schemas.Video, tags=["Videos"])
def update_video(video_id: int, video_update: schemas.VideoUpdate, db: Session = Depends(get_db)):
    db_video = crud.update_video(db, video_id=video_id, video_update=video_update)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

# Audio/TTS Endpoints
@app.post("/audio/synthesize", response_model=schemas.Audio, tags=["Audio"])
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

@app.get("/audio/", response_model=List[schemas.Audio], tags=["Audio"])
def read_audios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get list of audio synthesis requests
    """
    audios = crud.get_audios(db, skip=skip, limit=limit)
    return audios

@app.get("/audio/{audio_id}", response_model=schemas.Audio, tags=["Audio"])
def read_audio(audio_id: int, db: Session = Depends(get_db)):
    """
    Get audio synthesis request by ID
    """
    db_audio = crud.get_audio(db, audio_id=audio_id)
    if db_audio is None:
        raise HTTPException(status_code=404, detail="Audio not found")
    return db_audio

@app.get("/audio/user/{user_email}", response_model=List[schemas.Audio], tags=["Audio"])
def read_audios_by_user(user_email: str, db: Session = Depends(get_db)):
    """
    Get audio synthesis requests by user email
    """
    audios = crud.get_audios_by_user_email(db, user_email=user_email)
    return audios

@app.get("/audio/{audio_id}/download", tags=["Audio"])
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

@app.get("/audio/voices", tags=["Audio"])
def get_available_voices(language_code: str = None):
    """
    Get list of available voices from Google Cloud TTS
    """
    try:
        voices = tts_service.get_available_voices(language_code)
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
