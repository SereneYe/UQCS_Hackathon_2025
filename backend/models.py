from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, ForeignKey
from sqlalchemy.sql import func
from database import Base
import enum

class VideoStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"

class AudioStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FileCategory(enum.Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    OTHER = "other"

class FileStatus(enum.Enum):
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"

class VideoSessionStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoCategory(enum.Enum):
    CONGRATULATION_VIDEO = "congratulation_video"
    EVENT_PROPAGATION_VIDEO = "event_propagation_video" 
    COMPANY_INTRODUCTION_VIDEO = "company_introduction_video"
    GENERAL_VIDEO = "general_video"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    video_task_id = Column(String, index=True)
    veo_task_id = Column(String, index=True)
    status = Column(Enum(VideoStatus), index=True, default=VideoStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Audio(Base):
    __tablename__ = "audios"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    text_input = Column(Text, nullable=False)
    voice_name = Column(String, default="en-US-Wavenet-D")
    language_code = Column(String, default="en-US")
    audio_format = Column(String, default="MP3")
    status = Column(Enum(AudioStatus), index=True, default=AudioStatus.PENDING)
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class VideoSession(Base):
    __tablename__ = "video_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    session_name = Column(String, nullable=True)  # Optional name for the session
    user_prompt = Column(Text, nullable=True)  # User's prompt for video creation
    category = Column(Enum(VideoCategory), nullable=True)  # Video category
    status = Column(Enum(VideoSessionStatus), index=True, default=VideoSessionStatus.PENDING)
    description = Column(Text, nullable=True)
    total_files = Column(Integer, default=0)  # Track number of files in session
    processed_files = Column(Integer, default=0)  # Track processed files
    output_video_path = Column(String, nullable=True)  # Path to final video
    video_url = Column(String, nullable=True)  # URL to generated video
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)  # User who uploaded the file
    video_session_id = Column(Integer, ForeignKey("video_sessions.id"), nullable=True, index=True)  # Link to video session
    original_filename = Column(String, nullable=False)
    gcs_filename = Column(String, nullable=False, unique=True)  # Unique filename in GCS
    bucket_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    category = Column(Enum(FileCategory), nullable=False)
    status = Column(Enum(FileStatus), index=True, default=FileStatus.UPLOADING)
    public_url = Column(String, nullable=True)
    gcs_path = Column(String, nullable=False)  # Full GCS path
    md5_hash = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(String, nullable=True)  # JSON string of tags
    is_public = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())