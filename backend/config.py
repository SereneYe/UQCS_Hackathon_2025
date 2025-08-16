import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory paths
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"

# Temp folder paths
GENERATED_AUDIO_DIR = TEMP_DIR / "generated_audio"
GENERATED_VIDEO_DIR = TEMP_DIR / "generated_video"
PROCESSED_VIDEO_DIR = TEMP_DIR / "processed_video"

# GCP Storage Configuration
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "hackathon-file-storage")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_STORAGE_BASE_URL = f"https://storage.googleapis.com/{GCP_BUCKET_NAME}"

# File upload settings
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".aac", ".ogg", ".m4a"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
ALLOWED_TEXT_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}
ALLOWED_EXTENSIONS = ALLOWED_AUDIO_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS | ALLOWED_TEXT_EXTENSIONS

# Ensure temp directories exist
def ensure_temp_directories():
    """Create temp directories if they don't exist"""
    GENERATED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

# File path helpers
def get_audio_file_path(audio_id: int, format: str) -> str:
    """Get file path for generated audio"""
    ensure_temp_directories()
    return str(GENERATED_AUDIO_DIR / f"{audio_id}.{format.lower()}")

def get_video_file_path(video_id: int, format: str = "mp4") -> str:
    """Get file path for generated video"""
    ensure_temp_directories()
    return str(GENERATED_VIDEO_DIR / f"{video_id}.{format.lower()}")

def get_processed_video_path(video_id: int, format: str = "mp4") -> str:
    """Get file path for processed video"""
    ensure_temp_directories()
    return str(PROCESSED_VIDEO_DIR / f"{video_id}_processed.{format.lower()}")