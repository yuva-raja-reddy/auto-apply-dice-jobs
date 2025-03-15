import pandas as pd
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from main import login_to_dice, get_brave_driver
import pyautogui
import os

# File paths
applied_reference_path = "applied_jobs_reference.xlsx"
not_applied_path = "not_applied_jobs.xlsx"
applied_jobs_path = "applied_jobs.xlsx"

# Setup WebDriver
driver = get_brave_driver()

# Perform login
if not login_to_dice(driver):
    print("Login failed. Exiting...")
    driver.quit()
    exit()

print("Login successful! Retrieving applied jobs...")

# Go to applied jobs page
driver.get("https://www.dice.com/my-jobs?type=applied&page=1")
time.sleep(3)  # Allow page to load

# Load existing applied jobs reference file
try:
    df_applied_reference = pd.read_excel(applied_reference_path)
    applied_job_urls = set(df_applied_reference["Job URL"].tolist())
except FileNotFoundError:
    df_applied_reference = pd.DataFrame(columns=["Job URL", "Job Title", "Company Name", "Posted Date"])
    applied_job_urls = set()

print(f"Total known applied jobs in reference: {len(applied_job_urls)}")

# Get total number of pages
max_page = int(driver.find_element(By.XPATH, "//*[@id='react-aria-:R6kvelafcq:-tabpanel-applied']/div[2]/nav/section/span[2]").text)
print(f"Total pages to scrape: {max_page}")

processed_pages = 0
scraped_jobs = 0
found_in_reference = 0
moved_to_applied = 0
Updated_jobs = False

# Loop through pages
for page in range(1, max_page + 1):
    print(f"Scraping page {page}...")
    driver.get(f"https://www.dice.com/my-jobs?type=applied&page={page}")
    time.sleep(2)
    
    # move pointer to prevent sleeping
    pyautogui.moveRel(1, 1, duration=0.1)
    pyautogui.moveRel(-1, -1, duration=0.1)

    job_elements = driver.find_elements(By.CSS_SELECTOR, "li.flex.justify-between.gap-x-6.py-5")

    for job in job_elements:
        try:
            job_title = job.find_element(By.CSS_SELECTOR, "h3 a").text
            job_url = job.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")
            company_name = job.find_element(By.CSS_SELECTOR, "p.text-font-secondary.text-sm").text
            posted_date = job.find_elements(By.TAG_NAME, "div")[-1].text
            
            # Fetch final redirected URL
            response = requests.get(job_url, allow_redirects=True)
            final_job_url = response.url
            
            # Stop searching further if job is already in reference
            if final_job_url in applied_job_urls:
                found_in_reference += 1
                print(f"Found existing job in reference ({final_job_url}), stopping further scraping.")
                Updated_jobs = True
                break

            # Append new job to reference immediately
            new_job = {
                "Job URL": final_job_url,
                "Job Title": job_title,
                "Company Name": company_name,
                "Posted Date": posted_date
            }
            df_applied_reference = pd.concat([df_applied_reference, pd.DataFrame([new_job])], ignore_index=True)
            applied_job_urls.add(final_job_url)
            scraped_jobs += 1
            
        except Exception as e:
            print(f"Error extracting job details: {e}")
    
    processed_pages += 1
    print(f"Scraped {scraped_jobs} jobs so far, processed {processed_pages}/{max_page} pages.")

    if Updated_jobs:
        break

# Save updated reference file
print("Saving updated reference file...")
df_applied_reference.to_excel(applied_reference_path, index=False, engine='openpyxl')

# Compare with not_applied_jobs.xlsx and move matched jobs
try:
    df_not_applied = pd.read_excel(not_applied_path)
except FileNotFoundError:
    print("No not_applied_jobs.xlsx found. Skipping update.")
    exit()

matched_jobs = df_not_applied[df_not_applied["Job URL"].isin(applied_job_urls)]

if not matched_jobs.empty:
    df_applied_jobs = pd.read_excel(applied_jobs_path) if os.path.exists(applied_jobs_path) else pd.DataFrame(columns=["Job URL", "Job Title", "Company Name", "Posted Date"])
    df_applied_jobs = pd.concat([df_applied_jobs, matched_jobs], ignore_index=True)
    df_applied_jobs.to_excel(applied_jobs_path, index=False, engine='openpyxl')
    
    df_not_applied = df_not_applied[~df_not_applied["Job URL"].isin(applied_job_urls)]
    df_not_applied.to_excel(not_applied_path, index=False, engine='openpyxl')
    
    moved_to_applied = len(matched_jobs)
    print(f"Moved {moved_to_applied} jobs to applied_jobs.xlsx and updated not_applied_jobs.xlsx.")

# Print Summary
print("--- Job Processing Summary ---")
print(f"Total pages scraped: {processed_pages}/{max_page}")
print(f"Total jobs found in reference: {found_in_reference}")
print(f"Total scrapped - new jobs applied: {scraped_jobs}")
print(f"Total jobs moved to applied: {moved_to_applied}")
print("Job checking completed.")