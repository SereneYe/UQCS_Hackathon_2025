from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from database import engine

# Import all routers
from app.routers import storage, users, videos, audio, video_processing, files

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hackathon Backend API", 
    description="FastAPI backend with SQLite for UQCS Hackathon 2025",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(users.router)
app.include_router(videos.router)
app.include_router(audio.router)
app.include_router(video_processing.router)
app.include_router(files.router)
app.include_router(storage.router)

# Core health endpoints
@app.get("/")
def read_root():
    return {"message": "Hackathon Backend API is alive 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)