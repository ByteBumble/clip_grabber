# Video Downloader

A full-stack application to download videos from various platforms.

## Features

- Input video URL
- Choose download options (format, resolution)
- View download progress
- Access downloaded files (with history)

## Tech Stack

- **Backend**: Python, FastAPI, yt-dlp, SQLite
- **Web Frontend**: React, Vite, TailwindCSS
- **Mobile Frontend**: React Native (Expo)

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the project root directory:
   ```bash
   cd video-downloader-win
   ```

2. Create and activate a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   pip install uvicorn
   ```

4. Start the backend server:
   ```bash
   python -m uvicorn backend.main:app --reload
   ```
   The backend will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   # or
   yarn
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   The frontend will be available at `http://localhost:5173`

## Usage

1. Open your browser and go to `http://localhost:5173`
2. Enter a video URL in the input field
3. Select your preferred download options
4. Click "Download" to start the download
5. View your download history and access downloaded files

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Troubleshooting

- **Backend not starting**: Ensure all Python dependencies are installed and you're running from the project root directory
- **Connection refused**: Make sure the backend server is running before accessing the frontend
- **Module not found errors**: Ensure you've activated the virtual environment and installed all dependencies
