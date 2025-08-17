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

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# VEO3 Configuration
VEO3_API_KEY = os.getenv("VEO3_API_KEY")
VEO3_BASE_URL = os.getenv("VEO3_BASE_URL", "https://api.qingyuntop.top")
VEO3_MODEL = os.getenv("VEO3_MODEL", "veo3-fast-frames")
VEO3_MODEL_FRAMES = os.getenv("VEO3_MODEL_FRAMES", "veo3-fast-frames")
VEO3_POLL_INTERVAL = int(os.getenv("VEO3_POLL_INTERVAL", "5"))
VEO3_MAX_WAIT_TIME = int(os.getenv("VEO3_MAX_WAIT_TIME", "900"))  # 15 minutes

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