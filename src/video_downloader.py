import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import yt_dlp
import re
import time

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader")
        
        # Load settings
        self.settings = self.load_settings()
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL Entry
        ttk.Label(main_frame, text="Video URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Download Location
        ttk.Label(main_frame, text="Save to:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.download_path = tk.StringVar(value=self.settings.get('download_path', os.path.join(os.getcwd(), "Downloads")))
        self.location_entry = ttk.Entry(main_frame, textvariable=self.download_path, width=40)
        self.location_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_location).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status Label
        self.status = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status)
        self.status_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Download Button
        self.download_button = ttk.Button(button_frame, text="Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        # Open Folder Button
        self.open_folder_button = ttk.Button(button_frame, text="Open Download Folder", command=self.open_download_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=5)
        
        # Save Settings Button
        self.save_settings_button = ttk.Button(button_frame, text="Save Settings", command=self.save_settings)
        self.save_settings_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_path.get(), exist_ok=True)

    def load_settings(self):
        """Load settings from JSON file"""
        try:
            with open("settings.json", 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_settings(self):
        """Save current settings to JSON file"""
        settings = {
            'download_path': self.download_path.get()
        }
        try:
            with open("settings.json", 'w') as f:
                json.dump(settings, f, indent=4)
            self.status.set("Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {str(e)}")

    def browse_location(self):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)
            os.makedirs(folder, exist_ok=True)

    def open_download_folder(self):
        """Open the download folder in file explorer"""
        folder_path = self.download_path.get()
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showerror("Error", "Download folder not found!")

    def start_download(self):
        """Start the download process"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return
        
        self.download_button.config(state="disabled")
        self.status.set("Starting download...")
        self.progress_var.set(0)
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            try:
                # Calculate progress percentage
                if 'total_bytes' in d:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d:
                    percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    percent = 0
                
                # Update progress bar and status with detailed info
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / (1024 * 1024)  # Convert to MB/s
                    eta = d.get('eta', '?')
                    self.status.set(f"Downloading at {speed_mb:.1f} MB/s (ETA: {eta}s)")
                
                self.progress_var.set(percent)
                self.root.update()
            except Exception as e:
                print(f"Error in progress hook: {e}")
        elif d['status'] == 'finished':
            self.status.set("Download finished, processing file...")
            self.root.update()
        elif d['status'] == 'error':
            self.status.set(f"Error: {d.get('error', 'Unknown error')}")
            self.root.update()

    def get_recent_downloads(self, download_dir, seconds=60):
        """Get list of recently downloaded files"""
        current_time = time.time()
        result = []
        
        for f in os.listdir(download_dir):
            file_path = os.path.join(download_dir, f)
            try:
                # Check if it's a file and was modified recently
                if os.path.isfile(file_path):
                    mod_time = os.path.getmtime(file_path)
                    if current_time - mod_time <= seconds:
                        result.append((f, file_path, os.path.getsize(file_path)))
            except Exception as e:
                print(f"Error checking file {f}: {e}")
                
        return result

    def download_video(self, url):
        """Download video using yt-dlp Python library"""
        try:
            # Ensure download directory exists
            download_dir = self.download_path.get()
            os.makedirs(download_dir, exist_ok=True)

            # Get list of files before download
            files_before = set(os.path.join(download_dir, f) for f in os.listdir(download_dir))

            # Handle URLs and convert shorts to regular videos
            if 'youtube.com/shorts/' in url:
                url = url.replace('youtube.com/shorts/', 'youtube.com/watch?v=')
            elif not url.startswith('https://'):
                url = 'https://' + url

            # Clean up any existing partial downloads
            for file in os.listdir(download_dir):
                if file.endswith(('.part', '.temp', '.ytdl')):
                    try:
                        os.remove(os.path.join(download_dir, file))
                        self.status.set("Cleaned up partial downloads...")
                    except:
                        pass

            # Configure yt-dlp options using the proven format from batch file
            temp_filename = 'temp_video'  # Match batch file's temp filename
            temp_path = os.path.join(download_dir, f'{temp_filename}.mp4')  # Define temp_path at the start
            ydl_opts = {
                'outtmpl': os.path.join(download_dir, f'{temp_filename}.%(ext)s'),  # Match batch file approach
                'format': 'bv*+ba/b',  # Best video + best audio format
                'merge_output_format': 'mp4',
                'nocheckcertificate': True,  # SSL verification bypass
                'ignoreerrors': False,
                'no_warnings': True,
                'force_ipv4': True,
                'progress_hooks': [self.progress_hook],
                'quiet': True,  # Suppress debug output
                'verbose': False,  # Disable verbose logging
                'socket_timeout': 30,
                'retries': 10,
                'fragment_retries': 10,
                'hls_prefer_native': True,
                'restrictfilenames': True,  # Restrict filenames to only ASCII characters
                'windowsfilenames': True,   # Use Windows-compatible filenames
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                'postprocessors': [{
                    'key': 'FFmpegVideoRemuxer',
                    'preferedformat': 'mp4',
                }]
            }

            self.status.set("Starting download...")
            self.download_button.config(state="disabled")
            self.progress_var.set(0)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Try downloading with selected format
                    ydl.download([url])
                    
                    # After successful download, rename the file with timestamp
                    if os.path.exists(temp_path):
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        new_filename = f"video_converted_{timestamp}.mp4"
                        new_path = os.path.join(download_dir, new_filename)
                        os.rename(temp_path, new_path)
                        self.status.set(f"Download complete: {new_filename}")
                except Exception as e:
                    error_msg = str(e)
                    print(f"Download error: {error_msg}")
                    self.status.set("Download failed!")
                    # Clean up temp file if it exists
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                    raise

            # Wait briefly for file operations to complete
            time.sleep(1)

            # Get list of files after download
            files_after = set(os.path.join(download_dir, f) for f in os.listdir(download_dir))
            new_files = files_after - files_before

            if not new_files:
                # If no new files found, check recent downloads
                recent = self.get_recent_downloads(download_dir, seconds=60)
                if recent:
                    # Use the most recently modified file
                    newest_file = max(recent, key=lambda x: os.path.getmtime(x[1]))
                    new_files = {newest_file[1]}
                else:
                    raise Exception("No downloaded file found")

            # Verify the download
            downloaded_file = list(new_files)[0]  # Get the first (and should be only) new file
            if not os.path.exists(downloaded_file):
                raise Exception(f"Downloaded file not found: {downloaded_file}")

            file_size = os.path.getsize(downloaded_file)
            if file_size < 1024:  # Less than 1KB
                raise Exception(f"Downloaded file is too small: {file_size} bytes")

            self.status.set("Download completed successfully!")
            self.download_button.config(state="normal")
            
            if messagebox.askyesno("Success", "Download completed! Would you like to open the download folder?"):
                self.open_download_folder()
            return True

        except Exception as e:
            error_msg = str(e)
            self.status.set(f"Error: {error_msg}")
            self.download_button.config(state="normal")
            messagebox.showerror("Error", f"Download failed: {error_msg}")
            
            # Log the error details
            print(f"\nError details:")
            print(f"URL: {url}")
            print(f"Error: {error_msg}")
            print(f"Download directory: {download_dir}")
            print("Files in directory:")
            for f in os.listdir(download_dir):
                file_path = os.path.join(download_dir, f)
                print(f"- {f}: {os.path.getsize(file_path)} bytes")
            
            return False

    def clean_filename(self, title):
        """Clean filename to be Windows-compatible"""
        # Remove invalid characters
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        # Remove emojis and special characters
        title = re.sub(r'[^\x00-\x7F]+', '', title)
        # Truncate to reasonable length (max 100 chars)
        if len(title) > 100:
            title = title[:97] + "..."
        return title.strip()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()