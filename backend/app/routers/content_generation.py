from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db
from app.services.openai_service import openai_service
from app.services.veo3_service import veo3_service

router = APIRouter(
    prefix="/content-generation",
    tags=["Content Generation"],
    responses={404: {"description": "Not found"}},
)

# Request/Response Models
class ContentAnalysisRequest(BaseModel):
    user_input: str = Field(..., description="User's input text/prompt", min_length=1, max_length=5000)
    user_context: Optional[str] = Field(None, description="Optional additional context", max_length=2000)

class PromptAnalysis(BaseModel):
    main_theme: str
    key_elements: list[str]
    style_preference: str
    mood: str

class ContentAnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[PromptAnalysis] = None
    video_prompt: Optional[str] = None
    audio_prompt: Optional[str] = None
    raw_response: Optional[str] = None
    usage: Optional[dict] = None
    warning: Optional[str] = None
    error: Optional[str] = None

class PromptRefinementRequest(BaseModel):
    original_prompt: str = Field(..., description="Original prompt to refine", min_length=1)
    user_feedback: str = Field(..., description="User feedback for refinement", min_length=1, max_length=1000)
    prompt_type: str = Field(..., description="Type of prompt: 'video' or 'audio'")

class PromptRefinementResponse(BaseModel):
    success: bool
    refined_prompt: Optional[str] = None
    original_prompt: Optional[str] = None
    user_feedback: Optional[str] = None
    error: Optional[str] = None

class VideoGenerationRequest(BaseModel):
    video_prompt: str = Field(..., description="Video generation prompt", min_length=1, max_length=2000)
    output_video_id: int = Field(..., description="ID for the output video file")
    model: str = Field("veo3-fast", description="VEO3 model to use")
    enhance_prompt: bool = Field(True, description="Whether to enhance the prompt")
    image_url: Optional[str] = Field(None, description="Optional image URL for image-to-video generation")

class VideoGenerationResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    task_id: Optional[str] = None
    output_path: Optional[str] = None
    file_size: Optional[int] = None
    video_url: Optional[str] = None
    video_id: Optional[int] = None
    elapsed_seconds: Optional[float] = None
    error: Optional[str] = None

class CompleteWorkflowRequest(BaseModel):
    user_input: str = Field(..., description="User's input text/prompt", min_length=1, max_length=5000)
    user_context: Optional[str] = Field(None, description="Optional additional context", max_length=2000)
    output_video_id: int = Field(..., description="ID for the output video file")
    veo3_model: str = Field("veo3-fast", description="VEO3 model to use")
    enhance_prompt: bool = Field(True, description="Whether to enhance the video prompt")
    image_url: Optional[str] = Field(None, description="Optional image URL for image-to-video generation")

class CompleteWorkflowResponse(BaseModel):
    success: bool
    analysis: Optional[PromptAnalysis] = None
    video_prompt: Optional[str] = None
    audio_prompt: Optional[str] = None
    video_generation: Optional[VideoGenerationResponse] = None
    error: Optional[str] = None

@router.post("/analyze", response_model=ContentAnalysisResponse)
async def analyze_content_and_generate_prompts(
    request: ContentAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze user input content and generate video and audio prompts using OpenAI
    
    This endpoint:
    1. Takes user input text/prompt
    2. Uses OpenAI GPT to analyze the content
    3. Generates specialized prompts for video generation (VEO3) and audio generation (TTS)
    4. Returns structured analysis and both prompts
    """
    try:
        # Call OpenAI service to analyze and generate prompts
        result = await openai_service.analyze_and_generate_prompts(
            user_input=request.user_input,
            user_context=request.user_context
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to analyze content: {result.get('error', 'Unknown error')}"
            )
        
        # Extract data from result
        data = result["data"]
        
        # Structure the response
        response = ContentAnalysisResponse(
            success=True,
            analysis=PromptAnalysis(**data["analysis"]) if data and "analysis" in data else None,
            video_prompt=data.get("video_prompt") if data else None,
            audio_prompt=data.get("audio_prompt") if data else None,
            raw_response=result.get("raw_response"),
            usage=result.get("usage"),
            warning=result.get("warning")
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error during content analysis: {str(e)}"
        )

@router.post("/refine-prompt", response_model=PromptRefinementResponse)
async def refine_prompt(
    request: PromptRefinementRequest,
    db: Session = Depends(get_db)
):
    """
    Refine a generated prompt based on user feedback
    
    This endpoint allows users to provide feedback on generated prompts
    and get refined versions using OpenAI
    """
    try:
        if request.prompt_type not in ["video", "audio"]:
            raise HTTPException(
                status_code=400,
                detail="prompt_type must be either 'video' or 'audio'"
            )
        
        # Call appropriate refinement service
        if request.prompt_type == "video":
            result = await openai_service.refine_video_prompt(
                original_prompt=request.original_prompt,
                user_feedback=request.user_feedback
            )
        else:  # audio
            result = await openai_service.refine_audio_prompt(
                original_prompt=request.original_prompt,
                user_feedback=request.user_feedback
            )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to refine prompt: {result.get('error', 'Unknown error')}"
            )
        
        return PromptRefinementResponse(
            success=True,
            refined_prompt=result["refined_prompt"],
            original_prompt=result["original_prompt"],
            user_feedback=result["user_feedback"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during prompt refinement: {str(e)}"
        )

@router.post("/generate-video", response_model=VideoGenerationResponse)
async def generate_video_only(
    request: VideoGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate video using VEO3 with provided prompt
    
    This endpoint takes a video prompt and generates a video using VEO3 API
    """
    try:
        result = await veo3_service.generate_video_complete(
            prompt=request.video_prompt,
            output_video_id=request.output_video_id,
            model=request.model,
            enhance_prompt=request.enhance_prompt,
            image_url=request.image_url
        )
        
        return VideoGenerationResponse(**result)
        
    except Exception as e:
        return VideoGenerationResponse(
            success=False,
            error=f"Video generation failed: {str(e)}",
            video_id=request.output_video_id
        )

@router.post("/complete-workflow", response_model=CompleteWorkflowResponse)
async def complete_content_generation_workflow(
    request: CompleteWorkflowRequest,
    db: Session = Depends(get_db)
):
    """
    Complete workflow: Analyze user input -> Generate prompts -> Create video
    
    This endpoint:
    1. Analyzes user input with OpenAI
    2. Generates video and audio prompts
    3. Creates video using VEO3 with the generated video prompt
    4. Returns both prompts and video generation result
    """
    try:
        # Step 1: Analyze content and generate prompts
        analysis_result = await openai_service.analyze_and_generate_prompts(
            user_input=request.user_input,
            user_context=request.user_context
        )
        
        if not analysis_result["success"]:
            return CompleteWorkflowResponse(
                success=False,
                error=f"Content analysis failed: {analysis_result.get('error', 'Unknown error')}"
            )
        
        data = analysis_result["data"]
        video_prompt = data.get("video_prompt")
        audio_prompt = data.get("audio_prompt")
        
        if not video_prompt:
            return CompleteWorkflowResponse(
                success=False,
                error="Failed to generate video prompt from analysis"
            )
        
        # Step 2: Generate video using VEO3
        video_result = await veo3_service.generate_video_complete(
            prompt=video_prompt,
            output_video_id=request.output_video_id,
            model=request.veo3_model,
            enhance_prompt=request.enhance_prompt,
            image_url=request.image_url
        )
        
        # Prepare response
        response = CompleteWorkflowResponse(
            success=video_result["success"],
            analysis=PromptAnalysis(**data["analysis"]) if "analysis" in data else None,
            video_prompt=video_prompt,
            audio_prompt=audio_prompt,
            video_generation=VideoGenerationResponse(**video_result)
        )
        
        if not video_result["success"]:
            response.error = f"Video generation failed: {video_result.get('error', 'Unknown error')}"
        
        return response
        
    except Exception as e:
        return CompleteWorkflowResponse(
            success=False,
            error=f"Complete workflow failed: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for content generation service
    """
    try:
        # Test OpenAI service
        openai_healthy = bool(openai_service.api_key)
        
        # Test VEO3 service
        veo3_healthy = bool(veo3_service.api_key)
        
        if openai_healthy and veo3_healthy:
            status = "healthy"
            message = "All content generation services are operational"
        elif openai_healthy:
            status = "partial"
            message = "OpenAI service operational, VEO3 service not configured"
        elif veo3_healthy:
            status = "partial"
            message = "VEO3 service operational, OpenAI service not configured"
        else:
            status = "unhealthy"
            message = "No services configured properly"
        
        return {
            "status": status,
            "message": message,
            "service": "content-generation",
            "services": {
                "openai": {
                    "configured": openai_healthy,
                    "model": openai_service.model if openai_healthy else None
                },
                "veo3": {
                    "configured": veo3_healthy,
                    "base_url": veo3_service.base_url if veo3_healthy else None
                }
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Service error: {str(e)}",
            "service": "content-generation"
        }
