import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "download_dir": "",  # Will be set to Downloads folder
    "video_quality": "best",
    "theme": "dark",
    "recent_urls": [],
    "max_recent_urls": 5
}

CONFIG_FILE = Path(os.path.dirname(os.path.dirname(__file__))) / "settings.json"

def load_config():
    """Load configuration from file or create default."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Update with any new default keys
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception:
            pass
    
    # Set default download directory
    config = DEFAULT_CONFIG.copy()
    config["download_dir"] = str(Path(os.path.dirname(os.path.dirname(__file__))) / "Downloads")
    save_config(config)
    return config

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Initialize configuration
config = load_config()
