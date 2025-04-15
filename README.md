# Dice Auto Apply Bot

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/yuvarajareddy)

Dice Auto Apply Bot is a Python-based application that automates your job application process on Dice.com. It leverages Selenium for web automation, BeautifulSoup for HTML parsing, and Tkinter for a user-friendly GUI.

## Features
- **Automated Job Search & Application:** Automatically search for and apply to job listings using specified queries and filters.
- **Graphical User Interface:** Tkinter-based UI for easy control and monitoring of the application process.
- **Cross-Platform Support:** Instructions provided for both Windows and macOS (or Linux) users.
- **Customizable Configuration:** Set job search queries, include/exclude keywords, and configure job application limits.
- **Logging and Reporting:** Detailed logs are maintained alongside Excel outputs for applied, not applied, and excluded jobs.

## Prerequisites
- Python 3.x installed.
- A supported web browser (e.g., Chrome, Brave) along with a compatible WebDriver.
- Git (optional) if you wish to clone the repository.

## Installation

### Clone the Repository
Copy and remove the comment markers before running these commands:

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

If your python package doesnt have Tkinter, install using:

```bash
brew install python-tk # for mac
```

### Application Settings via the GUI
1. Run the application (see below) and navigate to the **Settings** tab.
2. Enter your Dice login credentials and test the connection.
3. Configure your job search queries, include/exclude keywords, and set the maximum number of applications.
4. Click **Save Settings** to persist your configuration.

## Running the Application

Launch the application using the following command after removing the comment markers:

```bash
python app_tkinter.py
```

Once started, the GUI will enable you to:
- Test your Dice login credentials.
- Initiate the automated job application process.
- Monitor progress and view real-time logs.
- Open Excel files containing summaries of applied, not applied, and excluded jobs.

## Troubleshooting

- **WebDriver Issues:**  
  Ensure your browser and its corresponding WebDriver are up to date. This project uses `webdriver_manager` to help manage drivers automatically.

- **Virtual Environment Problems:**  
  Make sure you are using the correct commands for your operating system.

- **Login Issues:**  
  Verify that the credentials in your `.env` file and those entered in the GUI settings match your Dice account information.

## Contributing
Feel free to fork this repository and submit pull requests for improvements, additional features, or bug fixes.

## Support
If you find this project useful, please consider supporting its development:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/yuvarajareddy)
