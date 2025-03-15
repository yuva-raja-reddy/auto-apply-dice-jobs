import os
import pandas as pd
import time
from main import login_to_dice, get_brave_driver
import pyautogui

# Define file path
file_path = "not_applied_jobs.xlsx"

# Check if file exists before loading
if not os.path.exists(file_path):
    print("Error: 'not_applied_jobs.xlsx' not found. Exiting...")
    exit()

# Load the Excel file
df = pd.read_excel(file_path)

# Extract job URLs
job_urls = df["Job URL"].dropna().tolist()

# Setup Brave WebDriver
driver = get_brave_driver()

def open_jobs():
    batch_size = 50
    for i in range(0, len(job_urls), batch_size):
        batch = job_urls[i:i + batch_size]
        
        for job_url in batch:
            print(f"Opening job: {job_url}")
            # move pointer to prevent sleeping
            pyautogui.moveRel(1, 1, duration=0.1)
            pyautogui.moveRel(-1, -1, duration=0.1)
            driver.execute_script("window.open(arguments[0], '_blank');", job_url)
            time.sleep(1)  # Allow some time for the page to load
        
        print(f"Opened {len(batch)} jobs. Press Enter to continue with the next batch...")
        input()  # Wait for user input before continuing

# Perform login
if login_to_dice(driver):
    print("Login successful! Now opening job links...")
    open_jobs()
    print("All job links opened in new tabs.")
else:
    print("Login failed. Exiting...")
    driver.quit()
