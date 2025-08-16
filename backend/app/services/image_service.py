import logging
from typing import Optional, Dict, Any
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import models
import crud
from database import get_db
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Service for processing image files for video sessions"""
    
    def __init__(self):
        pass
    
    async def get_session_image_url(self, session_id: int) -> Optional[str]:
        """
        Get the public URL for the image associated with a video session
        
        Args:
            session_id: Video session ID
            
        Returns:
            Public URL of the image if exists, None otherwise
        """
        try:
            # Get database session
            db = next(get_db())
            
            # Get all files for this session
            files = crud.get_files_by_video_session(db, session_id)
            
            # Find the first (and should be only) image file
            for file in files:
                if file.content_type and file.content_type.startswith("image/"):
                    logger.info(f"Found image file for session {session_id}: {file.original_filename}")
                    return file.public_url
            
            logger.info(f"No image file found for session {session_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session image URL: {e}")
            return None
    
    async def process_session_image(self, session_id: int) -> Dict[str, Any]:
        """
        Process image file for a video session and return metadata
        
        Args:
            session_id: Video session ID
            
        Returns:
            Dictionary with image processing results
        """
        try:
            # Get database session
            db = next(get_db())
            
            # Get all files for this session
            files = crud.get_files_by_video_session(db, session_id)
            
            # Find image files (should be at most one)
            image_files = [f for f in files if f.content_type and f.content_type.startswith("image/")]
            
            if not image_files:
                logger.info(f"No image files found for session {session_id}")
                return {
                    "status": "success",
                    "has_image": False,
                    "image_url": None,
                    "image_info": None
                }
            
            if len(image_files) > 1:
                logger.warning(f"Multiple image files found for session {session_id}, using the first one")
            
            # Use the first (and should be only) image
            image_file = image_files[0]
            
            logger.info(f"Processing image file: {image_file.original_filename}")
            
            image_info = {
                "file_id": image_file.id,
                "filename": image_file.original_filename,
                "content_type": image_file.content_type,
                "file_size": image_file.file_size,
                "public_url": image_file.public_url,
                "created_at": image_file.created_at.isoformat() if image_file.created_at else None
            }
            
            return {
                "status": "success",
                "has_image": True,
                "image_url": image_file.public_url,
                "image_info": image_info
            }
            
        except Exception as e:
            logger.error(f"Failed to process session image: {e}")
            return {
                "status": "error",
                "error": str(e),
                "has_image": False,
                "image_url": None,
                "image_info": None
            }

# Create a global instance
image_service = ImageProcessor()