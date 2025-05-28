from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from backend.models.download_job import DownloadJob
from backend.schemas.download_job import DownloadJobCreate, DownloadJobUpdate

class CRUDDownloadJob:
    def get(self, db: Session, id: Any) -> Optional[DownloadJob]:
        return db.query(DownloadJob).filter(DownloadJob.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[DownloadJob]:
        return db.query(DownloadJob).offset(skip).limit(limit).all()
    
    def get_multi_by_status(
        self, db: Session, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[DownloadJob]:
        return db.query(DownloadJob).filter(DownloadJob.status == status).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: DownloadJobCreate) -> DownloadJob:
        db_obj = DownloadJob(
            video_url=str(obj_in.video_url), # Ensure HttpUrl is converted to string for DB
            output_format=obj_in.output_format,
            resolution=obj_in.resolution,
            # status is set by default in the model
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: DownloadJob, obj_in: Union[DownloadJobUpdate, Dict[str, Any]]
    ) -> DownloadJob:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[DownloadJob]:
        obj = db.query(DownloadJob).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

download_job = CRUDDownloadJob()
