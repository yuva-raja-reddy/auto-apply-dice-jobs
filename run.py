#!/usr/bin/env python3
"""
Dice Auto Apply Bot Runner
This script ensures chromedriver has proper permissions before launching the application
"""
import os
import sys

def main():
    """Main entry point for the application"""
    # Add the current directory to Python path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Fix chromedriver permissions
    try:
        from fix_chromedriver import fix_chromedriver_permissions
        fix_chromedriver_permissions()
    except Exception as e:
        print(f"Warning: Could not fix ChromeDriver permissions: {e}")
    
    # Import and run the main app
    try:
        from app_tkinter import main
        main()
    except ImportError:
        print("ERROR: Could not import app_tkinter module. Make sure you're running from the correct directory.")
        sys.exit(1)

if __name__ == "__main__":
    main()
