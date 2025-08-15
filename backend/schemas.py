from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models import VideoStatus, AudioStatus

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