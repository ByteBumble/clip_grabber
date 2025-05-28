from fastapi import APIRouter

# Import endpoint modules here
from backend.api.v1.endpoints import downloads

api_router = APIRouter()

# Include routers from endpoint modules here
api_router.include_router(downloads.router, prefix="/downloads", tags=["downloads"])
