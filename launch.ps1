# Function to download file with progress
function Download-FileWithProgress {
    param (
        [string]$url,
        [string]$outputFile
    )
    
    Write-Host "Downloading $url..."
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($url, $outputFile)
}

# Check if Python environment exists
if (-not (Test-Path ".\python")) {
    Write-Host "Setting up portable Python environment..."
    
    # Download WinPython Zero
    Write-Host "Downloading WinPython..."
    Download-FileWithProgress -url "https://github.com/winpython/winpython/releases/download/4.3.20210620/Winpython64-3.9.5.0dot.exe" -outputFile "winpython.exe"
    
    # Extract WinPython
    Write-Host "Extracting Python..."
    Start-Process -Wait -FilePath ".\winpython.exe" -ArgumentList "-y", "-o."
    
    # Move Python directory
    Move-Item -Path "WPy64-3950\python-3.9.5.amd64" -Destination "python"
    Remove-Item -Path "WPy64-3950" -Recurse -Force
    Remove-Item -Force "winpython.exe"
    
    # Install requirements
    Write-Host "Installing requirements..."
    & ".\python\python.exe" -m pip install -r requirements.txt
}

# Update yt-dlp to latest version
Write-Host "Updating yt-dlp to latest version..."
& ".\python\python.exe" -m pip install --upgrade yt-dlp

# Launch the application
Write-Host "Launching Video Downloader..."
& ".\python\python.exe" src\video_downloader.py
