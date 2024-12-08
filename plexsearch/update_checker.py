"""Module for checking and handling package updates."""
import os
import json
import time
import feedparser
from packaging import version
from typing import Optional, Dict, Any
import subprocess

def get_latest_version(package_name: str) -> str:
    """Get the latest version of a package from PyPI."""
    rss_url = f"https://pypi.org/rss/project/{package_name}/releases.xml"
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        return "0.0.0"
    try:
        title = feed.entries[0].title
        if ": " in title:
            return title.split(": ")[1]
        elif " " in title:
            return title.split(" ")[1]
        return title
    except (IndexError, AttributeError):
        return "0.0.0"

def check_for_update(current_version: str, latest_version: str) -> bool:
    """Compare versions to check if an update is available."""
    try:
        return version.parse(latest_version) > version.parse(current_version)
    except version.InvalidVersion:
        return False

class UpdateChecker:
    """Handles checking for package updates."""
    
    def __init__(self, package_name: str, current_version: str):
        self.package_name = package_name
        self.current_version = current_version
        self.state_dir = os.path.expanduser("~/.config/plexsearch")
        self.state_file = os.path.join(self.state_dir, "update_state.json")
        
    def load_state(self) -> Dict[str, float]:
        """Load the saved state from file."""
        if not os.path.exists(self.state_file):
            if not os.path.exists(self.state_dir):
                os.makedirs(self.state_dir)
            return {"last_check": 0, "last_reminder": 0}
        
        with open(self.state_file, 'r') as f:
            return json.load(f)
            
    def save_state(self, state: Dict[str, float]) -> None:
        """Save the state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
            
    def check_and_notify(self, interval_hours: int = 24) -> Optional[str]:
        """Check for updates and notify if available."""
        state = self.load_state()
        current_time = time.time()
        
        # Only check periodically
        if current_time - state["last_check"] < interval_hours * 3600:
            return None
            
        state["last_check"] = current_time
        latest_version = get_latest_version(self.package_name)
        
        if check_for_update(self.current_version, latest_version):
            # Only remind periodically
            if current_time - state["last_reminder"] < interval_hours * 3600:
                return None
                
            state["last_reminder"] = current_time
            self.save_state(state)
            return latest_version
            
        self.save_state(state)
        return None
        
    def update_package(self) -> bool:
        """Update the package using pip."""
        try:
            subprocess.run(
                ["pip", "install", "--upgrade", self.package_name],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
