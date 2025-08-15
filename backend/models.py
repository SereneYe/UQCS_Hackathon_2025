from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum
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