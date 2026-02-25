from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.models import FileStatus


class FileBase(BaseModel):
    filename: str
    original_filename: str
    mime_type: str


class FileCreate(FileBase):
    file_path: str
    file_size: int
    user_id: int


class FileUpdate(BaseModel):
    status: Optional[FileStatus] = None
    extracted_text: Optional[str] = None
    extra_metadata: Optional[dict] = None


class FileResponse(FileBase):
    id: int
    user_id: int
    file_path: str
    file_size: int
    status: FileStatus
    extracted_text: Optional[str] = None
    extra_metadata: Optional[dict] = {}
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """Response after file upload"""
    id: int
    filename: str
    file_size: int
    mime_type: str
    status: FileStatus

    model_config = ConfigDict(from_attributes=True)
