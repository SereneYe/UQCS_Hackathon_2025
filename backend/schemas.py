from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models import VideoStatus

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