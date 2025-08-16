import os
import sys
import uuid
import mimetypes
from datetime import datetime, timedelta
from typing import Optional, List, BinaryIO
from pathlib import Path
from google.cloud import storage
from google.oauth2 import service_account
import json

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import (
    GCP_BUCKET_NAME, 
    GCP_PROJECT_ID, 
    MAX_FILE_SIZE, 
    ALLOWED_EXTENSIONS,
    ALLOWED_AUDIO_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    ALLOWED_IMAGE_EXTENSIONS
)

class StorageService:
    """
    Google Cloud Storage service for file upload and download operations
    """
    
    def __init__(self):
        self.client = self._create_storage_client()
        self.bucket_name = GCP_BUCKET_NAME
        self.bucket = self.client.bucket(self.bucket_name)
    
    def _create_storage_client(self):
        """
        Create GCS client using environment variables for authentication
        Uses same credential logic as TTS service
        """
        # Option 1: Use GOOGLE_APPLICATION_CREDENTIALS file path
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            return storage.Client()
        
        # Option 2: Use service account key content from env var
        service_account_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")
        if service_account_key:
            try:
                service_account_info = json.loads(service_account_key)
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info
                )
                return storage.Client(credentials=credentials, project=GCP_PROJECT_ID)
            except json.JSONDecodeError:
                raise ValueError("Invalid GOOGLE_SERVICE_ACCOUNT_KEY format")
        
        # Option 3: Try default credentials
        try:
            return storage.Client(project=GCP_PROJECT_ID)
        except Exception as e:
            raise ValueError(
                "Google Cloud credentials not found. Please set either:\n"
                "1. GOOGLE_APPLICATION_CREDENTIALS environment variable\n"
                "2. GOOGLE_SERVICE_ACCOUNT_KEY environment variable\n"
                f"Error: {str(e)}"
            )
    
    def validate_file(self, filename: str, file_size: int) -> None:
        """
        Validate file extension and size
        """
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type {file_ext} not allowed. Allowed types: {ALLOWED_EXTENSIONS}")
        
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size {file_size} exceeds maximum allowed size {MAX_FILE_SIZE}")
    
    def get_file_category(self, filename: str) -> str:
        """
        Determine file category based on extension
        """
        file_ext = Path(filename).suffix.lower()
        
        if file_ext in ALLOWED_AUDIO_EXTENSIONS:
            return "audio"
        elif file_ext in ALLOWED_VIDEO_EXTENSIONS:
            return "video"
        elif file_ext in ALLOWED_IMAGE_EXTENSIONS:
            return "image"
        else:
            return "other"
    
    def generate_unique_filename(self, original_filename: str, user_id: Optional[int] = None) -> str:
        """
        Generate unique filename with timestamp and UUID
        """
        file_ext = Path(original_filename).suffix
        file_stem = Path(original_filename).stem
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if user_id:
            return f"user_{user_id}/{timestamp}_{file_stem}_{unique_id}{file_ext}"
        else:
            return f"public/{timestamp}_{file_stem}_{unique_id}{file_ext}"
    
    def generate_signed_upload_url(
        self,
        original_filename: str,
        file_size: int,
        content_type: str,
        user_id: Optional[int] = None,
        expires_minutes: int = 10,
    ) -> dict:
        """
        Generate signed URL for secure file upload
        Returns:
          {
            "original_filename": "...",
            "gcs_filename": "...",
            "url": "https://storage.googleapis.com/...",
            "method": "PUT",
            "headers": {"Content-Type": "..."},
            "expiresAt": "ISO time"
          }
        """
        self.validate_file(original_filename, file_size)

        gcs_filename = self.generate_unique_filename(original_filename, user_id)
        blob = self.bucket.blob(gcs_filename)

        expiration = datetime.utcnow() + timedelta(minutes=expires_minutes)

        # Only allow PUT requests for 10 minutes
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="PUT",
            content_type=content_type or "application/octet-stream",
        )

        return {
            "original_filename": original_filename,
            "gcs_filename": gcs_filename,
            "bucket_name": self.bucket_name,
            "url": signed_url,
            "method": "PUT",
            "headers": {"Content-Type": content_type or "application/octet-stream"},
            "expiresAt": expiration.isoformat() + "Z",
        }

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: Optional[int] = None,
        content_type: Optional[str] = None
    ) -> dict:
        """
        Upload file to Google Cloud Storage
        
        Returns:
            dict: File information including GCS path and public URL
        """
        # Validate file
        self.validate_file(filename, len(file_content))
        
        # Generate unique filename
        gcs_filename = self.generate_unique_filename(filename, user_id)
        
        # Determine content type
        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = "application/octet-stream"
        
        try:
            # Create blob and upload
            blob = self.bucket.blob(gcs_filename)
            blob.upload_from_string(
                file_content,
                content_type=content_type
            )
            
            # Make blob publicly readable (optional)
            # blob.make_public()
            
            file_info = {
                "original_filename": filename,
                "gcs_filename": gcs_filename,
                "bucket_name": self.bucket_name,
                "size": len(file_content),
                "content_type": content_type,
                "category": self.get_file_category(filename),
                "public_url": f"https://storage.googleapis.com/{self.bucket_name}/{gcs_filename}",
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
            return file_info
            
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to GCS: {str(e)}")
    
    def upload_local_file(
        self,
        local_file_path: str,
        user_id: Optional[int] = None,
        custom_filename: Optional[str] = None
    ) -> dict:
        """
        Upload local file to GCS
        """
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file not found: {local_file_path}")
        
        filename = custom_filename or os.path.basename(local_file_path)
        
        with open(local_file_path, 'rb') as f:
            file_content = f.read()
        
        return self.upload_file(file_content, filename, user_id)
    
    def generate_signed_download_url(
        self,
        gcs_filename: str,
        expiration_minutes: int = 60
    ) -> str:
        """
        Generate signed URL for secure file download
        """
        try:
            blob = self.bucket.blob(gcs_filename)
            
            # Generate signed URL valid for specified minutes
            expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method="GET"
            )
            
            return signed_url
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate signed URL: {str(e)}")
    
    def delete_file(self, gcs_filename: str) -> bool:
        """
        Delete file from GCS
        """
        try:
            blob = self.bucket.blob(gcs_filename)
            blob.delete()
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to delete file from GCS: {str(e)}")
    
    def file_exists(self, gcs_filename: str) -> bool:
        """
        Check if file exists in GCS
        """
        try:
            blob = self.bucket.blob(gcs_filename)
            return blob.exists()
        except Exception:
            return False
    
    def list_files(self, prefix: str = "", limit: int = 100) -> List[dict]:
        """
        List files in bucket with optional prefix filter
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix, max_results=limit)
            
            files = []
            for blob in blobs:
                file_info = {
                    "name": blob.name,
                    "size": blob.size,
                    "content_type": blob.content_type,
                    "created": blob.time_created.isoformat() if blob.time_created else None,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "public_url": f"https://storage.googleapis.com/{self.bucket_name}/{blob.name}"
                }
                files.append(file_info)
            
            return files
            
        except Exception as e:
            raise RuntimeError(f"Failed to list files: {str(e)}")
    
    def get_file_metadata(self, gcs_filename: str) -> dict:
        """
        Get file metadata from GCS
        """
        try:
            blob = self.bucket.blob(gcs_filename)
            blob.reload()
            
            return {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "etag": blob.etag,
                "md5_hash": blob.md5_hash,
                "public_url": f"https://storage.googleapis.com/{self.bucket_name}/{blob.name}"
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get file metadata: {str(e)}")

# Create global storage service instance
storage_service = StorageService()