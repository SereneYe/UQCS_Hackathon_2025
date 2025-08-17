import os
import sys
import asyncio
import aiohttp
import aiofiles
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import VEO3_MODEL_FRAMES, get_video_file_path, ensure_temp_directories

# Load environment variables
load_dotenv()

class VEO3Service:
    """
    VEO3 AI video generation service
    Handles video creation, status polling, and file download
    """
    
    def __init__(self):
        self.api_key = os.getenv("VEO3_API_KEY")
        self.base_url = os.getenv("VEO3_BASE_URL", "https://api.qingyuntop.top")
        self.create_url = f"{self.base_url}/v1/video/create"
        self.query_url = f"{self.base_url}/v1/video/query"
        
        # Configuration
        self.poll_interval_seconds = 5
        self.max_wait_seconds = 15 * 60  # 15 minutes
        self.timeout_seconds = 30
        
        ensure_temp_directories()
    
    def _extract_task_id(self, response_data: Dict[str, Any]) -> Optional[str]:
        """Extract task ID from create response"""
        if not response_data:
            return None
        
        if isinstance(response_data, str):
            return response_data
        
        # Try multiple possible locations for task ID
        candidates = [
            response_data.get("data", {}).get("id"),
            response_data.get("id"),
            response_data.get("result", {}).get("id"),
            response_data.get("task_id"),
            response_data.get("data", {}).get("task_id"),
            response_data.get("detail", {}).get("id"),
        ]
        
        # Return first non-empty value
        for candidate in candidates:
            if candidate:
                return str(candidate)
        
        return None
    
    def _extract_status_info(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract status information from query response"""
        data = response_data.get("data", {}) if response_data else {}
        result = response_data.get("result", {}) if response_data else {}
        detail = response_data.get("detail", {}) if response_data else {}
        
        # Extract status
        status = (
            data.get("status") or
            response_data.get("status") or
            result.get("status") or
            detail.get("status")
        )
        
        # Extract video URL
        video_url = (
            data.get("url") or
            data.get("video_url") or
            data.get("video") or
            response_data.get("url") or
            result.get("url") or
            result.get("video_url") or
            response_data.get("video_url") or
            detail.get("video_url") or
            detail.get("url")
        )
        
        # Extract progress
        progress = (
            data.get("progress") or
            response_data.get("progress") or
            result.get("progress") or
            detail.get("progress")
        )
        
        # Extract error message
        error_msg = (
            data.get("error") or
            response_data.get("error") or
            result.get("error") or
            detail.get("error")
        )
        
        return {
            "status": status,
            "video_url": video_url,
            "progress": progress,
            "error_msg": error_msg
        }
    
    async def _make_request(self, session: aiohttp.ClientSession, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with proper headers and error handling"""
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        
        kwargs.setdefault('headers', {}).update(headers)
        kwargs.setdefault('timeout', aiohttp.ClientTimeout(total=self.timeout_seconds))
        
        async with session.request(method, url, **kwargs) as response:
            return await response.json()
    
    async def create_video_task(
        self,
        prompt: str,
        model: str = VEO3_MODEL,
        enhance_prompt: bool = True,
        images: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a video generation task
        
        Args:
            prompt: Video generation prompt
            model: VEO3 model to use (veo3-fast, veo3-quality, etc.)
            enhance_prompt: Whether to enhance the prompt
            image_url: Optional image URL for image-to-video generation
            
        Returns:
            Dictionary containing task creation result
        """
        if not self.api_key:
            raise ValueError("VEO3 API key not found. Please set VEO3_API_KEY environment variable.")
        
        try:
            payload = {
                "prompt": prompt,
                "model": model,
                "enhance_prompt": enhance_prompt
            }
            
            # Add image URL if provided
            if images:
                payload["images"] = images
                payload["model"] = VEO3_MODEL_FRAMES   
                
            async with aiohttp.ClientSession() as session:
                
                response_data = await self._make_request(
                    session, 'POST', self.create_url, json=payload
                )
                
                task_id = self._extract_task_id(response_data)
                
                if not task_id:
                    return {
                        "success": False,
                        "error": f"Failed to extract task ID from response: {response_data}",
                        "response_data": response_data
                    }
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "prompt": prompt,
                    "model": model,
                    "response_data": response_data
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create video task: {str(e)}",
                "prompt": prompt,
                "model": model
            }
    
    async def poll_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Poll task status until completion or timeout
        
        Args:
            task_id: Task ID from create_video_task
            
        Returns:
            Dictionary containing final status and video URL if successful
        """
        if not self.api_key:
            raise ValueError("VEO3 API key not found. Please set VEO3_API_KEY environment variable.")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with aiohttp.ClientSession() as session:
                while True:
                    # Check timeout
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > self.max_wait_seconds:
                        return {
                            "success": False,
                            "error": f"Task polling timeout after {self.max_wait_seconds} seconds",
                            "task_id": task_id,
                            "elapsed_seconds": elapsed
                        }
                    
                    try:
                        # Query task status
                        query_url = f"{self.query_url}?id={task_id}"
                        response_data = await self._make_request(session, 'GET', query_url)
                        
                        status_info = self._extract_status_info(response_data)
                        status = status_info.get("status", "").lower()
                        
                        # Check for completion
                        if status in ['succeeded', 'finished', 'complete', 'completed', 'done', 'ok', 'success']:
                            video_url = status_info.get("video_url")
                            
                            if not video_url:
                                # Try alternative extraction methods
                                video_url = (
                                    response_data.get("video_url") or
                                    response_data.get("detail", {}).get("video_url") or
                                    response_data.get("detail", {}).get("url") or
                                    response_data.get("data", {}).get("video_url") or
                                    response_data.get("data", {}).get("url") or
                                    response_data.get("url")
                                )
                            
                            if video_url:
                                return {
                                    "success": True,
                                    "status": "completed",
                                    "video_url": video_url,
                                    "task_id": task_id,
                                    "elapsed_seconds": elapsed,
                                    "response_data": response_data
                                }
                            else:
                                return {
                                    "success": False,
                                    "error": "Task completed but no video URL found",
                                    "task_id": task_id,
                                    "response_data": response_data
                                }
                        
                        # Check for failure
                        if status in ['failed', 'error', 'cancelled', 'canceled']:
                            error_msg = status_info.get("error_msg", "Unknown error")
                            return {
                                "success": False,
                                "error": f"Task failed: {error_msg}",
                                "status": status,
                                "task_id": task_id,
                                "response_data": response_data
                            }
                        
                        # Log progress if available
                        progress = status_info.get("progress")
                        if progress is not None:
                            print(f"Task {task_id} progress: {progress}%")
                        
                        if status:
                            print(f"Task {task_id} status: {status}")
                    
                    except Exception as poll_error:
                        print(f"Polling error (will retry): {poll_error}")
                    
                    # Wait before next poll
                    await asyncio.sleep(self.poll_interval_seconds)
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Polling failed: {str(e)}",
                "task_id": task_id
            }
    
    async def download_video(self, video_url: str, output_video_id: int, format: str = "mp4") -> Dict[str, Any]:
        """
        Download video from URL to local file
        
        Args:
            video_url: URL of the generated video
            output_video_id: ID for the output video file
            format: Video format (default: mp4)
            
        Returns:
            Dictionary containing download result
        """
        try:
            output_path = get_video_file_path(output_video_id, format)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    video_url, 
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes for download
                ) as response:
                    response.raise_for_status()
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Download file
                    async with aiofiles.open(output_path, 'wb') as file:
                        async for chunk in response.content.iter_chunked(8192):
                            await file.write(chunk)
            
            # Get file size
            file_size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "output_path": output_path,
                "file_size": file_size,
                "video_url": video_url,
                "video_id": output_video_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to download video: {str(e)}",
                "video_url": video_url,
                "video_id": output_video_id
            }
    
    async def generate_video_complete(
        self,
        prompt: str,
        output_video_id: int,
        model: str = VEO3_MODEL,
        enhance_prompt: bool = True,
        images: Optional[list] = None,
        format: str = "mp4"
    ) -> Dict[str, Any]:
        """
        Complete video generation workflow: create task -> poll status -> download video
        
        Args:
            prompt: Video generation prompt
            output_video_id: ID for the output video file
            model: VEO3 model to use
            enhance_prompt: Whether to enhance the prompt
            images: Optional image URL for image-to-video generation
            format: Output video format
            
        Returns:
            Dictionary containing complete generation result
        """
        try:
            # Step 1: Create task
            print(f"Creating video task with prompt: {prompt[:100]}...")
            create_result = await self.create_video_task(
                prompt=prompt,
                model=model,
                enhance_prompt=enhance_prompt,
                images=images
            )
            
            if not create_result["success"]:
                return create_result
            
            task_id = create_result["task_id"]
            print(f"Task created successfully. Task ID: {task_id}")
            
            # Step 2: Poll status
            print("Polling task status...")
            poll_result = await self.poll_task_status(task_id)
            
            if not poll_result["success"]:
                return poll_result
            
            video_url = poll_result["video_url"]
            print(f"Video generation completed. URL: {video_url}")
            
            # Step 3: Download video
            print("Downloading video...")
            download_result = await self.download_video(video_url, output_video_id, format)
            
            if not download_result["success"]:
                return download_result
            
            print(f"Video downloaded to: {download_result['output_path']}")
            
            # Return complete result
            return {
                "success": True,
                "message": "Video generated successfully",
                "task_id": task_id,
                "output_path": download_result["output_path"],
                "file_size": download_result["file_size"],
                "video_url": video_url,
                "video_id": output_video_id,
                "prompt": prompt,
                "model": model,
                "elapsed_seconds": poll_result.get("elapsed_seconds", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Video generation workflow failed: {str(e)}",
                "prompt": prompt,
                "video_id": output_video_id
            }

# Create a global VEO3 service instance
veo3_service = VEO3Service()
