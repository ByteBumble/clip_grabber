import yt_dlp
import os
import logging
import re
from sqlalchemy.orm import Session

from backend import crud, models, schemas
from backend.core.config import settings
from backend.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ydl_opts(job: models.DownloadJob):
    """Generate yt-dlp options based on job parameters."""
    output_template = os.path.join(settings.DOWNLOAD_PATH, f"{job.id}_%(title)s.%(ext)s")
    
    ydl_opts = {
        # Always prefer MP4 format with H.264 video and AAC audio
        'format': 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',  # Force MP4 container
        'outtmpl': output_template,
        'noplaylist': True,
        # 'progress_hooks' will be set dynamically in download_video_task
        # 'progress_hooks': [lambda d: actual_progress_hook(d, job.id, db_session_for_hook)],
        'logger': logger,
        'verbose': True,  # Enable verbose logging
        'retries': 10,  # Increase number of retries
        'fragment_retries': 10,  # Retry downloading fragments
        'file_access_retries': 10,  # Retry on file access errors
        'extractor_retries': 3,  # Retry on extractor errors
        'retry_sleep': 5,  # Wait between retries
        'socket_timeout': 30,  # Socket timeout in seconds
        'nocheckcertificate': True,  # Don't verify SSL certificates (can help with some network issues)
        'force_ip': '4',  # Force IPv4
        'geo_bypass': True,  # Bypass geographic restrictions
        'geo_bypass_country': 'US',  # Set to your country code if needed
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],  # Skip DASH and HLS formats which can cause issues
            },
        },
    }

    if job.output_format == models.OutputFormat.MP3:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # Handle resolution for video formats
        if job.resolution != models.Resolution.BEST:
            resolution_str = job.resolution.value.replace('p', '')
            # More specific format selection to avoid prank videos
            ydl_opts['format'] = (
                f'bestvideo[height<={resolution_str}][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/'  # MP4 with H.264
                f'bestvideo[height<={resolution_str}][ext=mp4]+bestaudio[ext=m4a]/'  # Fallback to any MP4
                f'best[height<={resolution_str}]/best'  # Final fallback
            )
        else:
            # For best quality, still prefer H.264 for compatibility
            ydl_opts['format'] = (
                'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/'  # MP4 with H.264
                'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'  # Fallback to any MP4
                'best'  # Final fallback
            )

    return ydl_opts

def update_job_progress(db: Session, job_id: int, progress: int, status: str = None, status_message: str = None):
    """Helper function to update job progress and status"""
    update_data = {'progress': progress}
    if status:
        update_data['status'] = status
    if status_message:
        update_data['status_message'] = status_message
    
    job = crud.download_job.get(db, id=job_id)
    if job:
        crud.download_job.update(db, db_obj=job, obj_in=schemas.DownloadJobUpdate(**update_data))
        db.commit()

def download_video_task(job_id: int):
    """The main task to download a video."""
    logger.info(f"Starting download task for job_id: {job_id}")
    db: Session = SessionLocal()
    job = None  # Initialize job to None
    
    try:  # Outer try block for overall task and DB session management
        job = crud.download_job.get(db, id=job_id)
        
        if not job:
            logger.error(f"Job {job_id} not found in database.")
            return  # Goes to finally

        # Update status to indicate download is starting
        update_job_progress(db, job_id, 0, models.DownloadStatus.DOWNLOADING, "Preparing download...")
        logger.info(f"Job {job_id} status updated to DOWNLOADING")

        ydl_opts = get_ydl_opts(job)
        
        # Track download progress states
        download_completed = False
        post_processing = False
        final_file_path = None
        
        def actual_progress_hook(d):
            nonlocal download_completed, post_processing, final_file_path
            
            try:
                hook_job = crud.download_job.get(db, id=job_id)
                if not hook_job:
                    logger.warning(f"Job {job_id} not found during progress hook. Skipping update.")
                    return

                if d['status'] == 'downloading':
                    if post_processing:
                        return  # Skip updates during post-processing
                        
                    raw_progress_str = d.get('_percent_str', '0%')
                    match = re.search(r'(\d+\.?\d*)', raw_progress_str)
                    if match:
                        progress_val_str = match.group(1)
                        try:
                            # Scale download progress to 0-80% to leave room for post-processing
                            download_progress = min(80, int(float(progress_val_str) * 0.8))
                            update_job_progress(
                                db, 
                                job_id, 
                                download_progress, 
                                status_message=f"Downloading: {progress_val_str}%"
                            )
                        except ValueError:
                            logger.warning(f"Could not convert progress string for job {job_id}: {progress_val_str}")
                    
                elif d['status'] == 'finished':
                    if not download_completed:
                        download_completed = True
                        post_processing = True
                        update_job_progress(
                            db, 
                            job_id, 
                            85, 
                            status_message="Download complete. Processing..."
                        )
                        
                elif d['status'] == 'error':
                    logger.error(f"yt-dlp error for job {job_id}: {d}")
                    update_job_progress(
                        db, 
                        job_id, 
                        0, 
                        models.DownloadStatus.FAILED, 
                        f"Error: {d.get('error', 'Unknown error')}"
                    )
                    
            except Exception as e:
                logger.error(f"Error in progress hook for job {job_id}: {str(e)}")
                # Don't fail the whole download if the hook fails
                pass

        # Set up the progress hook
        ydl_opts['progress_hooks'] = [actual_progress_hook]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Starting download for job {job_id} with URL: {job.video_url}")
                
                # Get video info first to set the correct filename
                update_job_progress(db, job_id, 5, status_message="Getting video info...")
                
                # Extract info without downloading
                info_dict = ydl.extract_info(job.video_url, download=False, process=False)
                
                # Log video info for debugging
                logger.info(f"Video info for {job.video_url}:")
                logger.info(f"Title: {info_dict.get('title')}")
                logger.info(f"Duration: {info_dict.get('duration')}s")
                logger.info(f"Formats: {[f.get('format_id') for f in info_dict.get('formats', [])[:3]]}...")
                
                # Verify the video title looks reasonable
                video_title = info_dict.get('title', '').strip()
                if not video_title or len(video_title) < 2:  # Very short titles are suspicious
                    logger.warning(f"Suspiciously short video title: '{video_title}'")
                    video_title = f'video_{job_id}'
                    
                # Check if this looks like a rickroll/prank video
                suspicious_terms = ['rick astley', 'never gonna give you up', 'rickroll', 'prank', 'troll']
                if any(term in video_title.lower() for term in suspicious_terms):
                    logger.warning(f"Suspicious video title detected: {video_title}")
                    # Try to get a different format that's less likely to be a prank
                    ydl_opts['format'] = 'best[height>=480]'  # Prefer higher quality to avoid prank videos
                    info_dict = ydl.extract_info(job.video_url, download=False)  # Refresh info with new format
                # Clean up the title to be filesystem-safe
                safe_title = re.sub(r'[^\w\-_. ]', '_', video_title)
                safe_title = re.sub(r'\s+', ' ', safe_title).strip()  # Replace multiple spaces with single
                safe_title = safe_title[:100]  # Limit length
                file_ext = job.output_format.value if hasattr(job.output_format, 'value') else 'mp4'
                # Only include job ID if not already in the title to avoid duplicates
                if str(job.id) not in safe_title:
                    final_filename = f"{job.id}_{safe_title}.{file_ext}"
                else:
                    final_filename = f"{safe_title}.{file_ext}"
                final_path = os.path.abspath(os.path.join(settings.DOWNLOAD_PATH, final_filename))
                
                # Ensure download directory exists
                os.makedirs(settings.DOWNLOAD_PATH, exist_ok=True)
                
                # Start the download
                update_job_progress(db, job_id, 10, status_message="Starting download...")
                ydl.download([str(job.video_url)])
                
                # After download completes, update status
                update_job_progress(db, job_id, 95, status_message="Finalizing...")
                
                # Verify the file was downloaded
                if not os.path.exists(final_path):
                    # Try to find the actual downloaded file
                    for f in os.listdir(settings.DOWNLOAD_PATH):
                        if f.startswith(str(job.id) + '_') and f.endswith('.' + file_ext):
                            final_path = os.path.abspath(os.path.join(settings.DOWNLOAD_PATH, f))
                            break
                
                if not os.path.exists(final_path):
                    raise FileNotFoundError(f"Downloaded file not found at: {final_path}")
                
                # Update the database with final status
                update_job_progress(
                    db=db,
                    job_id=job_id,
                    progress=100,
                    status=models.DownloadStatus.COMPLETED,
                    status_message=f"Download completed: {os.path.basename(final_path)}"
                )
                
                # Update file path in the database - store relative path from DOWNLOAD_PATH
                job = crud.download_job.get(db, id=job_id)
                relative_path = os.path.relpath(final_path, settings.DOWNLOAD_PATH).replace('\\', '/')
                if job:
                    # Update the job with the relative file path
                    job.file_path = relative_path
                    db.commit()
                    logger.info(f"Updated job {job_id} with file path: {relative_path}")
                
                logger.info(f"Job {job_id} completed successfully. File saved to: {final_path}")
                return final_path
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in yt-dlp for job {job_id}: {error_msg}", exc_info=True)
            update_job_progress(
                db=db,
                job_id=job_id,
                progress=0,
                status=models.DownloadStatus.FAILED,
                status_message=f"Download failed: {error_msg}"
            )
            raise

    except Exception as e: # Catch exceptions from the outer try block (e.g. job fetching fails)
        logger.exception(f"Critical error in download_video_task for job_id {job_id} (outside download ops): {e}")
        # If job object was defined and an error occurred, try to mark it as FAILED.
        if job: # 'job' would be None if crud.download_job.get failed or it was never assigned.
            try:
                crud.download_job.update(db, db_obj=job, obj_in=schemas.DownloadJobUpdate(
                    status=models.DownloadStatus.FAILED, 
                    error_message=f"Critical error: {str(e)[:200]}"  # Truncate to avoid DB field length issues
                ))
                db.commit()
            except Exception as update_error:
                logger.exception(f"Failed to update job {job_id} status after critical error: {update_error}")
        else: # Job was not fetched successfully
            logger.error(f"Job {job_id} could not be fetched or processed due to critical error: {str(e)}. Cannot update its status.")
        raise  # Re-raise the original error to ensure the task is marked as failed in the task queue
    finally:
        logger.info(f"Closing database session for job_id: {job_id}")
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database connection for job {job_id}: {str(e)}")
