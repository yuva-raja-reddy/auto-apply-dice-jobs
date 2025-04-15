import os
import platform
import subprocess
import glob
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

def detect_browser_paths():
    """
    Detects browser paths on the current system (macOS or Windows) and updates .env file.
    Searches in this order: Brave, Chrome, Safari, Edge, Firefox.
    
    Returns:
        str: The path to the detected browser or None if no browser is found.
    """
    system = platform.system()
    browser_paths = {}
    
    # print(f"Detecting browsers on {system} platform...")
    
    if system == "Darwin":  # macOS
        # Define common browser paths on macOS
        possible_paths = {
            "Brave": [
                "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                "/Applications/Brave Browser Dev.app/Contents/MacOS/Brave Browser Dev",
                "/Applications/Brave Browser Beta.app/Contents/MacOS/Brave Browser Beta"
            ],
            "Chrome": [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Google Chrome Dev.app/Contents/MacOS/Google Chrome Dev",
                "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
            ],
            "Safari": ["/Applications/Safari.app/Contents/MacOS/Safari"],
            "Firefox": ["/Applications/Firefox.app/Contents/MacOS/firefox"],
            "Edge": ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
        }
        
        # Check each browser path
        for browser, paths in possible_paths.items():
            for path in paths:
                if os.path.exists(path):
                    browser_paths[browser] = path
                    # print(f"Found {browser} at: {path}")
    
    
    elif system == "Windows":
        # Get all user profiles 
        users_dir = os.path.join(os.environ.get("SystemDrive", "C:"), "Users")
        user_folders = [f for f in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, f)) 
                        and f not in ["Public", "Default", "Default User", "All Users"]]
        
        # Standard program locations
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        
        # Possible browser paths across all users and standard locations
        possible_paths = {
            "Brave": [
                f"{program_files}\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                f"{program_files_x86}\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
            ],
            "Chrome": [
                f"{program_files}\\Google\\Chrome\\Application\\chrome.exe",
                f"{program_files_x86}\\Google\\Chrome\\Application\\chrome.exe"
            ],
            "Edge": [
                f"{program_files}\\Microsoft\\Edge\\Application\\msedge.exe",
                f"{program_files_x86}\\Microsoft\\Edge\\Application\\msedge.exe"
            ],
            "Firefox": [
                f"{program_files}\\Mozilla Firefox\\firefox.exe",
                f"{program_files_x86}\\Mozilla Firefox\\firefox.exe"
            ]
        }
        
        # Add user-specific locations for browsers
        for user in user_folders:
            user_path = os.path.join(users_dir, user)
            
            # AppData locations
            local_app_data = os.path.join(user_path, "AppData", "Local")
            roaming_app_data = os.path.join(user_path, "AppData", "Roaming")
            
            # Add common user-specific browser locations
            if os.path.exists(local_app_data):
                possible_paths["Brave"].extend([
                    os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
                    # Handle potential user-specific install directories
                    *glob.glob(os.path.join(user_path, "**", "Brave-Browser", "Application", "brave.exe"), recursive=True)
                ])
                
                possible_paths["Chrome"].extend([
                    os.path.join(local_app_data, "Google", "Chrome", "Application", "chrome.exe"),
                    # Handle potential user-specific install directories
                    *glob.glob(os.path.join(user_path, "**", "Chrome", "Application", "chrome.exe"), recursive=True)
                ])
                
                possible_paths["Edge"].extend([
                    os.path.join(local_app_data, "Microsoft", "Edge", "Application", "msedge.exe"),
                    # Handle potential user-specific install directories
                    *glob.glob(os.path.join(user_path, "**", "Edge", "Application", "msedge.exe"), recursive=True)
                ])
            
            if os.path.exists(roaming_app_data):
                possible_paths["Firefox"].extend([
                    os.path.join(roaming_app_data, "Mozilla", "Firefox", "firefox.exe"),
                    # Handle potential user-specific install directories
                    *glob.glob(os.path.join(user_path, "**", "Firefox", "firefox.exe"), recursive=True)
                ])
        
        # Check each browser path
        for browser, paths in possible_paths.items():
            for path in paths:
                if os.path.exists(path):
                    browser_paths[browser] = path
                    # print(f"Found {browser} at: {path}")
                    break  # Take first found instance of each browser

    # Try to detect browsers using command line on Windows or Unix-like
    if not browser_paths:
        try:
            if system == 'Windows':
                # Try using where command on Windows
                for browser in ["brave", "chrome", "msedge", "firefox"]:
                    try:
                        result = subprocess.run(f'where {browser}', shell=True, capture_output=True, text=True)
                        if result.returncode == 0 and result.stdout.strip():
                            path = result.stdout.strip().split('\n')[0]  # Take first result
                            browser_name = browser.capitalize()
                            if browser == "msedge":
                                browser_name = "Edge"
                            browser_paths[browser_name] = path
                            # print(f"Found {browser_name} at: {path}")
                    except Exception:
                        pass
            else:
                # Try using which command on Unix-like
                for browser in ["brave", "chrome", "chromium", "firefox", "safari"]:
                    try:
                        result = subprocess.run(f'which {browser}', shell=True, capture_output=True, text=True)
                        if result.returncode == 0 and result.stdout.strip():
                            browser_name = browser.capitalize()
                            browser_paths[browser_name] = result.stdout.strip()
                            # print(f"Found {browser_name} at: {result.stdout.strip()}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error detecting browser using command line: {e}")
    
    # IMPORTANT CHANGE: Always clear the existing browser path in .env to force detection
    from dotenv import set_key, find_dotenv
    dotenv_path = find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path)  # Load first to get other variables
        set_key(dotenv_path, "WEB_BROWSER_PATH", "")  # Clear the browser path
    
    # Order of preference: Brave, Chrome, Safari, Edge, Firefox
    preferred_order = ["Brave", "Chrome", "Safari", "Edge", "Firefox"]
    
    # Return the first browser found in the preferred order
    selected_browser = None
    selected_path = None
    
    for browser in preferred_order:
        if browser in browser_paths:
            selected_browser = browser
            selected_path = browser_paths[browser]
            print(f"Selected {selected_browser} browser")
            break
    
    if selected_path:
        # print(f"Selected {selected_browser} at {selected_path} as the preferred browser")
        update_env_file(selected_path)
        return selected_path
    else:
        print("No compatible browsers found!")
        return None

def update_env_file(browser_path):
    """
    Updates or creates .env file with the browser path.
    
    Parameters:
        browser_path (str): Path to the browser executable.
    """
    dotenv_path = find_dotenv()
    if not dotenv_path:
        dotenv_path = os.path.join(os.getcwd(), '.env')
        Path(dotenv_path).touch(exist_ok=True)
        # print(f"Created new .env file at {dotenv_path}")
    
    # Load existing .env file
    load_dotenv(dotenv_path)
    
    # Get current value
    current_path = os.getenv("WEB_BROWSER_PATH")
    
    if current_path != browser_path:
        # Update .env file with new browser path
        # Using set_key to maintain other variables in .env
        set_key(dotenv_path, "WEB_BROWSER_PATH", browser_path)
        # print(f"Updated WEB_BROWSER_PATH in .env file: {browser_path}")
    else:
        # print(f"WEB_BROWSER_PATH already set to: {browser_path}")
        pass
    
    return browser_path

def get_browser_path():
    """
    Gets the browser path from .env file or detects it if not available.
    
    Returns:
        str: The path to the browser.
    """
    # Load .env file
    load_dotenv()
    
    # Check if WEB_BROWSER_PATH exists in .env
    browser_path = os.getenv("WEB_BROWSER_PATH")
    
    if browser_path and os.path.exists(browser_path):
        # print(f"Using existing browser path from .env: {browser_path}")
        return browser_path
    
    # Detect browser paths if not found in .env or if path doesn't exist
    browser_path = detect_browser_paths()
    
    if not browser_path:
        raise Exception("No compatible browser found on your system. Please install Brave, Chrome, Safari, Edge, or Firefox.")
    
    return browser_path

if __name__ == "__main__":
    try:
        browser_path = get_browser_path()
        print(f"Browser path successfully set: {browser_path}")
    except Exception as e:
        print(f"Error: {e}")