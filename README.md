# Dice Auto Apply Bot

Dice Auto Apply Bot is a Python-based application that automates your job application process on Dice.com. It leverages Selenium for web automation, BeautifulSoup for HTML parsing, and Tkinter for a user-friendly GUI.

## Features
- **Automated Job Search & Application:** Automatically search for and apply to job listings using specified queries and filters.
- **Graphical User Interface:** Tkinter-based UI for easy control and monitoring of the application process.
- **Cross-Platform Support:** Works on both Windows and macOS/Linux systems.
- **Customizable Configuration:** Set job search queries, include/exclude keywords, and configure job application limits.
- **Logging and Reporting:** Detailed logs and Excel outputs for applied, not applied, and excluded jobs.

## Demo Video

Watch a complete demonstration of how to set up and use the Dice Auto Apply Bot:

[![Watch the Demo Video](https://img.shields.io/badge/Watch-Demo_Video-red?style=for-the-badge&logo=google-drive&logoColor=white)](https://drive.google.com/file/d/1c0Y69PZ5UlFb3dZg0_-_wn7UibRQQwlW/view?usp=sharing)

The video shows step-by-step instructions for installation, configuration, and running the application on both Windows and Mac.

## Prerequisites
- Python 3.x installed.
- A web browser (preferably Brave Browser, but Chrome, Firefox, Edge or Safari will also work).
- Git (optional) if you wish to clone the repository.

## Installation

### Clone the Repository
Copy and run these commands:

```bash
git clone https://github.com/yuva-raja-reddy/auto-apply-dice-jobs.git
cd auto-apply-dice-jobs
```

### Create and Activate a Virtual Environment

#### For Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### For macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
After activating your virtual environment, install the required packages:

```bash
pip install -r requirements.txt
```

If your Python installation doesn't include Tkinter, install it using:

```bash
# For macOS
brew install python-tk

# For Ubuntu/Debian
sudo apt-get install python3-tk
```

## Running the Application

### For Windows
```bash
# Using the run script
python run.py

# Or directly
python app_tkinter.py
```

### For macOS / Linux
```bash
# Using the run script (recommended)
python3 run.py

# Or directly
python3 app_tkinter.py

# If you encounter permission issues with chromedriver
chmod +x run.py
./run.py
```

The run.py script automatically handles chromedriver permissions, which is particularly helpful for macOS users.

## Browser Configuration

The application will automatically detect your installed browsers in this preference order:
1. Brave Browser (recommended)
2. Google Chrome
3. Safari (macOS only)
4. Microsoft Edge
5. Firefox

If Brave Browser is installed, it will be used by default. If not, the application will fall back to the next available browser in the preference list.

## Using the Application

Once started, the GUI allows you to:
- Test your Dice login credentials.
- Configure job search queries and keywords.
- Start the automated job application process.
- Monitor progress and view real-time logs.
- Access Excel files with summaries of applied, not applied, and excluded jobs.

### Application Settings via the GUI
1. Navigate to the **Settings** tab.
2. Enter your Dice login credentials and test the connection.
3. Configure your job search queries, include/exclude keywords, and set the maximum number of applications.
4. Click **Save Settings** to persist your configuration.
5. Return to the **Run Bot** tab to start applying.

## Troubleshooting

- **Slow Login Issues:**  
  The application has been updated to handle slower login processes. If you still experience issues, try increasing timeouts in the settings.

- **WebDriver Issues:**  
  The application uses `webdriver_manager` to handle drivers automatically. If you encounter issues, try running `run.py` which fixes common permission issues.

- **Browser Detection Problems:**  
  If your browser isn't being detected correctly, you can manually specify the browser path in the .env file.

## Contributing
Feel free to fork this repository and submit pull requests for improvements, additional features, or bug fixes.

## Support
If you find this project useful, please consider supporting its development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/yuvarajareddy)