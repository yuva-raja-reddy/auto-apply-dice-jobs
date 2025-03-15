# Dice Job Auto-Apply Bot

### **Project Overview**
- This project automates job applications **only for Dice.com** using Selenium and Python.
- It applies for jobs, tracks application history, and allows manual job applications when required.

### **Installation Guide**
#### 1. **Clone the Repository**
```bash
git clone https://github.com/yuva-raja-reddy/auto-apply-dice-jobs.git
cd auto-apply-dice-jobs
```

#### 2. **Set Up Virtual Environment (Optional but Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

#### 3. **Install Dependencies**
```bash
pip install -r requirements.txt -q
```

### **Configuration**
#### 4. **Set Up `.env` File for Dice Credentials**
Create a `.env` file in the project root and add:
```plaintext
DICE_USERNAME="your_email_here"
DICE_PASSWORD="your_password_here"
```

#### 5. **Define Job Search Criteria in `main.py`**
Modify the following variable in `main.py`:
```python
DICE_SEARCH_QUERY = "Gen AI"  # Change this to your desired job search
```

### **How to Use the Bot**
#### **Step 1: Run `main.py` to Auto-Apply for Jobs**
```bash
python main.py
```
- This script logs into Dice and attempts to auto-apply to all relevant job postings.
- Successfully applied jobs are logged in `applied_jobs.xlsx`.
- Jobs that couldn't be applied are recorded in `not_applied_jobs.xlsx`.

#### **Step 2: Check If a Job Was Already Applied (`check_if_already_applied.py`)**
```bash
python check_if_already_applied.py
```
- This script scans `applied_jobs_reference.xlsx` to see if a job has been previously applied.
- If running for the first time, it may take longer to collect historical applied jobs.
- It updates `not_applied_jobs.xlsx` and `applied_jobs.xlsx` accordingly.

#### **Step 3: Manually Apply for Jobs (`open_not_applied_jobs.py`)**
```bash
python open_not_applied_jobs.py
```
- This script opens a **maximum of 50 jobs at a time** from `not_applied_jobs.xlsx`.
- Users manually apply for these jobs.
- After completing manual applications, run `check_if_already_applied.py` to update records.

### **Understanding Excel Files**
- `applied_jobs_reference.xlsx`: **Complete history of all applied jobs (manual + auto).**
- `applied_jobs.xlsx`: **Only jobs auto-applied using this bot.**
- `not_applied_jobs.xlsx`: **Jobs that were not yet applied.**
- **Do NOT delete any of these files**, as they are essential for tracking job applications.

### **Additional Notes**
- The bot prevents duplicate applications by referencing `applied_jobs_reference.xlsx`.
- The script waits and interacts dynamically to handle page loads.
- The automation ensures a smooth job application process while allowing manual intervention when needed.
