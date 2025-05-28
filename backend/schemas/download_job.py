from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, HttpUrl, field_validator
from enum import Enum

class DownloadJobBase(BaseModel):
    video_url: HttpUrl
    output_format: Optional[Literal['mp4', 'mp3', 'webm', 'flv', 'mkv', 'avi']] = 'mp4'
    resolution: Optional[Literal['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', 'best']] = 'best'

class DownloadJobCreate(DownloadJobBase):
    pass

class DownloadJobUpdate(BaseModel):
    @field_validator("status", mode='before')
    @classmethod
    def status_enum_to_value(cls, value):
        if isinstance(value, Enum):
            return value.value
        return value

    status: Optional[Literal['pending', 'downloading', 'processing', 'completed', 'failed', 'cancelled']] = None
    progress: Optional[int] = None # Percentage 0-100
    file_path: Optional[str] = None
    error_message: Optional[str] = None

class DownloadJobInDBBase(DownloadJobBase):
    id: int
    created_at: datetime
    updated_at: datetime
    status: Literal['pending', 'downloading', 'processing', 'completed', 'failed', 'cancelled'] = 'pending'
    progress: int = 0
    file_path: Optional[str] = None
    error_message: Optional[str] = None

    @field_validator("output_format", "resolution", "status", mode='before')
    @classmethod
    def enum_to_value(cls, value):
        if isinstance(value, Enum):
            return value.value
        return value

    class Config:
        from_attributes = True # Pydantic models to map to ORM objects

# Properties to return to client
class DownloadJob(DownloadJobInDBBase):
    pass

# Properties stored in DB
class DownloadJobInDB(DownloadJobInDBBase):
    pass
