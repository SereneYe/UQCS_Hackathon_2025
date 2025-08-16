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
            
            # Import VEO3 service and generate video
            # from app.services.veo3_service import veo3_service
            #
            # veo3_result = await veo3_service.generate_video_complete(
            #     prompt=veo3_inputs["video_prompt"],
            #     output_video_id=session_id,  # Use session_id as video_id
            #     model="veo3-fast",
            #     enhance_prompt=False,  # AI already enhanced the prompt
            #     image_url=veo3_inputs["image_url"],
            #     format="mp4"
            # )
            #
            # print("VEO3 Result:", veo3_result)
            #
            # if veo3_result["success"]:
            #     # Update session status to completed
            #     success_update = schemas.VideoSessionUpdate(
            #         status=models.VideoSessionStatus.COMPLETED,
            #         output_video_path=veo3_result["output_path"]
            #     )
            #     updated_session = crud.update_video_session(db, session_id, success_update)
            #
            #     return {
            #         "message": "Video processing completed successfully",
            #         "session_id": session_id,
            #         "status": "completed",
            #         "user_prompt": updated_session.user_prompt,
            #         "category": updated_session.category,
            #         "ai_processing": ai_results,
            #         "veo3_processing": veo3_result,
            #         "output_video_path": veo3_result["output_path"],
            #         "video_url": veo3_result.get("video_url"),
            #         "task_id": veo3_result.get("task_id"),
            #         "prompts_generated": ai_results.get("prompts_generated", {})
            #     }
            # else:
            #     # Update session status to failed
            #     failed_update = schemas.VideoSessionUpdate(status=models.VideoSessionStatus.FAILED)
            #     crud.update_video_session(db, session_id, failed_update)
            #
            #     return {
            #         "message": "VEO3 video generation failed",
            #         "session_id": session_id,
            #         "status": "failed",
            #         "error": veo3_result.get("error"),
            #         "ai_processing": ai_results,
            #         "veo3_error": veo3_result
            #     }

            # Remove the following fake return when doing the testing
            return {
                "message": "Video processing completed successfully",
                "session_id": session_id,
                "status": "completed",
                "user_prompt": updated_session.user_prompt,
                "category": updated_session.category,
                "ai_processing": ai_results,
                "output_video_path": "/Users/sereneye/Downloads/Studying/Others/UQCS_Hackathon_2025/backend/temp/generated_video/8.mp4",
                "video_url": "https://filesystem.site/cdn/20250816/RE33nHoQGQ6UlmNYmouXmQAy0kwZi8.mp4",
                "task_id": "veo3-fast:1755347551-WBOLccEf3c",
                "prompts_generated": ai_results.get("prompts_generated", {})
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
        prompts_generated = ai_results.get("prompts_generated", {})
        if isinstance(prompts_generated, dict):
            video_prompt = prompts_generated.get("video_prompt")
        
        # Fallback to ai_generation.data.video_prompt
        if not video_prompt:
            ai_generation = ai_results.get("ai_generation", {})
            if isinstance(ai_generation, dict) and ai_generation.get("data"):
                video_prompt = ai_generation["data"].get("video_prompt")
        
        if not video_prompt:
            return {
                "success": False,
                "error": "Video prompt not found in AI results"
            }
        
        # Extract audio prompt
        audio_prompt = None
        if isinstance(prompts_generated, dict):
            audio_prompt = prompts_generated.get("audio_prompt")
        
        # Fallback to ai_generation.data.audio_prompt
        if not audio_prompt:
            ai_generation = ai_results.get("ai_generation", {})
            if isinstance(ai_generation, dict) and ai_generation.get("data"):
                audio_prompt = ai_generation["data"].get("audio_prompt")
        
        # Extract enhanced user prompt
        enhanced_user_prompt = None
        if isinstance(prompts_generated, dict):
            enhanced_user_prompt = prompts_generated.get("enhanced_user_prompt")
        
        # Extract analysis
        analysis = None
        ai_generation = ai_results.get("ai_generation", {})
        if isinstance(ai_generation, dict) and ai_generation.get("data"):
            analysis = ai_generation["data"].get("analysis")
        
        # Extract image information
        image_url = None
        has_image = False
        
        image_processing = ai_results.get("image_processing", {})
        if isinstance(image_processing, dict):
            has_image = image_processing.get("has_image", False)
            
            if has_image:
                image_info = image_processing.get("image_info", {})
                if isinstance(image_info, dict):
                    # Use public_url if available
                    if image_info.get("public_url"):
                        image_url = image_info["public_url"]
                    # Otherwise construct download URL using file_id
                    elif image_info.get("file_id"):
                        file_id = image_info["file_id"]
                        image_url = f"/api/files/{file_id}/download"
        
        # Return extracted inputs
        return {
            "success": True,
            "video_prompt": video_prompt,
            "image_url": image_url,
            "audio_prompt": audio_prompt,
            "enhanced_user_prompt": enhanced_user_prompt,
            "analysis": analysis,
            "has_image": has_image
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