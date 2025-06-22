import os
import sys
import subprocess
import psutil
import pyautogui
import time
import shutil
import glob
from pathlib import Path
import platform
import json
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

class AccessibilityCommands:
    def __init__(self):
        self.system = platform.system().lower()
        self.browser_driver = None
        
    # Window Management
    def open_application(self, app_name):
        """Open an application by name"""
        try:
            if self.system == "windows":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif self.system == "darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            else:  # Linux
                subprocess.Popen([app_name])
            return f"Successfully opened {app_name}"
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    
    def close_application(self, app_name):
        """Close an application by name"""
        try:
            closed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    closed_count += 1
            if closed_count > 0:
                return f"Closed {closed_count} instance(s) of {app_name}"
            return f"Application {app_name} not found running"
        except Exception as e:
            return f"Error closing {app_name}: {str(e)}"
    
    def minimize_window(self):
        """Minimize the active window"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('win', 'down')
            elif self.system == "darwin":
                pyautogui.hotkey('cmd', 'm')
            else:
                pyautogui.hotkey('alt', 'F9')
            return "Active window minimized"
        except Exception as e:
            return f"Error minimizing window: {str(e)}"
    
    def maximize_window(self):
        """Maximize the active window"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('win', 'up')
            elif self.system == "darwin":
                pyautogui.hotkey('cmd', 'ctrl', 'f')
            else:
                pyautogui.hotkey('alt', 'F10')
            return "Active window maximized"
        except Exception as e:
            return f"Error maximizing window: {str(e)}"
    
    def switch_window(self):
        """Switch between open windows"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('alt', 'tab')
            elif self.system == "darwin":
                pyautogui.hotkey('cmd', 'tab')
            else:
                pyautogui.hotkey('alt', 'tab')
            return "Switched to next window"
        except Exception as e:
            return f"Error switching window: {str(e)}"
    
    def close_window(self):
        """Close the active window"""
        try:
            if self.system == "windows":
                pyautogui.hotkey('alt', 'f4')
            elif self.system == "darwin":
                pyautogui.hotkey('cmd', 'w')
            else:
                pyautogui.hotkey('alt', 'f4')
            return "Active window closed"
        except Exception as e:
            return f"Error closing window: {str(e)}"
    
    def get_active_windows(self):
        """Get list of active windows for accessibility"""
        try:
            windows = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name']:
                    windows.append(proc.info['name'])
            unique_windows = list(set(windows))[:15]  # Limit to 15 for readability
            return f"Active applications: {', '.join(unique_windows)}"
        except Exception as e:
            return f"Error getting active windows: {str(e)}"

    # File Operations
    def create_file(self, filepath, content=""):
        """Create a new file"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            return f"Created file: {filepath}"
        except Exception as e:
            return f"Error creating file: {str(e)}"
    
    def create_folder(self, folderpath):
        """Create a new folder"""
        try:
            Path(folderpath).mkdir(parents=True, exist_ok=True)
            return f"Created folder: {folderpath}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"
    
    def delete_file(self, filepath):
        """Delete a file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return f"Deleted file: {filepath}"
            return f"File not found: {filepath}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
    
    def delete_folder(self, folderpath):
        """Delete a folder and its contents"""
        try:
            if os.path.exists(folderpath):
                shutil.rmtree(folderpath)
                return f"Deleted folder: {folderpath}"
            return f"Folder not found: {folderpath}"
        except Exception as e:
            return f"Error deleting folder: {str(e)}"
    
    def copy_file(self, source, destination):
        """Copy a file"""
        try:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            return f"Copied {source} to {destination}"
        except Exception as e:
            return f"Error copying file: {str(e)}"
    
    def move_file(self, source, destination):
        """Move a file"""
        try:
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source, destination)
            return f"Moved {source} to {destination}"
        except Exception as e:
            return f"Error moving file: {str(e)}"
    
    def rename_file(self, old_path, new_path):
        """Rename a file or folder"""
        try:
            os.rename(old_path, new_path)
            return f"Renamed {old_path} to {new_path}"
        except Exception as e:
            return f"Error renaming: {str(e)}"
    
    def search_files(self, directory, pattern):
        """Search for files matching a pattern"""
        try:
            matches = glob.glob(os.path.join(directory, f"**/*{pattern}*"), recursive=True)
            if matches:
                return f"Found {len(matches)} files: {', '.join(matches[:10])}"
            return f"No files found matching '{pattern}' in {directory}"
        except Exception as e:
            return f"Error searching files: {str(e)}"
    
    def list_directory(self, directory="."):
        """List contents of a directory"""
        try:
            items = os.listdir(directory)
            folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]
            files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
            return f"Directory {directory}:\nFolders: {', '.join(folders[:10])}\nFiles: {', '.join(files[:10])}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def set_brightness(self, level):
        """Set screen brightness (0-100) - Windows only"""
        try:
            if self.system == "windows":
                subprocess.run(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})", shell=True)
                return f"Brightness set to {level}%"
            else:
                return "Brightness control not implemented for this OS"
        except Exception as e:
            return f"Error setting brightness: {str(e)}"
    
    def shutdown_system(self):
        """Shutdown the computer"""
        try:
            if self.system == "windows":
                subprocess.run("shutdown /s /t 5", shell=True)
            elif self.system == "darwin":
                subprocess.run("sudo shutdown -h +1", shell=True)
            else:
                subprocess.run("shutdown -h +1", shell=True)
            return "System will shutdown in 1 minute"
        except Exception as e:
            return f"Error shutting down: {str(e)}"
    
    def restart_system(self):
        """Restart the computer"""
        try:
            if self.system == "windows":
                subprocess.run("shutdown /r /t 5", shell=True)
            elif self.system == "darwin":
                subprocess.run("sudo shutdown -r +1", shell=True)
            else:
                subprocess.run("shutdown -r +1", shell=True)
            return "System will restart in 1 minute"
        except Exception as e:
            return f"Error restarting: {str(e)}"

    # Browser Operations
    def init_browser(self):
        """Initialize browser driver"""
        try:
            if not self.browser_driver:
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                self.browser_driver = webdriver.Chrome(options=options)
            return "Browser initialized"
        except Exception as e:
            return f"Error initializing browser: {str(e)}"
    
    def open_url(self, url):
        """Open a URL in the browser"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return f"Opened URL: {url}"
        except Exception as e:
            return f"Error opening URL: {str(e)}"
    
    def browser_back(self):
        """Go back in browser"""
        try:
            if self.browser_driver:
                self.browser_driver.back()
                return "Navigated back"
            else:
                pyautogui.hotkey('alt', 'left')
                return "Navigated back using keyboard shortcut"
        except Exception as e:
            return f"Error going back: {str(e)}"
    
    def browser_forward(self):
        """Go forward in browser"""
        try:
            if self.browser_driver:
                self.browser_driver.forward()
                return "Navigated forward"
            else:
                pyautogui.hotkey('alt', 'right')
                return "Navigated forward using keyboard shortcut"
        except Exception as e:
            return f"Error going forward: {str(e)}"
    
    def refresh_page(self):
        """Refresh the current page"""
        try:
            if self.browser_driver:
                self.browser_driver.refresh()
                return "Page refreshed"
            else:
                pyautogui.hotkey('ctrl', 'r')
                return "Page refreshed using keyboard shortcut"
        except Exception as e:
            return f"Error refreshing page: {str(e)}"
    
    def new_tab(self):
        """Open a new tab"""
        try:
            pyautogui.hotkey('ctrl', 't')
            return "New tab opened"
        except Exception as e:
            return f"Error opening new tab: {str(e)}"
    
    def close_tab(self):
        """Close the current tab"""
        try:
            pyautogui.hotkey('ctrl', 'w')
            return "Tab closed"
        except Exception as e:
            return f"Error closing tab: {str(e)}"
    
    def switch_tab(self, direction="next"):
        """Switch to next or previous tab"""
        try:
            if direction == "next":
                pyautogui.hotkey('ctrl', 'tab')
            else:
                pyautogui.hotkey('ctrl', 'shift', 'tab')
            return f"Switched to {direction} tab"
        except Exception as e:
            return f"Error switching tab: {str(e)}"

    # Accessibility Features
    def read_screen(self, x=None, y=None):
        """Take a screenshot and describe coordinates"""
        try:
            screenshot = pyautogui.screenshot()
            if x and y:
                pixel_color = screenshot.getpixel((x, y))
                return f"Pixel at ({x}, {y}) has color RGB{pixel_color}"
            else:
                screenshot.save("current_screen.png")
                return "Screenshot saved as current_screen.png"
        except Exception as e:
            return f"Error reading screen: {str(e)}"
    
    def click_at(self, x, y):
        """Click at specific coordinates"""
        try:
            pyautogui.click(x, y)
            return f"Clicked at coordinates ({x}, {y})"
        except Exception as e:
            return f"Error clicking at coordinates: {str(e)}"
    
    def type_text(self, text):
        """Type text at current cursor position"""
        try:
            pyautogui.write(text)
            return f"Typed: {text}"
        except Exception as e:
            return f"Error typing text: {str(e)}"
    
    def press_key(self, key):
        """Press a specific key or key combination"""
        try:
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            return f"Pressed key: {key}"
        except Exception as e:
            return f"Error pressing key: {str(e)}"
    
    def scroll(self, direction="down", clicks=3):
        """Scroll in a direction"""
        try:
            if direction == "down":
                pyautogui.scroll(-clicks)
            else:
                pyautogui.scroll(clicks)
            return f"Scrolled {direction} {clicks} clicks"
        except Exception as e:
            return f"Error scrolling: {str(e)}"

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.browser_driver:
                self.browser_driver.quit()
            return "Cleanup completed"
        except Exception as e:
            return f"Error during cleanup: {str(e)}"