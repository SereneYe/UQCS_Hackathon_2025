import logging
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import models
import crud
import schemas
from database import get_db
from sqlalchemy.orm import Session
from .pdf_service import pdf_service
from .openai_service import openai_service
from .storage_service import storage_service
from .image_service import image_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    """Main AI processing module that orchestrates PDF reading and OpenAI prompt generation"""
    
    def __init__(self):
        self.pdf_service = pdf_service
        self.openai_service = openai_service
        self.storage_service = storage_service
        self.image_service = image_service
    
    async def process_video_session(
        self, 
        session_id: int, 
        user_prompt: Optional[str] = None,
        category: Optional[models.VideoCategory] = None
    ) -> Dict[str, Any]:
        """
        Complete AI processing pipeline for a video session
        
        Args:
            session_id: Video session ID
            user_prompt: User's prompt for video creation
            category: Video category
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Starting AI processing for session {session_id}")
            
            # Get database session
            db = next(get_db())
            
            # Get video session details
            session = crud.get_video_session(db, session_id)
            if not session:
                raise Exception(f"Video session {session_id} not found")
            
            # Use session's prompt and category if not provided
            final_user_prompt = user_prompt or session.user_prompt or "Create a video based on the uploaded documents"
            final_category = category or session.category
            
            logger.info(f"Processing with prompt: '{final_user_prompt}' and category: {final_category}")
            
            # Step 1: Process PDF files
            logger.info("Step 1: Processing PDF files")
            pdf_results = await self._process_session_pdfs(session_id)
            
            # Step 2: Process image files
            logger.info("Step 2: Processing image files")
            image_results = await self._process_session_images(session_id)
            
            # Step 3: Generate AI prompts
            logger.info("Step 3: Generating AI prompts")
            ai_results = await self._generate_ai_prompts(
                final_user_prompt, 
                pdf_results["combined_content"], 
                image_results["images"],
                final_category
            )
            
            # Step 4: Update session with results
            logger.info("Step 4: Updating session with results")
            session_update = await self._update_session_with_results(
                session_id, 
                pdf_results, 
                image_results,
                ai_results,
                final_user_prompt,
                final_category
            )
            
            # Compile final results
            processing_results = {
                "session_id": session_id,
                "status": "completed",
                "pdf_processing": pdf_results,
                "image_processing": image_results,
                "ai_generation": ai_results,
                "session_updated": session_update,
                "prompts_generated": {
                    "video_prompt": ai_results.get("data", {}).get("video_prompt", ""),
                    "audio_prompt": ai_results.get("data", {}).get("audio_prompt", ""),
                    "enhanced_user_prompt": ai_results.get("data", {}).get("enhanced_user_prompt", final_user_prompt)
                },
                "processing_time": datetime.utcnow().isoformat(),
                "user_prompt": final_user_prompt,
                "category": final_category.value if final_category else None
            }
            
            logger.info(f"AI processing completed successfully for session {session_id}")
            return processing_results
            
        except Exception as e:
            logger.error(f"AI processing failed for session {session_id}: {e}")
            
            # Update session status to failed
            try:
                db = next(get_db())
                update_data = schemas.VideoSessionUpdate(status=models.VideoSessionStatus.FAILED)
                crud.update_video_session(db, session_id, update_data)
            except Exception as update_error:
                logger.error(f"Failed to update session status to failed: {update_error}")
            
            return {
                "session_id": session_id,
                "status": "failed",
                "error": str(e),
                "processing_time": datetime.utcnow().isoformat()
            }
    
    async def _process_session_pdfs(self, session_id: int) -> Dict[str, Any]:
        """Process all PDF files in the session"""
        try:
            # Process PDFs using the PDF service
            pdf_contents = await self.pdf_service.process_session_pdfs(session_id)
            
            # Early return for empty PDF list
            if not pdf_contents:
                return {
                    "status": "success",
                    "pdf_files_processed": 0,
                    "pdf_details": [],
                    "combined_content": "",  # Empty string instead of message
                    "total_characters": 0,
                    "successful_extractions": 0,
                    "failed_extractions": 0
                }
            
            # Combine all PDF texts only if there are PDFs
            combined_content = self.pdf_service.combine_pdf_texts(pdf_contents)
            
            return {
                "status": "success",
                "pdf_files_processed": len(pdf_contents),
                "pdf_details": pdf_contents,
                "combined_content": combined_content,
                "total_characters": len(combined_content),
                "successful_extractions": len([pdf for pdf in pdf_contents if pdf["status"] == "success"]),
                "failed_extractions": len([pdf for pdf in pdf_contents if pdf["status"] == "error"])
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "pdf_files_processed": 0,
                "combined_content": "",
                "total_characters": 0
            }
    
    async def _process_session_images(self, session_id: int) -> Dict[str, Any]:
        """Process image file in the session"""
        try:
            # Process image using the image service
            image_result = await self.image_service.process_session_image(session_id)
            
            if image_result["status"] == "success" and image_result["has_image"]:
                images = [image_result["image_url"]]
                return {
                    "status": "success",
                    "has_image": True,
                    "images": images,
                    "image_info": image_result["image_info"]
                }
            else:
                return {
                    "status": "success", 
                    "has_image": False,
                    "images": [],
                    "image_info": None
                }
                
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "has_image": False,
                "images": [],
                "image_info": None
            }
    
    async def _generate_ai_prompts(
        self, 
        user_prompt: str, 
        pdf_content: str, 
        images: list,
        category: Optional[models.VideoCategory]
    ) -> Dict[str, Any]:
        """Generate AI prompts using OpenAI service"""
        try:
            has_pdf = pdf_content and pdf_content.strip() != ""
            has_images = images and len(images) > 0
            
            print('pdf_content', pdf_content)
            if not has_pdf and not has_images:
                # No PDF or image content, use standard prompt analysis
                logger.info("No PDF or image content available, using standard prompt analysis")
                return await self.openai_service.analyze_and_generate_prompts(user_prompt)
            elif has_pdf:
                # Use PDF-enhanced prompt generation (images are passed through separately)
                logger.info(f"Using PDF-enhanced prompt generation")
                res = await self.openai_service.analyze_pdf_content_and_generate_prompts(
                    user_prompt, 
                    pdf_content, 
                    category
                )
                print('res', res)
                return res
            else:
                # Only images, no PDF - use standard prompt analysis
                logger.info("Only images available, using standard prompt analysis")
                return await self.openai_service.analyze_and_generate_prompts(user_prompt)
                
        except Exception as e:
            logger.error(f"AI prompt generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def _update_session_with_results(
        self, 
        session_id: int, 
        pdf_results: Dict[str, Any], 
        image_results: Dict[str, Any],
        ai_results: Dict[str, Any],
        user_prompt: str,
        category: Optional[models.VideoCategory]
    ) -> Dict[str, Any]:
        """Update video session with processing results"""
        try:
            db = next(get_db())
            
            # Determine session status
            if (pdf_results["status"] == "success" and 
                image_results["status"] == "success" and 
                ai_results.get("success", False)):
                new_status = models.VideoSessionStatus.COMPLETED
            else:
                new_status = models.VideoSessionStatus.FAILED
            
            # Update session
            update_data = schemas.VideoSessionUpdate(
                status=new_status,
                user_prompt=user_prompt,
                category=category,
                processed_files=pdf_results.get("successful_extractions", 0)
            )
            
            updated_session = crud.update_video_session(db, session_id, update_data)
            
            if updated_session:
                return {
                    "status": "success",
                    "session_status": new_status.value,
                    "processed_files": pdf_results.get("successful_extractions", 0),
                    "updated_at": updated_session.updated_at.isoformat() if updated_session.updated_at else None
                }
            else:
                return {
                    "status": "failed",
                    "error": "Failed to update session in database"
                }
                
        except Exception as e:
            logger.error(f"Session update failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def get_processing_status(self, session_id: int) -> Dict[str, Any]:
        """Get current processing status of a video session"""
        try:
            db = next(get_db())
            session = crud.get_video_session(db, session_id)
            
            if not session:
                return {
                    "status": "not_found",
                    "error": "Session not found"
                }
            
            files = crud.get_files_by_video_session(db, session_id)
            pdf_files = [f for f in files if f.content_type == "application/pdf"]
            
            return {
                "status": "success",
                "session_id": session_id,
                "session_status": session.status.value,
                "total_files": len(files),
                "pdf_files": len(pdf_files),
                "processed_files": session.processed_files,
                "user_prompt": session.user_prompt,
                "category": session.category.value if session.category else None,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat() if session.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get processing status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Create a global instance
ai_processor = AIProcessor()