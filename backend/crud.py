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