import os
import sys
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.storage_service import storage_service
import crud
import models

class IntegrationService:
    """
    Service to integrate file storage with existing audio/video processing
    """
    
    def __init__(self):
        pass
    
    async def upload_processed_file_to_gcs(
        self,
        local_file_path: str,
        user_email: Optional[str] = None,
        file_type: str = "processed",
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a processed file (audio/video) to GCS and create database record
        
        Args:
            local_file_path: Path to the local file
            user_email: User email for file association
            file_type: Type of file (audio, video, processed, etc.)
            description: Optional description
            
        Returns:
            Dictionary with file info and GCS details
        """
        try:
            # Check if file exists
            if not os.path.exists(local_file_path):
                raise FileNotFoundError(f"Local file not found: {local_file_path}")
            
            # Generate filename based on file type and timestamp
            filename = os.path.basename(local_file_path)
            
            # Upload to GCS
            gcs_info = storage_service.upload_local_file(
                local_file_path,
                user_email,
                filename
            )
            
            return {
                "success": True,
                "local_path": local_file_path,
                "gcs_info": gcs_info,
                "message": f"File uploaded to GCS successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "local_path": local_file_path,
                "message": f"Failed to upload file to GCS: {str(e)}"
            }
    
    async def backup_audio_files_to_gcs(
        self,
        db: Session,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Backup existing audio files to GCS
        """
        try:
            # Get audio files to backup
            if user_email:
                audio_files = crud.get_audios_by_user_email(db, user_email)
            else:
                audio_files = crud.get_audios(db, limit=1000)  # Limit for safety
            
            uploaded_count = 0
            failed_count = 0
            results = []
            
            for audio in audio_files:
                if audio.file_path and os.path.exists(audio.file_path):
                    try:
                        result = await self.upload_processed_file_to_gcs(
                            audio.file_path,
                            audio.user_email,
                            "audio",
                            f"TTS Audio - {audio.text_input[:50]}..."
                        )
                        
                        if result["success"]:
                            uploaded_count += 1
                        else:
                            failed_count += 1
                        
                        results.append({
                            "audio_id": audio.id,
                            "result": result
                        })
                        
                    except Exception as e:
                        failed_count += 1
                        results.append({
                            "audio_id": audio.id,
                            "result": {
                                "success": False,
                                "error": str(e)
                            }
                        })
            
            return {
                "success": True,
                "uploaded_count": uploaded_count,
                "failed_count": failed_count,
                "total_processed": len(results),
                "details": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to backup audio files: {str(e)}"
            }
    
    async def cleanup_local_files_after_gcs_upload(
        self,
        local_file_path: str,
        keep_local: bool = True
    ) -> bool:
        """
        Optionally clean up local files after successful GCS upload
        
        Args:
            local_file_path: Path to local file
            keep_local: Whether to keep the local file (default: True for safety)
            
        Returns:
            True if cleanup successful or skipped, False if failed
        """
        try:
            if not keep_local and os.path.exists(local_file_path):
                os.remove(local_file_path)
                return True
            return True  # Skipped cleanup
            
        except Exception as e:
            print(f"Failed to cleanup local file {local_file_path}: {e}")
            return False

# Create global integration service instance
integration_service = IntegrationService()