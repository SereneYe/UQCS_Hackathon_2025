from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import VideoStatus, AudioStatus, FileCategory, FileStatus, VideoSessionStatus, VideoCategory

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Video Schemas
class VideoBase(BaseModel):
    user_email: str
    video_task_id: str
    veo_task_id: str
    status: VideoStatus

class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    status: Optional[VideoStatus] = None
    veo_task_id: Optional[str] = None

class Video(VideoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Audio Schemas
class AudioBase(BaseModel):
    user_email: str
    text_input: str
    voice_name: Optional[str] = "en-US-Wavenet-D"
    language_code: Optional[str] = "en-US"
    audio_format: Optional[str] = "MP3"

class AudioCreate(AudioBase):
    pass

class AudioUpdate(BaseModel):
    status: Optional[AudioStatus] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None

class Audio(AudioBase):
    id: int
    status: AudioStatus
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# File Schemas
class FileBase(BaseModel):
    original_filename: str
    description: Optional[str] = None
    tags: Optional[str] = None

class FileCreate(FileBase):
    user_email: Optional[str] = None
    video_session_id: Optional[int] = None

class FileUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[FileStatus] = None
    video_session_id: Optional[int] = None

class FileUploadResponse(BaseModel):
    id: int
    original_filename: str
    gcs_filename: str
    file_size: int
    content_type: str
    category: FileCategory
    status: FileStatus
    public_url: Optional[str] = None
    upload_url: Optional[str] = None
    message: str

class FileDownloadResponse(BaseModel):
    id: int
    original_filename: str
    download_url: str
    expires_at: Optional[datetime] = None
    file_size: int
    content_type: str

class File(FileBase):
    id: int
    user_email: Optional[str] = None
    video_session_id: Optional[int] = None
    gcs_filename: str
    bucket_name: str
    file_size: int
    content_type: str
    category: FileCategory
    status: FileStatus
    public_url: Optional[str] = None
    gcs_path: str
    md5_hash: Optional[str] = None
    download_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FileList(BaseModel):
    files: List[File]
    total: int
    page: int
    per_page: int

# Video Session Schemas
class VideoSessionBase(BaseModel):
    user_id: int
    session_name: Optional[str] = None
    user_prompt: Optional[str] = None
    category: Optional[VideoCategory] = None
    description: Optional[str] = None

class VideoSessionCreate(VideoSessionBase):
    pass

class VideoSessionUpdate(BaseModel):
    session_name: Optional[str] = None
    user_prompt: Optional[str] = None
    category: Optional[VideoCategory] = None
    status: Optional[VideoSessionStatus] = None
    description: Optional[str] = None
    total_files: Optional[int] = None
    processed_files: Optional[int] = None
    output_video_path: Optional[str] = None
    video_url: Optional[str] = None

class VideoSession(VideoSessionBase):
    id: int
    status: VideoSessionStatus
    total_files: int = 0
    processed_files: int = 0
    output_video_path: Optional[str] = None
    video_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VideoSessionList(BaseModel):
    sessions: List[VideoSession]
    total: int
    page: int
    per_page: int