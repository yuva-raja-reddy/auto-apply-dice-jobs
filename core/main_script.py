import os
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from dotenv import load_dotenv
import time
import re
import pyautogui
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
# Try both absolute and relative imports for compatibility
try:
    from dice_auto_apply.core.browser_detector import get_browser_path
    from dice_auto_apply.core.dice_login import login_to_dice
except ImportError:
    try:
        from ..core.browser_detector import get_browser_path
        from ..core.dice_login import login_to_dice
    except ImportError:
        from core.browser_detector import get_browser_path
        from core.dice_login import login_to_dice


# Load environment variables
load_dotenv()

def get_web_driver(headless=False, retry_with_alternative=True):
    """
    Initializes a Selenium WebDriver with fallback options.
    If the primary browser (Brave) fails to load, it will try Chrome as a fallback.
    
    Parameters:
        headless (bool): Whether to use headless mode
        retry_with_alternative (bool): Whether to try alternative browsers if primary fails
        
    Returns:
        WebDriver: Initialized WebDriver instance
    """
    import platform  # Add this import for system detection
    
    # Get browser path from .env or detect it
    web_browser_path = get_browser_path()
    
    if not web_browser_path:
        raise Exception("Browser path not found in .env file. Please set WEB_BROWSER_PATH.")

    tried_browsers = []
    
    # Try the primary browser first
    try:
        options = Options()
        options.binary_location = web_browser_path
        
        # Add headless mode options if requested
        if headless:
            options.add_argument("--headless")
            
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=EnableEphemeralFlashPermission")
        options.add_argument("--no-sandbox")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        
        # Clear browser cache and cookies
        options.add_argument("--disable-application-cache")
        options.add_argument("--incognito")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Test navigation to a simple page to verify browser is working
        driver.get("https://www.google.com")
        driver.find_element(By.TAG_NAME, "body")  # Should work if page loaded
        
        print(f"Successfully initialized browser: {os.path.basename(web_browser_path)}")
        return driver
        
    except Exception as e:
        tried_browsers.append(os.path.basename(web_browser_path))
        print(f"Error initializing primary browser ({os.path.basename(web_browser_path)}): {e}")
        
        if not retry_with_alternative:
            raise Exception(f"Failed to initialize browser and retry is disabled.")
    
    # If we get here, the primary browser failed - let's try alternatives
    system = platform.system()
    alternative_paths = []
    
    if system == "Darwin":  # macOS
        alternative_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Firefox.app/Contents/MacOS/firefox",
            "/Applications/Safari.app/Contents/MacOS/Safari"
        ]
    elif system == "Windows":
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        alternative_paths = [
            f"{program_files}\\Google\\Chrome\\Application\\chrome.exe",
            f"{program_files_x86}\\Google\\Chrome\\Application\\chrome.exe",
            f"{program_files}\\Mozilla Firefox\\firefox.exe",
            f"{program_files_x86}\\Mozilla Firefox\\firefox.exe"
        ]
    else:  # Linux
        alternative_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/firefox"
        ]
    
    # Try each alternative browser
    for alt_path in alternative_paths:
        if alt_path not in tried_browsers and os.path.exists(alt_path):
            try:
                options = Options()
                options.binary_location = alt_path
                
                if headless:
                    options.add_argument("--headless")
                    
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--incognito")  # Use incognito to avoid cache issues
                
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Test navigation
                driver.get("https://www.google.com")
                driver.find_element(By.TAG_NAME, "body")
                
                print(f"Successfully initialized alternative browser: {os.path.basename(alt_path)}")
                
                # Update the .env file with working browser
                from dotenv import set_key, find_dotenv
                dotenv_path = find_dotenv()
                if dotenv_path:
                    set_key(dotenv_path, "WEB_BROWSER_PATH", alt_path)
                    print(f"Updated WEB_BROWSER_PATH in .env file to: {alt_path}")
                
                return driver
                
            except Exception as e:
                tried_browsers.append(os.path.basename(alt_path))
                print(f"Error initializing alternative browser ({os.path.basename(alt_path)}): {e}")
    
    # If we get here, all browsers failed
    raise Exception(f"Failed to initialize any browser. Tried: {', '.join(tried_browsers)}")



def apply_to_job_url(driver, job_url):
    """
    Applies to a job without opening a new tab, preventing focus stealing.
    Instead navigates to job URL in the same tab and returns to original URL when done.
    """
    # Store current URL to return to later
    original_url = driver.current_url
    
    # Navigate to job URL in the same tab
    driver.get(job_url)
    
    wait = WebDriverWait(driver, 10)
    applied = False
    
    # move pointer to prevent sleeping
    pyautogui.moveRel(1, 1, duration=0.1)
    pyautogui.moveRel(-1, -1, duration=0.1)

    try:
        # First wait for #applyButton to be present in the DOM
        wait.until(EC.presence_of_element_located((By.ID, "applyButton")))
        
        # Wait and continuously poll for text in shadow DOM with a timeout
        max_attempts = 10
        shadow_content_found = False
        
        for attempt in range(max_attempts):
            # Check for existence of either "Application Submitted" or "Easy apply" text
            shadow_check = driver.execute_script("""
                // Get the apply-button-wc element
                const applyButtonWc = document.querySelector('apply-button-wc');
                if (!applyButtonWc) return { found: false, message: 'No apply-button-wc found' };
                
                // Wait for shadow root
                const shadowRoot = applyButtonWc.shadowRoot;
                if (!shadowRoot) return { found: false, message: 'No shadow root found' };
                
                // Get all text content from the shadow DOM
                const shadowText = shadowRoot.textContent || '';
                
                // Check for specific text content
                if (shadowText.includes('Application Submitted')) {
                    return { found: true, status: 'already_applied', message: 'Application Submitted text found' };
                } else if (shadowText.includes('Easy apply')) {
                    return { found: true, status: 'can_apply', message: 'Easy apply text found' };
                }
                
                return { found: false, message: 'No relevant text found in shadow DOM' };
            """)
            
            if shadow_check.get('found', False):
                shadow_content_found = True
                status = shadow_check.get('status', 'unknown')
                message = shadow_check.get('message', '')
                # print(f"Shadow DOM content found: {status} - {message}")
                break
            
            # If not found, wait and try again
            time.sleep(0.5)
        
        if not shadow_content_found:
            # print("Shadow DOM content not found after multiple attempts")
            driver.get(original_url)  # Go back to original URL
            return False
        
        # Process based on the shadow DOM status
        if status == 'already_applied':
            print(f"Skipping this Job as it is already applied: {job_url}")
            applied = True
            
        elif status == 'can_apply':
            # Click the Easy apply button
            click_success = driver.execute_script("""
                const applyButtonWc = document.querySelector('apply-button-wc');
                if (!applyButtonWc || !applyButtonWc.shadowRoot) return false;
                
                // Try three different ways to find the button
                const easyApplyBtn = 
                    // Method 1: Direct button in shadow DOM
                    applyButtonWc.shadowRoot.querySelector('button.btn.btn-primary') ||
                    // Method 2: Button inside apply-button element
                    (applyButtonWc.shadowRoot.querySelector('apply-button') && 
                     applyButtonWc.shadowRoot.querySelector('apply-button').shadowRoot &&
                     applyButtonWc.shadowRoot.querySelector('apply-button').shadowRoot.querySelector('button.btn.btn-primary')) ||
                    // Method 3: Find any button containing "Easy apply" text
                    Array.from(applyButtonWc.shadowRoot.querySelectorAll('button')).find(btn => 
                        btn.textContent.includes('Easy apply')
                    );
                
                if (!easyApplyBtn) return false;
                
                // Click the button
                easyApplyBtn.click();
                return true;
            """)
            
            if click_success:
                # Continue with the application process
                try:
                    # Locate the 'Next' button
                    next_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'btn-next') and normalize-space()='Next']")
                    ))
                    
                    # Click Next using JavaScript
                    driver.execute_script("arguments[0].click();", next_button)
                    
                    # Locate the 'Submit' button
                    submit_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'btn-next') and normalize-space()='Submit']")
                    ))
                    
                    # Click Submit using JavaScript
                    driver.execute_script("arguments[0].click();", submit_button)
                    
                    # Wait for confirmation
                    try:
                        confirmation = wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//header[contains(@class, 'post-apply-banner')]//h1[contains(text(), 'Application submitted')]")
                        ))
                        print(f"Application confirmed for New Job: {job_url}")
                        applied = True
                    except Exception as e:
                        print(f"Could not confirm application submission: {e}")
                        applied = False
                        
                except Exception as e:
                    applied = False
            else:
                print("Failed to click Easy apply button")
                applied = False
        else:
            print(f"Unknown shadow DOM state: {status}")
            applied = False
            
    except Exception as e:
        print(f"Error in application process: {e}")
        applied = False
        
    # Always return to the original URL
    driver.get(original_url)
    return applied

def fetch_jobs_with_requests(driver, search_query, include_keywords=None, exclude_keywords=None):
    """
    Use the existing browser instance to fetch job listings, preventing focus stealing
    and including mouse movements to prevent system sleeping.
    
    Returns:
        tuple: (included_jobs_list, excluded_jobs_list) - Lists of jobs that match and don't match criteria
    """
    print(f"Fetching jobs for query: {search_query}")
    
    # Format search parameters for URL
    encoded_query = quote(search_query)
    
    # Construct the URL with all filters already applied
    base_url = f"https://www.dice.com/jobs?q={encoded_query}&countryCode=US&radius=30&radiusUnit=mi&page=1&pageSize=100&filters.postedDate=ONE&filters.employmentType=CONTRACTS&language=en"
    
    included_jobs = []
    excluded_jobs = []  # Track excluded jobs with reason
    total_jobs_found = 0
    
    try:
        # First load the initial page to get total job count
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get(base_url)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error loading initial page. Retry {attempt+1}/{max_retries}...")
                    time.sleep(2)
                else:
                    print(f"Failed to load initial page after {max_retries} attempts.")
                    raise e
        
        # Move mouse to prevent system sleeping
        pyautogui.moveRel(1, 1, duration=0.1)
        pyautogui.moveRel(-1, -1, duration=0.1)
        
        wait = WebDriverWait(driver, 20)  # Increased timeout
        
        # Wait for the page to load completely
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)  # Extra wait for dynamic content
        
        # Get total jobs from the job count element
        total_pages = 1
        try:
            # First try explicit wait for the element
            job_count_element = wait.until(EC.presence_of_element_located((By.ID, "totalJobCount")))
            # Additional JavaScript check to ensure element is visible and has text
            total_jobs_text = driver.execute_script("""
                const element = document.getElementById('totalJobCount');
                if (element && element.innerText.trim()) {
                    return element.innerText.trim();
                }
                return '0';
            """)
            
            total_jobs_text = total_jobs_text.replace(",", "")
            total_jobs = int(total_jobs_text)
            print(f"Total jobs for query '{search_query}': {total_jobs}")
            
            # Calculate total pages needed (100 jobs per page)
            jobs_per_page = 100
            total_pages = min(11, (total_jobs + jobs_per_page - 1) // jobs_per_page)  # Ceiling division, max 11 pages
            print(f"Will process {total_pages} pages ({jobs_per_page} jobs per page)")
            
        except Exception as e:
            print(f"Could not find total job count, defaulting to 3 pages: {str(e)}")
            total_jobs = 0
            total_pages = 3  # Default to 3 pages if we can't determine the count
        
        # Process each page based on calculated total
        for page in range(1, total_pages + 1):
            # Move mouse to prevent system sleeping
            pyautogui.moveRel(1, 1, duration=0.1)
            pyautogui.moveRel(-1, -1, duration=0.1)
            
            # Construct URL for current page
            current_url = base_url.replace("page=1", f"page={page}")
            print(f"Processing page {page}/{total_pages}")
            
            # Retry mechanism for loading each page
            page_load_success = False
            for retry in range(max_retries):
                try:
                    # Navigate to the page with timeout handling
                    driver.get(current_url)
                    
                    # Wait for job cards or error indication to appear
                    try:
                        # Wait longer for pages after page 3 (which seem problematic)
                        wait_time = 25 if page > 3 else 15
                        
                        # Wait for either job cards OR an indication there are no results
                        job_cards_present = driver.execute_script("""
                            return new Promise(resolve => {
                                const checkForElements = () => {
                                    const cards = document.querySelectorAll('dhi-search-card');
                                    const noResults = document.querySelector('.no-results-container');
                                    if (cards && cards.length > 0) {
                                        resolve(true);
                                    } else if (noResults) {
                                        resolve(false);
                                    } else {
                                        setTimeout(checkForElements, 500);
                                    }
                                };
                                checkForElements();
                            });
                        """)
                        
                        if not job_cards_present:
                            print(f"No job cards found on page {page} (confirmed by page)")
                            break
                            
                        page_load_success = True
                        break
                    except Exception:
                        if retry < max_retries - 1:
                            print(f"Waiting for job cards failed on page {page}. Retry {retry+1}/{max_retries}...")
                            time.sleep(2)
                        else:
                            print(f"Could not find job cards on page {page} after {max_retries} attempts.")
                
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"Error loading page {page}. Retry {retry+1}/{max_retries}...")
                        time.sleep(3)
                    else:
                        print(f"Failed to load page {page} after {max_retries} attempts. Error: {str(e)}")
            
            if not page_load_success:
                print(f"Skipping page {page} due to load failures.")
                continue
            
            # Find all job cards
            try:
                job_cards = driver.find_elements(By.CSS_SELECTOR, "dhi-search-card")
                if not job_cards:
                    print(f"No job cards found on page {page}")
                    continue
                    
                print(f"Found {len(job_cards)} jobs on page {page}")
                
                # Process each job card
                for card_index, card in enumerate(job_cards):
                    # Extract job details using JavaScript
                    job_data = driver.execute_script("""
                        const card = arguments[0];
                        
                        try {
                            // Get job title and URL
                            const titleElement = card.querySelector("a[data-cy='card-title-link']");
                            const jobTitle = titleElement ? titleElement.textContent.trim() : "Unknown";
                            const jobId = titleElement ? titleElement.id : null;
                            const jobUrl = jobId ? `https://www.dice.com/job-detail/${jobId}` : "Unknown";
                            
                            // Get company
                            const company = card.querySelector("a[data-cy='search-result-company-name']");
                            const companyName = company ? company.textContent.trim() : "Unknown";
                            
                            // Get location
                            const location = card.querySelector("span[data-cy='search-result-location']");
                            const jobLocation = location ? location.textContent.trim() : "Unknown";
                            
                            // Get employment type
                            const empType = card.querySelector("span[data-cy='search-result-employment-type']");
                            const jobEmpType = empType ? empType.textContent.trim() : "Unknown";
                            
                            // Get posted date
                            const posted = card.querySelector("span[data-cy='card-posted-date']");
                            const jobPostedDate = posted ? posted.textContent.trim() : "Unknown";
                            
                            return {
                                jobTitle,
                                jobUrl,
                                companyName,
                                jobLocation,
                                jobEmpType,
                                jobPostedDate,
                                error: null
                            };
                        } catch (err) {
                            return {
                                error: err.toString(),
                                html: card.innerHTML.substring(0, 200) + "..."
                            };
                        }
                    """, card)
                    
                    # Skip if error in extraction
                    if job_data.get('error'):
                        continue
                        
                    job_title = job_data.get('jobTitle', "Unknown")
                    job_url = job_data.get('jobUrl', "Unknown")
                    company_name = job_data.get('companyName', "Unknown")
                    job_location = job_data.get('jobLocation', "Unknown")
                    job_employment_type = job_data.get('jobEmpType', "Unknown")
                    job_posted_date = job_data.get('jobPostedDate', "Unknown")
                    
                    # Create job object
                    job_entry = {
                        "Job Title": job_title,
                        "Job URL": job_url,
                        "Company": company_name,
                        "Location": job_location,
                        "Employment Type": job_employment_type,
                        "Posted Date": job_posted_date,
                        "Applied": False
                    }
                    
                    # Apply keyword filtering with reasons for exclusion
                    include_job = True
                    exclusion_reason = ""
                    job_title_lower = job_title.lower()
                    
                    # Check exclude keywords
                    if exclude_keywords and any(keyword.lower() in job_title_lower for keyword in exclude_keywords):
                        matching_keywords = [kw for kw in exclude_keywords if kw.lower() in job_title_lower]
                        exclusion_reason = f"Contains excluded keywords: {', '.join(matching_keywords)}"
                        include_job = False
                    
                    # Check include keywords
                    if include_keywords and not any(keyword.lower() in job_title_lower for keyword in include_keywords):
                        exclusion_reason = f"Missing required keywords: {', '.join(include_keywords)}"
                        include_job = False
                    
                    if include_job:
                        included_jobs.append(job_entry)
                    else:
                        # Add exclusion reason to the job entry
                        job_entry["Exclusion Reason"] = exclusion_reason
                        excluded_jobs.append(job_entry)
                
                total_jobs_found += len(job_cards)
                
            except Exception as e:
                print(f"Error processing job cards on page {page}: {str(e)}")
    
    except Exception as e:
        print(f"Error during job fetching: {str(e)}")
    
    print(f"Total jobs processed: {total_jobs_found}")
    print(f"Jobs included after filtering: {len(included_jobs)}")
    print(f"Jobs excluded after filtering: {len(excluded_jobs)}")
    
    return included_jobs, excluded_jobs


            

def save_to_excel(job_data, filename="job_application_report.xlsx"):
    """
    Saves job data to an Excel file.
    """
    try:
        df = pd.DataFrame(job_data["jobs"])
        df.to_excel(filename, index=False)
        print(f"Job application report saved to {filename}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

def main():
    # Record the start time of the entire script
    script_start_time = time.time()
    
    # Disable PyAutoGUI failsafe to prevent accidental triggering
    pyautogui.FAILSAFE = False
    
    driver = get_web_driver()  # Use browser
    
    # Define file names for fresh start
    applied_jobs_file = "applied_jobs.xlsx"
    not_applied_jobs_file = "not_applied_jobs.xlsx"
    job_report_file = "job_application_report.xlsx"
    excluded_jobs_file = "excluded_jobs.xlsx"
 
    # Delete existing files before login to start fresh (excluding applied_jobs.xlsx)
    for file in [not_applied_jobs_file, job_report_file, excluded_jobs_file]:
        if os.path.exists(file):
            os.remove(file)
            
    # Ensure applied_jobs.xlsx exists before writing
    if not os.path.exists(applied_jobs_file):
        df_empty = pd.DataFrame(columns=["Job Title", "Job URL", "Company", "Location", "Employment Type", "Posted Date", "Applied"])
        df_empty.to_excel(applied_jobs_file, index=False)

    job_data = {
        "Total Jobs Posted Today": 0,
        "jobs": []
    }

    try:
        # Record login start time
        login_start_time = time.time()
        
        if login_to_dice(driver):
            login_time = time.time() - login_start_time
            print(f"Login successful in {login_time:.2f} seconds. Starting job search...")

            # Move mouse to prevent system sleeping
            pyautogui.moveRel(1, 1, duration=0.1)
            pyautogui.moveRel(-1, -1, duration=0.1)

            # Use existing driver to fetch jobs
            collected_jobs = {}  # Dictionary to hold unique jobs by URL
            excluded_jobs = []   # List to hold excluded jobs
            fetch_start_time = time.time()
            
            for query in DICE_SEARCH_QUERIES:
                # Pass the existing driver to fetch_jobs_with_requests
                included_jobs, query_excluded_jobs = fetch_jobs_with_requests(driver, query, INCLUDE_KEYWORDS, EXCLUDE_KEYWORDS)
                
                # Add each job to the collected jobs dictionary
                for job in included_jobs:
                    if job["Job URL"] not in collected_jobs:
                        collected_jobs[job["Job URL"]] = job
                
                # Add to excluded jobs list
                excluded_jobs.extend(query_excluded_jobs)
                
                print(f"Query '{query}' returned {len(included_jobs)} jobs")
                
                # Mouse movement between queries to prevent sleep
                pyautogui.moveRel(1, 1, duration=0.1)
                pyautogui.moveRel(-1, -1, duration=0.1)
                
            fetch_time = time.time() - fetch_start_time
            print(f"Finished fetching jobs in {fetch_time:.2f} seconds")

            # Save excluded jobs to Excel
            if excluded_jobs:
                df_excluded = pd.DataFrame(excluded_jobs)
                df_excluded.to_excel(excluded_jobs_file, index=False)
                print(f"Saved {len(excluded_jobs)} excluded jobs to {excluded_jobs_file}")

            # Merge all job details into job_data
            job_data["jobs"] = list(collected_jobs.values())
            print(f"==========> Total unique jobs collected from all queries: {len(job_data['jobs'])}")
            
            # Rest of your code stays the same...
            # Check for already applied jobs
            if not os.path.exists(not_applied_jobs_file):
                df_empty = pd.DataFrame(columns=["Job Title", "Job URL", "Company", "Location", "Employment Type", "Posted Date", "Applied"])
                df_empty.to_excel(not_applied_jobs_file, index=False)
                
            existing_applied_jobs = set()
            existing_not_applied_jobs = set()

            if os.path.exists(applied_jobs_file):
                try:
                    df_applied = pd.read_excel(applied_jobs_file)
                    existing_applied_jobs = set(df_applied["Job URL"].dropna())
                except Exception as e:
                    print(f"Error loading existing applied jobs: {e}")

            if os.path.exists(not_applied_jobs_file):
                try:
                    df_not_applied = pd.read_excel(not_applied_jobs_file)
                    existing_not_applied_jobs = set(df_not_applied["Job URL"].dropna())
                except Exception as e:
                    print(f"Error loading not applied jobs: {e}")

            # Count already applied jobs
            already_applied_count = sum(1 for job in job_data["jobs"] if job["Job URL"] in existing_applied_jobs)
            print(f"==========> Skipping jobs that were already applied: {already_applied_count}")

            # Filter jobs before applying
            pending_jobs = [job for job in job_data["jobs"] if job["Job URL"] not in existing_applied_jobs]
            print(f"==========> Total jobs to apply for: {len(pending_jobs)}")
            
            # Calculate and display the estimated time
            print(f"==========> Estimated time to apply all {len(pending_jobs)} jobs: {len(pending_jobs)//8//60} hours {len(pending_jobs)//8%60} minutes")
            
            # Record application start time
            apply_start_time = time.time()
            successful_applications = 0
            failed_applications = 0
            
            # Process only pending jobs
            for job_index, job in enumerate(pending_jobs):
                # Move mouse every 3 jobs to prevent system sleeping
                if job_index % 3 == 0:
                    pyautogui.moveRel(1, 1, duration=0.1)
                    pyautogui.moveRel(-1, -1, duration=0.1)
                
                job_start_time = time.time()
                
                if not job["Applied"] and job["Job URL"] != "Unknown":
                    applied = apply_to_job_url(driver, job["Job URL"])
                    job["Applied"] = applied
                    
                    job_time = time.time() - job_start_time
                    
                    if applied:
                        successful_applications += 1
                        try:
                            df_existing = pd.read_excel(applied_jobs_file)
                        except Exception:
                            df_existing = pd.DataFrame(columns=["Job Title", "Job URL", "Company", "Location", "Employment Type", "Posted Date", "Applied"])
                        df_new = pd.DataFrame([job])
                        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                        df_combined.to_excel(applied_jobs_file, index=False)
                    else:
                        failed_applications += 1
                        try:
                            df_existing = pd.read_excel(not_applied_jobs_file)
                        except Exception:
                            df_existing = pd.DataFrame(columns=["Job Title", "Job URL", "Company", "Location", "Employment Type", "Posted Date", "Applied"])
                        df_new = pd.DataFrame([job])
                        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                        df_combined.to_excel(not_applied_jobs_file, index=False)
                    
                    # Print progress every 5 jobs
                    if (job_index + 1) % 5 == 0 or job_index == len(pending_jobs) - 1:
                        elapsed = time.time() - apply_start_time
                        progress = (job_index + 1) / len(pending_jobs) * 100
                        estimated_total = elapsed / (job_index + 1) * len(pending_jobs)
                        remaining = estimated_total - elapsed
                        
                        print(f"Progress: {job_index+1}/{len(pending_jobs)} jobs ({progress:.1f}%) | "
                              f"Last job: {job_time:.1f}s | "
                              f"Success rate: {successful_applications}/{job_index+1} | "
                              f"Est. remaining: {remaining/60:.1f} mins")

            apply_time = time.time() - apply_start_time
            applications_per_minute = (successful_applications + failed_applications) / (apply_time / 60) if apply_time > 0 else 0
            print(f"\n==========> Application phase completed in {apply_time:.2f} seconds")
            print(f"==========> Successfully applied: {successful_applications} jobs")
            print(f"==========> Failed applications: {failed_applications} jobs")
            print(f"==========> Average application rate: {applications_per_minute:.2f} jobs per minute")

            # Save final data to JSON
            with open("job_data.json", "w") as json_file:
                json.dump(job_data, json_file, indent=4)
            print("Job data saved to job_data.json")

            # Final save to Excel
            save_to_excel(job_data)

        else:
            print("Login failed. Exiting...")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pass
        # Don't close the browser immediately for debugging
        # driver.quit()
        
    # Calculate and print total execution time
    total_time = time.time() - script_start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print("\n===== EXECUTION TIME SUMMARY =====")
    print(f"Total script execution time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    if 'pending_jobs' in locals() and pending_jobs:
        print(f"Average time per job processed: {total_time/len(pending_jobs):.2f} seconds")
    print("==================================")



if __name__ == "__main__":
    # Search in dice
    DICE_SEARCH_QUERIES = ["AI ML", "Gen AI", "Agentic AI", "Data Engineer", "Data Analyst", "Machine Learning"]  # You can update this list anytime

    # Optional: Define keywords for filtering job applications
    EXCLUDE_KEYWORDS = ["Manager", "Director",".net", "SAP","java","w2 only","only w2","no c2c",
        "only on w2","w2 profiles only","tester","f2f"]  # Add more if needed
    INCLUDE_KEYWORDS = ["AI", "Artificial","Inteligence","Machine","Learning", "ML", "Data", "NLP", "ETL",
        "Natural Language Processing","analyst","scientist","senior","cloud", 
        "aws","gcp","Azure","agentic","python","rag","llm"]  # Add more if needed

    start_time = datetime.datetime.now()
    main()
    end_time = datetime.datetime.now()
    print(f"Exact Execution time: {end_time - start_time}")