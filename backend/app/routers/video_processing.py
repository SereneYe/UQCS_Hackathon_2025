from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db
from app.services.video_service import video_service
from app.services.audio_video_service import audio_video_service

router = APIRouter(
    prefix="/videos",
    tags=["Video Processing"],
    responses={404: {"description": "Not found"}},
)

@router.post("/merge")
async def merge_videos(
    video_paths: List[str],
    output_video_id: int,
    with_transitions: bool = False,
    transition_duration: float = 0.5
):
    """
    Merge multiple videos into one
    """
    try:
        if with_transitions:
            output_path = video_service.merge_videos_with_transition(
                video_paths, output_video_id, transition_duration
            )
        else:
            output_path = video_service.merge_videos(video_paths, output_video_id)
        
        return {
            "message": "Videos merged successfully",
            "output_path": output_path,
            "video_id": output_video_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video merge failed: {str(e)}")

@router.post("/add-audio")
async def add_audio_to_video(
    video_path: str,
    audio_path: str,
    output_video_id: int,
    replace_audio: bool = False,
    audio_start_time: float = 0.0,
    video_start_time: float = 0.0
):
    """
    Add or replace audio in a video file
    """
    try:
        if replace_audio:
            output_path = audio_video_service.replace_audio_in_video(
                video_path, audio_path, output_video_id
            )
        else:
            output_path = audio_video_service.merge_audio_with_video(
                video_path, audio_path, output_video_id, audio_start_time, video_start_time
            )
        
        return {
            "message": "Audio added to video successfully",
            "output_path": output_path,
            "video_id": output_video_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio-video merge failed: {str(e)}")

@router.post("/background-music")
async def add_background_music(
    video_path: str,
    music_path: str,
    output_video_id: int,
    music_volume: float = 0.3,
    original_volume: float = 1.0
):
    """
    Add background music to video while preserving original audio
    """
    try:
        output_path = audio_video_service.add_background_music(
            video_path, music_path, output_video_id, music_volume, original_volume
        )
        
        return {
            "message": "Background music added successfully",
            "output_path": output_path,
            "video_id": output_video_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Background music addition failed: {str(e)}")

@router.post("/extract-audio")
async def extract_audio_from_video(
    video_path: str,
    output_audio_id: int,
    audio_format: str = "mp3"
):
    """
    Extract audio track from video file
    """
    try:
        output_path = audio_video_service.extract_audio_from_video(
            video_path, output_audio_id, audio_format
        )
        
        return {
            "message": "Audio extracted successfully",
            "output_path": output_path,
            "audio_id": output_audio_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio extraction failed: {str(e)}")

@router.get("/{video_id}/info")
async def get_video_info(video_path: str):
    """
    Get video file information (duration, resolution, etc.)
    """
    try:
        info = video_service.get_video_info(video_path)
        return {"video_info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get video info: {str(e)}")