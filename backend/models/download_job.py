from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from backend.db.base_class import Base

class DownloadStatus(PyEnum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OutputFormat(PyEnum):
    MP4 = "mp4"
    MP3 = "mp3"
    WEBM = "webm"
    FLV = "flv"
    MKV = "mkv"
    AVI = "avi"

class Resolution(PyEnum):
    P144 = "144p"
    P240 = "240p"
    P360 = "360p"
    P480 = "480p"
    P720 = "720p"
    P1080 = "1080p"
    P1440 = "1440p"
    P2160 = "2160p"
    BEST = "best"

class DownloadJob(Base):
    id = Column(Integer, primary_key=True, index=True)
    video_url = Column(String, nullable=False)
    output_format = Column(SQLAlchemyEnum(OutputFormat, values_callable=lambda x: [e.value for e in x]), default=OutputFormat.MP4, nullable=False)
    resolution = Column(SQLAlchemyEnum(Resolution, values_callable=lambda x: [e.value for e in x]), default=Resolution.BEST, nullable=False)
    
    status = Column(SQLAlchemyEnum(DownloadStatus, values_callable=lambda x: [e.value for e in x]), default=DownloadStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    file_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<DownloadJob(id={self.id}, url='{self.video_url[:30]}...', status='{self.status.value}')>"
