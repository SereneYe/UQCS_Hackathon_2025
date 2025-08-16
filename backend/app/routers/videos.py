from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/videos",
    tags=["Videos"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Video)
def create_video(video: schemas.VideoCreate, db: Session = Depends(get_db)):
    """Create a new video"""
    return crud.create_video(db=db, video=video)

@router.get("/", response_model=List[schemas.Video])
def read_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of videos with pagination"""
    videos = crud.get_videos(db, skip=skip, limit=limit)
    return videos

@router.get("/{video_id}", response_model=schemas.Video)
def read_video(video_id: int, db: Session = Depends(get_db)):
    """Get video by ID"""
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@router.get("/user/{user_email}", response_model=List[schemas.Video])
def read_videos_by_user(user_email: str, db: Session = Depends(get_db)):
    """Get videos by user email"""
    videos = crud.get_videos_by_user_email(db, user_email=user_email)
    return videos

@router.get("/task/{video_task_id}", response_model=schemas.Video)
def read_video_by_task_id(video_task_id: str, db: Session = Depends(get_db)):
    """Get video by task ID"""
    db_video = crud.get_video_by_task_id(db, video_task_id=video_task_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video task not found")
    return db_video

@router.put("/{video_id}", response_model=schemas.Video)
def update_video(video_id: int, video_update: schemas.VideoUpdate, db: Session = Depends(get_db)):
    """Update video information"""
    db_video = crud.update_video(db, video_id=video_id, video_update=video_update)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video