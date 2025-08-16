from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.storage_service import storage_service

router = APIRouter(prefix="/storage", tags=["storage"])

class UploadItem(BaseModel):
    fileName: str = Field(..., description="Original file name")
    size: int = Field(..., gt=0, description="File size in bytes")
    contentType: Optional[str] = Field(None, description="MIME type")

class SignedUrlItem(BaseModel):
    fileName: str
    gcsFileName: str
    url: str
    method: str = "PUT"
    headers: dict
    expiresAt: str
    bucket: str

class SignedUrlBatchResponse(BaseModel):
    urls: List[SignedUrlItem]

@router.post("/upload-urls", response_model=SignedUrlBatchResponse)
async def create_signed_upload_urls(items: List[UploadItem]):
    if not items:
        raise HTTPException(status_code=400, detail="No files provided")
    try:
        user_id = 1

        results = []
        for it in items:
            signed = storage_service.generate_signed_upload_url(
                original_filename=it.fileName,
                file_size=it.size,
                content_type=it.contentType or "application/octet-stream",
                user_id=user_id,
                expires_minutes=10,
            )
            results.append(
                SignedUrlItem(
                    fileName=it.fileName,
                    gcsFileName=signed["gcs_filename"],
                    url=signed["url"],
                    method="PUT",
                    headers=signed["headers"],
                    expiresAt=signed["expiresAt"],
                    bucket=signed["bucket_name"],
                )
            )
        return SignedUrlBatchResponse(urls=results)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create signed URLs: {str(e)}")