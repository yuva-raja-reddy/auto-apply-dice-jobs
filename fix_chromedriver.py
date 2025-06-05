# dice_auto_apply/fix_chromedriver.py

import os
import stat
import glob
import platform
import subprocess

def fix_chromedriver_permissions():
    """Fix permissions on ChromeDriver executable"""
    print("Fixing ChromeDriver permissions...")
    
    # Get user's home directory
    home_dir = os.path.expanduser("~")
    
    # Look for chromedriver in .wdm directory
    chromedriver_pattern = os.path.join(home_dir, ".wdm", "drivers", "chromedriver", "**", "chromedriver*")
    
    # Find all chromedriver files
    chromedriver_files = glob.glob(chromedriver_pattern, recursive=True)
    
    if not chromedriver_files:
        print("No ChromeDriver files found.")
        return False
        
    success = False
    
    for driver_path in chromedriver_files:
        if os.path.isfile(driver_path) and not os.path.islink(driver_path):
            try:
                print(f"Setting permissions for: {driver_path}")
                
                # Add execute permissions (chmod +x)
                os.chmod(driver_path, os.stat(driver_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                
                # On macOS, also remove quarantine attribute
                if platform.system() == "Darwin":
                    try:
                        subprocess.run(["xattr", "-d", "com.apple.quarantine", driver_path], 
                                      stderr=subprocess.DEVNULL)
                    except:
                        pass  # Ignore if xattr command fails
                        
                print(f"Fixed permissions for {os.path.basename(driver_path)}")
                success = True
            except Exception as e:
                print(f"Error setting permissions for {driver_path}: {e}")
    
    return success

if __name__ == "__main__":
    # This allows running the script directly to fix permissions
    fixed = fix_chromedriver_permissions()
    
    if fixed:
        print("Successfully fixed ChromeDriver permissions.")
    else:
        print("Could not fix ChromeDriver permissions. Please check manually.")
