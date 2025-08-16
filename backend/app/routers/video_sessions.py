from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import crud
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/video-sessions",
    tags=["Video Sessions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.VideoSession)
async def create_video_session(
    user_id: int = Form(...),
    session_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a new video session for a user
    """
    try:
        session_data = schemas.VideoSessionCreate(
            user_id=user_id,
            session_name=session_name,
            description=description
        )
        
        db_session = crud.create_video_session(db, session_data)
        
        return db_session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create video session: {str(e)}")

@router.get("/", response_model=schemas.VideoSessionList)
async def list_video_sessions(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    List video sessions with pagination and optional user filter
    """
    try:
        if user_id:
            sessions = crud.get_video_sessions_by_user(db, user_id, skip, limit)
            total = crud.get_video_sessions_count_by_user(db, user_id)
        else:
            sessions = crud.get_video_sessions(db, skip, limit)
            total = crud.get_video_sessions_count(db)
        
        return schemas.VideoSessionList(
            sessions=sessions,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list video sessions: {str(e)}")

@router.get("/{session_id}", response_model=schemas.VideoSession)
async def get_video_session(session_id: int, db: Session = Depends(get_db)):
    """
    Get video session by ID
    """
    db_session = crud.get_video_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Video session not found")
    return db_session

@router.put("/{session_id}", response_model=schemas.VideoSession)
async def update_video_session(
    session_id: int,
    session_update: schemas.VideoSessionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update video session
    """
    db_session = crud.update_video_session(db, session_id, session_update)
    if not db_session:
        raise HTTPException(status_code=404, detail="Video session not found")
    return db_session

@router.delete("/{session_id}")
async def delete_video_session(session_id: int, db: Session = Depends(get_db)):
    """
    Delete video session
    """
    success = crud.delete_video_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video session not found")
    return {"message": "Video session deleted successfully"}

@router.get("/{session_id}/files", response_model=schemas.FileList)
async def get_session_files(
    session_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get files associated with a video session
    """
    try:
        # Check if session exists
        db_session = crud.get_video_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Video session not found")
        
        files = crud.get_files_by_video_session(db, session_id, skip, limit)
        total = crud.get_files_count_by_video_session(db, session_id)
        
        return schemas.FileList(
            files=files,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session files: {str(e)}")

@router.post("/{session_id}/start-processing")
async def start_session_processing(session_id: int, db: Session = Depends(get_db)):
    """
    Start video processing for a session
    """
    try:
        db_session = crud.get_video_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Video session not found")
        
        # Update session status to processing
        update_data = schemas.VideoSessionUpdate(status=models.VideoSessionStatus.PROCESSING)
        updated_session = crud.update_video_session(db, session_id, update_data)
        
        # Here you would typically trigger your video processing pipeline
        # For now, we'll just update the status
        
        return {
            "message": "Video processing started",
            "session_id": session_id,
            "status": updated_session.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

@router.post("/{session_id}/complete")
async def complete_session(
    session_id: int,
    output_video_path: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Mark session as completed with optional output video path
    """
    try:
        db_session = crud.get_video_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Video session not found")
        
        update_data = schemas.VideoSessionUpdate(
            status=models.VideoSessionStatus.COMPLETED,
            output_video_path=output_video_path
        )
        updated_session = crud.update_video_session(db, session_id, update_data)
        
        return {
            "message": "Video session completed",
            "session_id": session_id,
            "output_video_path": updated_session.output_video_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")