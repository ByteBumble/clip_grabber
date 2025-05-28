from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from backend import crud, models, schemas
from backend.db.session import get_db
from backend.services.downloader import download_video_task

router = APIRouter()

@router.post("/", response_model=schemas.DownloadJob, status_code=status.HTTP_201_CREATED)
async def create_download_job(
    *, 
    db: Session = Depends(get_db),
    job_in: schemas.DownloadJobCreate,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Create new download job.
    The actual download will be started as a background task.
    """
    db_job = crud.download_job.create(db=db, obj_in=job_in)
    background_tasks.add_task(download_video_task, job_id=db_job.id)
    return db_job

@router.get("/{job_id}", response_model=schemas.DownloadJob)
def read_download_job(
    *, 
    db: Session = Depends(get_db),
    job_id: int,
) -> Any:
    """
    Get download job by ID.
    """
    job = crud.download_job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download job not found")
    return job

@router.get("/", response_model=List[schemas.DownloadJob])
def read_download_jobs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve download jobs.
    """
    jobs = crud.download_job.get_multi(db, skip=skip, limit=limit)
    return jobs

@router.put("/{job_id}", response_model=schemas.DownloadJob)
def update_download_job(
    *, 
    db: Session = Depends(get_db),
    job_id: int,
    job_in: schemas.DownloadJobUpdate,
) -> Any:
    """
    Update a download job (e.g., its status or progress).
    This might be called by the background worker.
    """
    job = crud.download_job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download job not found")
    job = crud.download_job.update(db=db, db_obj=job, obj_in=job_in)
    return job

@router.delete("/{job_id}", response_model=schemas.DownloadJob)
def delete_download_job(
    *, 
    db: Session = Depends(get_db),
    job_id: int,
) -> Any:
    """
    Delete a download job.
    """
    job = crud.download_job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download job not found")
    # Add logic here if you need to cancel an ongoing download before deleting
    job = crud.download_job.remove(db=db, id=job_id)
    return job
