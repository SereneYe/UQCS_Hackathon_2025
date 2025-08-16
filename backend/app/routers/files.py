from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import crud
import models
import schemas
from database import get_db
from app.services.storage_service import storage_service

router = APIRouter(
    prefix="/files",
    tags=["File Management"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload", response_model=schemas.FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_email: Optional[str] = Form(None),
    video_session_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_public: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Upload file to Google Cloud Storage
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to GCS
        gcs_info = await storage_service.upload_file(
            file_content, 
            file.filename, 
            user_email
        )
        
        # Create database record
        file_data = {
            "user_email": user_email,
            "video_session_id": video_session_id,
            "original_filename": gcs_info["original_filename"],
            "gcs_filename": gcs_info["gcs_filename"],
            "bucket_name": gcs_info["bucket_name"],
            "file_size": gcs_info["size"],
            "content_type": gcs_info["content_type"],
            "category": models.FileCategory(gcs_info["category"]),
            "status": models.FileStatus.COMPLETED,
            "public_url": gcs_info["public_url"] if is_public else None,
            "gcs_path": gcs_info["gcs_filename"],
            "description": description,
            "tags": tags,
            "is_public": is_public,
            "video_session_id": video_session_id
        }
        
        db_file = crud.create_file(db, file_data)
        
        # Update video session file count if session is provided
        if video_session_id:
            try:
                session = crud.get_video_session(db, video_session_id)
                if session:
                    total_files = crud.get_files_count_by_video_session(db, video_session_id)
                    crud.update_video_session(db, video_session_id, schemas.VideoSessionUpdate(total_files=total_files))
            except Exception as e:
                print(f"Warning: Could not update session file count: {e}")
        
        return schemas.FileUploadResponse(
            id=db_file.id,
            original_filename=db_file.original_filename,
            gcs_filename=db_file.gcs_filename,
            file_size=db_file.file_size,
            content_type=db_file.content_type,
            category=db_file.category,
            status=db_file.status,
            public_url=db_file.public_url,
            message="File uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    user_email: Optional[str] = Form(None),
    video_session_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload multiple files to Google Cloud Storage
    """
    try:
        uploaded_files = []
        
        for file in files:
            file_content = await file.read()
            
            gcs_info = await storage_service.upload_file(
                file_content, 
                file.filename, 
                user_email
            )
            
            file_data = {
                "user_email": user_email,
                "video_session_id": video_session_id,
                "original_filename": gcs_info["original_filename"],
                "gcs_filename": gcs_info["gcs_filename"],
                "bucket_name": gcs_info["bucket_name"],
                "file_size": gcs_info["size"],
                "content_type": gcs_info["content_type"],
                "category": models.FileCategory(gcs_info["category"]),
                "status": models.FileStatus.COMPLETED,
                "gcs_path": gcs_info["gcs_filename"],
                "is_public": False
            }
            
            db_file = crud.create_file(db, file_data)
            uploaded_files.append({
                "id": db_file.id,
                "filename": db_file.original_filename,
                "size": db_file.file_size,
                "status": "uploaded"
            })
        
        # Update video session file count if session is provided
        if video_session_id:
            try:
                session = crud.get_video_session(db, video_session_id)
                if session:
                    total_files = crud.get_files_count_by_video_session(db, video_session_id)
                    crud.update_video_session(db, video_session_id, schemas.VideoSessionUpdate(total_files=total_files))
            except Exception as e:
                print(f"Warning: Could not update session file count: {e}")
        
        return {
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": uploaded_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple file upload failed: {str(e)}")

@router.get("/{file_id}/download", response_model=schemas.FileDownloadResponse)
async def get_download_url(
    file_id: int,
    expiration_minutes: int = 60,
    db: Session = Depends(get_db)
):
    """
    Get signed download URL for file
    """
    try:
        db_file = crud.get_file(db, file_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Generate signed URL
        download_url = storage_service.generate_signed_download_url(
            db_file.gcs_filename, 
            expiration_minutes
        )
        
        # Update download count
        crud.update_file_download_count(db, file_id)
        
        expires_at = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        
        return schemas.FileDownloadResponse(
            id=db_file.id,
            original_filename=db_file.original_filename,
            download_url=download_url,
            expires_at=expires_at,
            file_size=db_file.file_size,
            content_type=db_file.content_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {str(e)}")

@router.get("/", response_model=schemas.FileList)
async def list_files(
    skip: int = 0,
    limit: int = 50,
    user_email: Optional[str] = None,
    category: Optional[models.FileCategory] = None,
    db: Session = Depends(get_db)
):
    """
    List files with pagination and filters
    """
    try:
        if user_email:
            files = crud.get_files_by_user(db, user_email, skip, limit)
            total = crud.get_files_count_by_user(db, user_email)
        elif category:
            files = crud.get_files_by_category(db, category, skip, limit)
            total = crud.get_files_count(db)  # Simplified - could add category count
        else:
            files = crud.get_files(db, skip, limit)
            total = crud.get_files_count(db)
        
        return schemas.FileList(
            files=files,
            total=total,
            page=skip // limit + 1,
            per_page=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.get("/{file_id}", response_model=schemas.File)
async def get_file_info(file_id: int, db: Session = Depends(get_db)):
    """
    Get file information by ID
    """
    db_file = crud.get_file(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@router.put("/{file_id}", response_model=schemas.File)
async def update_file_info(
    file_id: int,
    file_update: schemas.FileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update file metadata
    """
    db_file = crud.update_file(db, file_id, file_update)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@router.delete("/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """
    Delete file from both GCS and database
    """
    try:
        db_file = crud.get_file(db, file_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from GCS
        storage_service.delete_file(db_file.gcs_filename)
        
        # Delete from database
        crud.delete_file(db, file_id)
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")