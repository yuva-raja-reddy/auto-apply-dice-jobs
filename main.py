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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from dotenv import load_dotenv
import time  # Added import for time
import re  # Added import for regex
import pyautogui

# Load environment variables
load_dotenv()

def get_brave_driver():
    """
    Initializes a Selenium WebDriver for Brave Browser with proper settings.

    Returns:
        webdriver.Chrome: A Brave browser instance.
    """
    brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # Update path if needed

    options = Options()
    options.binary_location = brave_path
    options.add_argument("--start-maximized")  # Maximize browser
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    options.add_argument("--disable-popup-blocking")  # Prevent popups from blocking execution
    options.add_argument("--disable-web-security")  # Allow cross-domain scripting
    options.add_argument("--disable-features=EnableEphemeralFlashPermission")
    options.add_argument("--no-sandbox")  # Fixes profile directory creation issues
    options.add_argument("--remote-debugging-port=9222")  # Allows debugging
    options.add_argument("--disable-infobars")  # Disable automation-controlled banner
    options.add_argument("--disable-notifications")  # Disable popups
    options.add_argument("--disable-gpu")  # Disable GPU acceleration to avoid graphical issues

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Mask WebDriver property to avoid bot detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def login_to_dice(driver):
    """
    Logs into Dice using credentials from the .env file.
    
    Parameters:
        driver (selenium.webdriver): Selenium WebDriver instance.
    
    Returns:
        bool: True if login is successful, False otherwise.
    """
    username = os.getenv("DICE_USERNAME")
    password = os.getenv("DICE_PASSWORD")
    
    if not username or not password:
        raise Exception("Dice credentials not found in .env file. Please set DICE_USERNAME and DICE_PASSWORD.")
    
    driver.get("https://www.dice.com/dashboard/login")
    wait = WebDriverWait(driver, 10)

    try:
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.clear()
        email_field.send_keys(username)

        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='sign-in-button']")))
        continue_button.click()

        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.clear()
        password_field.send_keys(password)

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='submit-password']")))
        login_button.click()

        wait.until(EC.presence_of_element_located((By.XPATH, "//form[@class='flex h-auto w-full flex-row rounded-lg rounded-bl-lg bg-white']")))
        print("Login successful!")
        return True

    except Exception as e:
        print("Login failed:", e)
        return False

def apply_filters(driver):
    """
    Applies job search filters:
    - Clicks 'Posted Date: Today' and waits.
    - Selects 'Contract' employment type and waits.
    - Scrolls to and selects 100 jobs per page.
    
    Parameters:
        driver (selenium.webdriver): Selenium WebDriver instance.
    """
    wait = WebDriverWait(driver, 15)

    try:
        # Click "Posted Date: Today" based on text and wait for reload
        today_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Today') and @data-cy='posted-date-option']")))
        today_button.click()
        time.sleep(2)  # Ensure page has enough time to refresh
        print("Selected 'Today' filter.")

        # Click "Contract" employment type and wait for reload
        contract_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@data-cy='facet-group-toggle']/button[@aria-label='Filter Search Results by Contract']")))
        contract_checkbox.click()
        time.sleep(2)  # Ensure page has enough time to refresh
        print("Selected 'Contract' filter.")

        # Scroll smoothly to page size dropdown
        page_size_dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='pageSize_2']")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", page_size_dropdown)
        time.sleep(1)  # Allow time for scroll

        # Click and select "100" in the dropdown
        wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@id='pageSize_2']"))).click()
        time.sleep(1)  # Small delay before selecting the option
        wait.until(EC.element_to_be_clickable((By.XPATH, "//option[@value='100']"))).click()
        time.sleep(2)  # Ensure page has enough time to refresh
        print("Set results per page to 100.")

    except Exception as e:
        print("Error applying filters:", e)

def get_total_jobs(driver):
    """
    Retrieves the total number of job postings.

    Parameters:
        driver (selenium.webdriver): Selenium WebDriver instance.

    Returns:
        int: The total job count.
    """
    try:
        wait = WebDriverWait(driver, 30)
        
        # Apply filters before retrieving job count
        apply_filters(driver)

        job_count_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@id='totalJobCount']")))
        total_jobs_text = job_count_element.text.strip().replace(",", "")  # Remove commas before conversion
        total_jobs = int(total_jobs_text)
        
        print(f"Total jobs found today: {total_jobs}")
        return total_jobs
    except Exception as e:
        print("Error retrieving total job count:", e)
        return 0

def search_jobs(driver):
    """
    Manually enters job search criteria and clicks the search button.
    
    Parameters:
        driver (selenium.webdriver): Selenium WebDriver instance.
    """
    wait = WebDriverWait(driver, 10)

    try:
        # Retrieve job search parameters from .env
        job_query = DICE_SEARCH_QUERY

        # Locate and enter the job title/skills
        job_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Job title, skill, company, keyword']")))
        job_field.clear()
        job_field.send_keys(job_query)

        # Skip entering location (leave it empty)

        # Click the search button
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='job-search-search-bar-search-button']")))
        search_button.click()

        print(f"Searching for jobs: {job_query}")

    except Exception as e:
        print("Error while searching for jobs:", e)

def get_job_links(driver):
    """
    Extracts job titles, companies, locations, employment types, and posted dates from the current page.

    Parameters:
        driver (selenium.webdriver): Selenium WebDriver instance.

    Returns:
        list: A list of dictionaries containing job details.
    """
    job_list = []
    try:
        wait = WebDriverWait(driver, 10)
        job_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//dhi-search-card")))
        
        for job in job_elements:
            job_title = "Unknown"
            job_company = "Unknown"
            job_location = "Unknown"
            job_employment_type = "Unknown"
            job_posted_date = "Unknown"
            job_url = "Unknown"

            try:
                job_title_element = job.find_element(By.XPATH, ".//a[@data-cy='card-title-link']")
                job_title = job_title_element.text.strip()
                job_url = job_title_element.get_attribute("id")
                if job_url:
                    job_url = f"https://www.dice.com/job-detail/{job_url}"
            except Exception as e:
                print(f"Error retrieving job ID: {e}")

            try:
                job_company = job.find_element(By.XPATH, ".//a[@data-cy='search-result-company-name']").text.strip()
            except Exception:
                pass

            try:
                job_location = job.find_element(By.XPATH, ".//span[@data-cy='search-result-location']").text.strip()
            except Exception:
                pass

            try:
                job_employment_type = job.find_element(By.XPATH, ".//span[@data-cy='search-result-employment-type']").text.strip()
            except Exception:
                pass

            try:
                job_posted_date = job.find_element(By.XPATH, ".//span[@data-cy='card-posted-date']").text.strip()
            except Exception:
                pass

            job_list.append({
                "Job Title": job_title,
                "Job URL": job_url,
                "Company": job_company,
                "Location": job_location,
                "Employment Type": job_employment_type,
                "Posted Date": job_posted_date,
                "Applied": False
            })

        print(f"Collected {len(job_list)} job links from page.")

    except Exception as e:
        print("Error retrieving job links:", e)

    return job_list

def apply_to_job_url(driver, job_url):
    """
    Opens the job URL in a new tab, performs the application process,
    and returns True if the application was successful.
    """
    driver.execute_script("window.open(arguments[0], '_blank');", job_url)
    new_tab_handle = driver.window_handles[-1]
    driver.switch_to.window(new_tab_handle)
    
    wait = WebDriverWait(driver, 5)
    applied = False
    
    # move pointer to prevent sleeping
    pyautogui.moveRel(1, 1, duration=0.1)
    pyautogui.moveRel(-1, -1, duration=0.1)


    try:
        # Locate the apply button container
        apply_button_container = wait.until(EC.presence_of_element_located((By.ID, "applyButton")))
        time.sleep(1)
        # Use ActionChains to move the mouse pointer to the apply button and click
        actions = ActionChains(driver)
        actions.move_to_element(apply_button_container).pause(1).click().perform()
        print("Clicked Easy Apply button using mouse pointer.")
 
        # Locate the 'Next' button using a robust XPath
        next_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn-next') and normalize-space()='Next']")))
        
        # Scroll the button into view and ensure it is visible
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
        
        # Try clicking normally; if it fails, click using JavaScript execution
        try:
            next_button.click()
        except Exception as click_exception:
            print("Normal click next button failed, trying JavaScript click.")
            driver.execute_script("arguments[0].click();", next_button)
            print("Clicked Next button using JavaScript.")
        # time.sleep(2)

        try:
            # Locate the 'Submit' button
            submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn-next') and normalize-space()='Submit']")))

            # Scroll the button into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
            time.sleep(1)  # Allow time for scrolling

            # Click the 'Submit' button using ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(submit_button).pause(1).click().perform()
            print("Clicked Submit button using mouse pointer.")

            # Wait for the page to refresh and check for the confirmation banner
            try:
                confirmation_banner = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//header[contains(@class, 'post-apply-banner')]//h1[contains(text(), 'Application submitted')]"))
                )
                print("Application successfully submitted!")
                applied = True

                # Close the current job tab and switch back to the main search tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                return applied
            except Exception:
                print("Application submission confirmation not found. Might have failed.")
                applied = False

        except Exception as e:
            print("Error interacting with Submit button:", e)
            applied = False
    except Exception as e:
        print(f"Error applying to job at {job_url}")
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return applied

def save_to_excel(job_data, filename="job_application_report.xlsx"):
    """
    Saves job data to an Excel file.

    Parameters:
        job_data (dict): Dictionary containing job application data.
        filename (str): Output Excel filename.
    """
    try:
        df = pd.DataFrame(job_data["jobs"])
        df.to_excel(filename, index=False)
        print(f"Job application report saved to {filename}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")

def main():
    driver = get_brave_driver()  # Use Brave browser
    # Define file names for fresh start
    applied_jobs_file = "applied_jobs.xlsx"
    not_applied_jobs_file = "not_applied_jobs.xlsx"
    job_report_file = "job_application_report.xlsx"

    # Delete existing files before login to start fresh
    for file in [not_applied_jobs_file, job_report_file]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted old {file} to start fresh.")

    # Ensure applied_jobs.xlsx exists before writing
    if not os.path.exists(applied_jobs_file):
        df_empty = pd.DataFrame(columns=["Job Title", "Job URL", "Company", "Location", "Employment Type", "Posted Date", "Applied"])
        df_empty.to_excel(applied_jobs_file, index=False)
        print("Created 'applied_jobs.xlsx' as it was missing.")
    job_data = {
        "Total Jobs Posted Today": 0,
        "jobs": []
    }

    try:
        if login_to_dice(driver):
            print("Login successful. Starting job search...")
            driver.execute_script("document.body.style.zoom='75%'")
            # Perform job search manually
            search_jobs(driver)

            # Get the total job count after applying filters
            total_jobs = get_total_jobs(driver)
            job_data["Total Jobs Posted Today"] = total_jobs

            # Calculate number of pages
            jobs_per_page = 100
            total_pages = (total_jobs // jobs_per_page) + (1 if total_jobs % jobs_per_page > 0 else 0)

            # Iterate through pages
            for page in range(1, total_pages + 1):
                print(f"Scraping page {page}...")
                job_data["jobs"].extend(get_job_links(driver))

                # Update the page number in the URL instead of clicking the button
                current_url = driver.current_url
                next_page_url = re.sub(r"page=\d+", f"page={page + 1}", current_url) if "page=" in current_url else f"{current_url}&page={page + 1}"
                
                print(f"Navigating to next page: {next_page_url}")
                driver.get(next_page_url)
                time.sleep(2)  # Allow time for page load

                # Save data to Excel after each page
                save_to_excel(job_data)

            # Save final data to JSON
            with open("job_data.json", "w") as json_file:
                json.dump(job_data, json_file, indent=4)
            print("Job data saved to job_data.json")

            # Load existing applied and not-applied jobs to avoid redundant processing
            # Files already defined and recreated at startup
            # applied_jobs_file and not_applied_jobs_file are available from earlier
            if not os.path.exists(not_applied_jobs_file):
                df_empty = pd.DataFrame(columns=["Job Title", "Job URL", "Company", "Location", "Employment Type", "Posted Date", "Applied"])
                df_empty.to_excel(not_applied_jobs_file, index=False)
                print("Created 'not_applied_jobs.xlsx' as it was missing.")
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
            print(f"==========> Skipping {already_applied_count} jobs that were already applied.")

            # Filter jobs before applying
            pending_jobs = [job for job in job_data["jobs"] if job["Job URL"] not in existing_applied_jobs]
            print(f"==========> Total jobs to process: {len(pending_jobs)}")

            # Process only pending jobs
            for job in pending_jobs:
                if not job["Applied"] and job["Job URL"] != "Unknown":
                    print(f"Processing application for job: {job['Job Title']}")
                    applied = apply_to_job_url(driver, job["Job URL"])
                    job["Applied"] = applied
                    if applied:
                        try:
                            df_existing = pd.read_excel(applied_jobs_file)
                        except Exception:
                            df_existing = pd.DataFrame(columns=["Job Title", "Job URL", "Company", "Location", "Employment Type", "Posted Date", "Applied"])
                        df_new = pd.DataFrame([job])
                        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                        df_combined.to_excel(applied_jobs_file, index=False)
                    else:
                        try:
                            df_existing = pd.read_excel(not_applied_jobs_file)
                        except Exception:
                            df_existing = pd.DataFrame(columns=["Job Title", "Job URL", "Company", "Location", "Employment Type", "Posted Date", "Applied"])
                        df_new = pd.DataFrame([job])
                        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                        df_combined.to_excel(not_applied_jobs_file, index=False)

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
        input("Press Enter to close the browser...")  # Keeps the browser open for debugging
    finally:
        pass
        # driver.quit()

def test_apply_single_job(job_url):
    """
    Logs in and applies to a single job URL for testing purposes.
    
    Parameters:
        job_url (str): The URL of the job to apply for.
    """
    driver = get_brave_driver()  # Use Brave browser
    try:
        if login_to_dice(driver):
            print("Login successful. Applying to single job...")
            applied = apply_to_job_url(driver, job_url)
            print(f"Application status: {'Success' if applied else 'Failed'} for job: {job_url}")
        else:
            print("Login failed. Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to close the browser...")  # Keeps the browser open for debugging
    finally:
        driver.quit()




if __name__ == "__main__":
    # Search in dice
    DICE_SEARCH_QUERY="AI ML" # Change to which jobs you are applying for.
    main()
    # test_apply_single_job("https://www.dice.com/job-detail/48ff85b2-6984-4105-b5c6-ea5e5d969a3d")
