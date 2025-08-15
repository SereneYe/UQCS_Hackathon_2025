from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class VideoStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"

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