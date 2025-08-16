from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_video(db: Session, video_id: int) -> Optional[models.Video]:
    return db.query(models.Video).filter(models.Video.id == video_id).first()

def get_videos_by_user_email(db: Session, user_email: str) -> List[models.Video]:
    return db.query(models.Video).filter(models.Video.user_email == user_email).all()

def get_video_by_task_id(db: Session, video_task_id: str) -> Optional[models.Video]:
    return db.query(models.Video).filter(models.Video.video_task_id == video_task_id).first()

def get_videos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Video]:
    return db.query(models.Video).offset(skip).limit(limit).all()

def create_video(db: Session, video: schemas.VideoCreate) -> models.Video:
    db_video = models.Video(
        user_email=video.user_email,
        video_task_id=video.video_task_id,
        veo_task_id=video.veo_task_id,
        status=video.status
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def update_video(db: Session, video_id: int, video_update: schemas.VideoUpdate) -> Optional[models.Video]:
    db_video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if db_video:
        update_data = video_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_video, field, value)
        db.commit()
        db.refresh(db_video)
    return db_video

def get_audio(db: Session, audio_id: int) -> Optional[models.Audio]:
    return db.query(models.Audio).filter(models.Audio.id == audio_id).first()

def get_audios_by_user_email(db: Session, user_email: str) -> List[models.Audio]:
    return db.query(models.Audio).filter(models.Audio.user_email == user_email).all()

def get_audios(db: Session, skip: int = 0, limit: int = 100) -> List[models.Audio]:
    return db.query(models.Audio).offset(skip).limit(limit).all()

def create_audio(db: Session, audio: schemas.AudioCreate) -> models.Audio:
    db_audio = models.Audio(
        user_email=audio.user_email,
        text_input=audio.text_input,
        voice_name=audio.voice_name,
        language_code=audio.language_code,
        audio_format=audio.audio_format
    )
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)
    return db_audio

def update_audio(db: Session, audio_id: int, audio_update: schemas.AudioUpdate) -> Optional[models.Audio]:
    db_audio = db.query(models.Audio).filter(models.Audio.id == audio_id).first()
    if db_audio:
        update_data = audio_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_audio, field, value)
        db.commit()
        db.refresh(db_audio)
    return db_audio

# File CRUD Operations
def create_file(db: Session, file_data: dict) -> models.File:
    """Create a new file record"""
    db_file = models.File(**file_data)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_file(db: Session, file_id: int) -> Optional[models.File]:
    """Get file by ID"""
    return db.query(models.File).filter(models.File.id == file_id).first()

def get_file_by_gcs_filename(db: Session, gcs_filename: str) -> Optional[models.File]:
    """Get file by GCS filename"""
    return db.query(models.File).filter(models.File.gcs_filename == gcs_filename).first()

def get_files(db: Session, skip: int = 0, limit: int = 100) -> List[models.File]:
    """Get all files with pagination"""
    return db.query(models.File).offset(skip).limit(limit).all()

def get_files_by_user(db: Session, user_email: str, skip: int = 0, limit: int = 100) -> List[models.File]:
    """Get files by user email"""
    return db.query(models.File).filter(models.File.user_email == user_email).offset(skip).limit(limit).all()

def get_files_by_category(db: Session, category: models.FileCategory, skip: int = 0, limit: int = 100) -> List[models.File]:
    """Get files by category"""
    return db.query(models.File).filter(models.File.category == category).offset(skip).limit(limit).all()

def update_file(db: Session, file_id: int, file_update: schemas.FileUpdate) -> Optional[models.File]:
    """Update file record"""
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if db_file:
        update_data = file_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_file, field, value)
        db.commit()
        db.refresh(db_file)
    return db_file

def update_file_download_count(db: Session, file_id: int) -> Optional[models.File]:
    """Increment file download count"""
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if db_file:
        db_file.download_count += 1
        db.commit()
        db.refresh(db_file)
    return db_file

def delete_file(db: Session, file_id: int) -> bool:
    """Delete file record"""
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    return False

def get_files_count(db: Session) -> int:
    """Get total count of files"""
    return db.query(models.File).count()

def get_files_count_by_user(db: Session, user_email: str) -> int:
    """Get count of files by user"""
    return db.query(models.File).filter(models.File.user_email == user_email).count()

# Video Session CRUD Operations
def create_video_session(db: Session, session: schemas.VideoSessionCreate) -> models.VideoSession:
    """Create a new video session"""
    db_session = models.VideoSession(
        user_id=session.user_id,
        session_name=session.session_name,
        description=session.description
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_video_session(db: Session, session_id: int) -> Optional[models.VideoSession]:
    """Get video session by ID"""
    return db.query(models.VideoSession).filter(models.VideoSession.id == session_id).first()

def get_video_sessions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.VideoSession]:
    """Get video sessions by user ID"""
    return db.query(models.VideoSession).filter(models.VideoSession.user_id == user_id).offset(skip).limit(limit).all()

def get_video_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[models.VideoSession]:
    """Get all video sessions with pagination"""
    return db.query(models.VideoSession).offset(skip).limit(limit).all()

def update_video_session(db: Session, session_id: int, session_update: schemas.VideoSessionUpdate) -> Optional[models.VideoSession]:
    """Update video session"""
    db_session = db.query(models.VideoSession).filter(models.VideoSession.id == session_id).first()
    if db_session:
        update_data = session_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_session, field, value)
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_video_session(db: Session, session_id: int) -> bool:
    """Delete video session"""
    db_session = db.query(models.VideoSession).filter(models.VideoSession.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False

def get_video_sessions_count(db: Session) -> int:
    """Get total count of video sessions"""
    return db.query(models.VideoSession).count()

def get_video_sessions_count_by_user(db: Session, user_id: int) -> int:
    """Get count of video sessions by user"""
    return db.query(models.VideoSession).filter(models.VideoSession.user_id == user_id).count()

def get_files_by_video_session(db: Session, session_id: int, skip: int = 0, limit: int = 100) -> List[models.File]:
    """Get files associated with a video session"""
    return db.query(models.File).filter(models.File.video_session_id == session_id).offset(skip).limit(limit).all()

def get_files_count_by_video_session(db: Session, session_id: int) -> int:
    """Get count of files in a video session"""
    return db.query(models.File).filter(models.File.video_session_id == session_id).count()