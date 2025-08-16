from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.storage_service import storage_service

router = APIRouter(prefix="/storage", tags=["storage"])

class UploadFileItem(BaseModel):
    fileName: str = Field(..., description="Original file name from client")
    size: int = Field(..., ge=0, description="File size in bytes")
    contentType: Optional[str] = Field(default="application/octet-stream")

class GetUploadUrlsRequest(BaseModel):
    userId: int = Field(..., ge=1, description="Current user id")
    files: List[UploadFileItem]

class SignedUrlResponseItem(BaseModel):
    fileName: str
    gcsFileName: str
    url: str
    method: str = "PUT"
    headers: dict
    expiresAt: str
    bucket: str

class GetUploadUrlsResponse(BaseModel):
    urls: List[SignedUrlResponseItem]

@router.post("/upload-urls", response_model=GetUploadUrlsResponse)
def get_signed_upload_urls(payload: GetUploadUrlsRequest):
    try:
        urls: List[SignedUrlResponseItem] = []
        for f in payload.files:
            # 生成签名URL并把 user_id 传进去
            signed = storage_service.generate_signed_upload_url(
                original_filename=f.fileName,
                file_size=f.size,
                content_type=f.contentType or "application/octet-stream",
                user_id=payload.userId,
            )
            # 将后端字段名映射为前端期望的命名
            urls.append(SignedUrlResponseItem(
                fileName=signed["original_filename"],
                gcsFileName=signed["gcs_filename"],
                url=signed["url"],
                method=signed["method"],
                headers=signed["headers"],
                expiresAt=signed["expiresAt"],
                bucket=signed["bucket_name"],
            ))
        return GetUploadUrlsResponse(urls=urls)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create signed URLs: {str(e)}")