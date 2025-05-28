import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.db.base_class import Base  # Import Base
from backend.db.session import engine  # Import engine
from backend.core.config import settings
# Ensure all models are imported before Base.metadata.create_all is called
from backend import models  # This will import __init__.py from models which imports DownloadJob


def create_tables():
    Base.metadata.create_all(bind=engine)

# Ensure download directory exists
os.makedirs(settings.DOWNLOAD_PATH, exist_ok=True)

app = FastAPI(
    title="Video Downloader API",
    description="API for downloading videos and managing download history.",
    version="0.1.0",
    on_startup=[create_tables],
)

# Serve static files from the downloads directory
app.mount("/downloads", StaticFiles(directory=settings.DOWNLOAD_PATH), name="downloads")

# CORS middleware for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Video Downloader API"}

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Endpoint to download files securely"""
    try:
        # Sanitize the file path to prevent directory traversal
        safe_path = os.path.normpath(file_path).lstrip('/')
        # Remove any 'downloads/' prefix if it exists to prevent double 'downloads' in path
        if safe_path.startswith('downloads/'):
            safe_path = safe_path[10:]  # Remove 'downloads/' prefix
        full_path = os.path.abspath(os.path.join(settings.DOWNLOAD_PATH, safe_path))
        
        # Verify the file exists and is within the download directory
        if not os.path.isfile(full_path):
            return JSONResponse(
                status_code=404,
                content={"detail": f"File not found: {full_path}"}
            )
            
        # Verify the file is within the download directory
        if not os.path.abspath(full_path).startswith(os.path.abspath(settings.DOWNLOAD_PATH)):
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
            
        # Get the filename for the Content-Disposition header
        filename = os.path.basename(full_path)
        
        return FileResponse(
            path=full_path,
            filename=filename,
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error downloading file: {str(e)}"}
        )

@app.get("/stream/{file_path:path}")
async def stream_video(file_path: str, request: Request):
    """Endpoint to stream video files for playback"""
    try:
        # Sanitize the file path to prevent directory traversal
        safe_path = os.path.normpath(file_path).lstrip('/')
        # Remove any 'downloads/' prefix if it exists to prevent double 'downloads' in path
        if safe_path.startswith('downloads/'):
            safe_path = safe_path[10:]  # Remove 'downloads/' prefix
        full_path = os.path.abspath(os.path.join(settings.DOWNLOAD_PATH, safe_path))
        
        # Verify the file exists
        if not os.path.isfile(full_path):
            return JSONResponse(
                status_code=404,
                content={"detail": f"File not found: {full_path}"}
            )
            
        # Verify the file is within the download directory
        if not full_path.startswith(os.path.abspath(settings.DOWNLOAD_PATH)):
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        
        # Determine the media type based on file extension
        ext = os.path.splitext(full_path)[1].lower()
        media_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.ogg': 'video/ogg',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.flac': 'audio/flac',
            '.aac': 'audio/aac'
        }
        media_type = media_types.get(ext, 'application/octet-stream')
        
        # Get file size for range requests
        file_size = os.path.getsize(full_path)
        
        # Handle range requests for seeking
        range_header = request.headers.get('range')
        if range_header:
            from fastapi.responses import Response
            start, end = 0, None
            range_ = range_header.replace('bytes=', '').split('-')
            if range_[0]:
                start = int(range_[0])
            if len(range_) > 1 and range_[1]:
                end = int(range_[1])
            
            length = (end or file_size) - start
            
            with open(full_path, 'rb') as f:
                f.seek(start)
                data = f.read(length)
                
            response = Response(
                data,
                status_code=206,
                media_type=media_type,
                headers={
                    'Content-Range': f'bytes {start}-{start + len(data) - 1}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(len(data)),
                    'Content-Type': media_type,
                }
            )
            return response
        
        # If no range header, return the whole file
        return FileResponse(
            path=full_path,
            media_type=media_type,
            headers={
                'Accept-Ranges': 'bytes',
                'Content-Length': str(file_size),
                'Content-Type': media_type
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error streaming file: {str(e)}"}
        )

# API routers
from backend.api.v1.api import api_router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
