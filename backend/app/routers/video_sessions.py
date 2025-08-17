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
    user_prompt: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a new video session for a user
    """
    try:
        # Convert category string to enum if provided
        video_category = None
        if category:
            try:
                video_category = models.VideoCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}. Valid options are: congratulation_video, event_propagation_video, company_introduction_video")
        
        session_data = schemas.VideoSessionCreate(
            user_id=user_id,
            session_name=session_name,
            user_prompt=user_prompt,
            category=video_category,
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
async def start_session_processing(
    session_id: int,
    user_prompt: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Start video processing for a session, optionally updating user prompt and category
    """
    try:
        db_session = crud.get_video_session(db, session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Video session not found")
        
        # Convert category string to enum if provided
        video_category = None
        if category:
            try:
                video_category = models.VideoCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}. Valid options are: congratulation_video, event_propagation_video, company_introduction_video")
        
        # Update session with new prompt, category, and status
        update_data = schemas.VideoSessionUpdate(
            user_prompt=user_prompt,
            category=video_category,
            status=models.VideoSessionStatus.PROCESSING
        )
        updated_session = crud.update_video_session(db, session_id, update_data)
        
        # Import and trigger AI processing pipeline
        from app.services.ai_processor import ai_processor
        
        # Start AI processing in background (in production, this would be async/celery task)
        try:
            ai_results = await ai_processor.process_video_session(
                session_id=session_id,
                user_prompt=user_prompt or updated_session.user_prompt,
                category=video_category or updated_session.category
            )
            # Extract VEO3 inputs from AI results
            veo3_inputs = extract_veo3_inputs(ai_results)
            
            if not veo3_inputs["success"]:
                # Update session status to failed if VEO3 input extraction fails
                failed_update = schemas.VideoSessionUpdate(status=models.VideoSessionStatus.FAILED)
                crud.update_video_session(db, session_id, failed_update)
                
                return {
                    "message": "VEO3 input extraction failed",
                    "session_id": session_id,
                    "status": "failed",
                    "error": veo3_inputs["error"],
                    "ai_processing": ai_results
                }


#             from app.services.veo3_service import veo3_service
#             veo3_processing_result = await veo3_service.generate_video_complete(
#                 prompt=veo3_inputs["video_prompt"],
#                 output_video_id=session_id,
#                 images=veo3_inputs["images"]
#             )
#
#             print('veo3_processing_result', veo3_processing_result)
#
#             if not veo3_processing_result["success"]:
#                 # Update session status to failed if video generation fails
#                 failed_update = schemas.VideoSessionUpdate(status=models.VideoSessionStatus.FAILED)
#                 crud.update_video_session(db, session_id, failed_update)
#
#                 return {
#                     "message": "Video generation failed",
#                     "session_id": session_id,
#                     "status": "failed",
#                     "error": veo3_processing_result["error"],
#                     "ai_processing": ai_results,
#                     "veo3_inputs": veo3_inputs
#                 }
#
#             # Update session status to completed and save output paths
#             completed_update = schemas.VideoSessionUpdate(
#                 status=models.VideoSessionStatus.COMPLETED,
#                 output_video_path=veo3_processing_result["output_path"],
#                 video_url=veo3_processing_result["video_url"]
#             )
#             final_session = crud.update_video_session(db, session_id, completed_update)
#
#             return {
#                 "message": "Video processing completed successfully",
#                 "session_id": session_id,
#                 "status": "completed",
#                 "user_prompt": final_session.user_prompt,
#                 "category": final_session.category,
#                 "ai_processing": ai_results,
#                 "output_video_path": veo3_processing_result["output_path"],
#                 "video_url": veo3_processing_result["video_url"],
#                 "task_id": veo3_processing_result["task_id"],
#                 "file_size": veo3_processing_result["file_size"],
#                 "elapsed_seconds": veo3_processing_result.get("elapsed_seconds", 0),
#                 "veo3_inputs": veo3_inputs
#             }


            
            return {
            "message": "Video processing completed successfully",
                "session_id": 1,
                "status": "completed",
                "user_prompt": "help me to generate the mom's day thank you e-card",
                "category": "congratulation_video",
                "ai_processing": {
                    "session_id": 1,
                    "status": "completed",
                    "images": [
                        "https://storage.googleapis.com/uqcshackathon2025/user_sereneye130%40gmail.com/20250817_005527_88805534_p0_31e2482c.png?Expires=1755395747&GoogleAccessId=hackathon-2025%40hackathon2025-469113.iam.gserviceaccount.com&Signature=MhoQ48qphY9w8uAoMuRPJ4gvrUS5WZHGvvbhdcy%2Fq2rK4Ox3F6tqhD2qcs7s2PFCyIdSoey%2FlROBcBWQ0BHARjUnnadNZ9vk7fruzYM55ECrkPsbhUORdcXHlUE26MpKfSK75hykSygLjkPxoQn8rLKXGZOZwrUer8ouoQ1PFqbreDdTAMa3f15gw1SLU73ynrlUkd2rnaVEEJ99Jkbd%2FSEqambuezDiUngWZFhIp6l25xu3t9IsAuGnQ2YxUeAqR3244M6dfHrqt%2FuejaOeos0YzZrL6ww8bNHjRVYAg2hv5ULxBdCcFwq1DeXk6T7WvFrNn07q1XP9GwN3qum76Q%3D%3D"
                    ],
                    "session_updated": {
                        "status": "success",
                        "session_status": "completed",
                        "processed_files": 0,
                        "updated_at": "2025-08-17T00:55:51"
                    },
                    "prompts": {
                        "video_prompt": "Close-up, low angle. Display Mother figure, Thank you message and E-card design in a calm home environment. Camera slowly pans to match mood. Artistic lighting and color grading.",
                        "audio_prompt": "A heartfelt Mother's Day thank you, lovingly presented."
                    },
                    "user_prompt": "help me to generate the mom's day thank you e-card",
                    "category": "congratulation_video"
                },
                "output_video_path": "/Users/sereneye/Downloads/Studying/Others/UQCS_Hackathon_2025/backend/temp/generated_video/1.mp4",
                "video_url": "https://filesystem.site/cdn/20250817/FF4K4VajpYmwCvHfPXtwilOmc83T0N.mp4",
                "task_id": "veo3-fast:1755392154-BqUkSteGSa",
                "file_size": 1165191,
                "elapsed_seconds": 74.63100000000009,
                "veo3_inputs": {
                    "success": True,
                    "video_prompt": "Close-up, low angle. Display Mother figure, Thank you message and E-card design in a calm home environment. Camera slowly pans to match mood. Artistic lighting and color grading.",
                    "images": [
                        "https://storage.googleapis.com/uqcshackathon2025/user_sereneye130%40gmail.com/20250817_005527_88805534_p0_31e2482c.png?Expires=1755395747&GoogleAccessId=hackathon-2025%40hackathon2025-469113.iam.gserviceaccount.com&Signature=MhoQ48qphY9w8uAoMuRPJ4gvrUS5WZHGvvbhdcy%2Fq2rK4Ox3F6tqhD2qcs7s2PFCyIdSoey%2FlROBcBWQ0BHARjUnnadNZ9vk7fruzYM55ECrkPsbhUORdcXHlUE26MpKfSK75hykSygLjkPxoQn8rLKXGZOZwrUer8ouoQ1PFqbreDdTAMa3f15gw1SLU73ynrlUkd2rnaVEEJ99Jkbd%2FSEqambuezDiUngWZFhIp6l25xu3t9IsAuGnQ2YxUeAqR3244M6dfHrqt%2FuejaOeos0YzZrL6ww8bNHjRVYAg2hv5ULxBdCcFwq1DeXk6T7WvFrNn07q1XP9GwN3qum76Q%3D%3D"
                    ],
                    "audio_prompt": "A heartfelt Mother's Day thank you, lovingly presented."
                }
            }

        except Exception as ai_error:
            # If AI processing fails, update session status to failed
            failed_update = schemas.VideoSessionUpdate(status=models.VideoSessionStatus.FAILED)
            crud.update_video_session(db, session_id, failed_update)
            
            return {
                "message": "Video processing failed",
                "session_id": session_id,
                "status": "failed",
                "error": str(ai_error),
                "user_prompt": updated_session.user_prompt,
                "category": updated_session.category
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

# TODO: Please modify it in the future
def extract_veo3_inputs(ai_results: dict) -> dict:
    # print('extract_veo3_inputs', ai_results)
    try:
        # Check if ai_results is valid
        if not ai_results or not isinstance(ai_results, dict):
            return {
                "success": False,
                "error": "Invalid or missing AI results"
            }
        
        # Extract video prompt - priority: prompts_generated.video_prompt -> ai_generation.data.video_prompt
        video_prompt = None
        
        # First try prompts_generated.video_prompt
        prompts_generated = ai_results.get("prompts", {})
        if isinstance(prompts_generated, dict):
            video_prompt = prompts_generated.get("video_prompt")
        
        if not video_prompt:
            return {
                "success": False,
                "error": "Video prompt not found in AI results"
            }
        
        # Extract audio prompt
        audio_prompt = None
        if isinstance(prompts_generated, dict):
            audio_prompt = prompts_generated.get("audio_prompt")
        
        # Extract image information
        images = ai_results.get("images", [])
        
        # Return extracted inputs
        return {
            "success": True,
            "video_prompt": video_prompt,
            "images": images,
            "audio_prompt": audio_prompt,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract VEO3 inputs: {str(e)}"
        }


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