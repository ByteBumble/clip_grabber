import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Video Downloader API"
    PROJECT_VERSION: str = "0.1.0"

    # Database settings (PostgreSQL - commented out)
    # POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user")
    # POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    # POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    # POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    # POSTGRES_DB: str = os.getenv("POSTGRES_DB", "app_db")
    # DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # SQLite configuration:
    SQLITE_DB_FILE: str = os.getenv("SQLITE_DB_FILE", "./video_downloader.db") # Changed default name
    DATABASE_URL: str = f"sqlite:///{SQLITE_DB_FILE}"

    # yt-dlp settings
    DOWNLOAD_PATH: str = os.getenv("DOWNLOAD_PATH", "./downloads")

settings = Settings()

# Ensure download path exists
if not os.path.exists(settings.DOWNLOAD_PATH):
    os.makedirs(settings.DOWNLOAD_PATH)
