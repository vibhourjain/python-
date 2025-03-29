import requests
import os
import time
import subprocess
import logging

# Configuration
API_URL = "http://localhost:5000/health"
CHECK_INTERVAL = 300  # 5 minutes
LOG_FILE = "api_monitor.log"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def is_api_running():
    try:
        response = requests.get(API_URL, timeout=10)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def start_api():
    try:
        # Kill any existing instances
        subprocess.run(["pkill", "-f", "api.py"], check=False)
        # Start new instance in background
        subprocess.Popen(
            ["python3", "api.py"],
            stdout=open("api.log", "a"),
            stderr=subprocess.STDOUT
        )
        logging.info("API started successfully")
    except Exception as e:
        logging.error(f"Failed to start API: {str(e)}")

def monitor():
    while True:
        if not is_api_running():
            logging.warning("API is down! Attempting restart...")
            start_api()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    logging.info("Starting API monitor")
    monitor()

#For Windows users (create a batch file start_api.bat):
@echo off
:loop
tasklist | find "python.exe" > nul
if errorlevel 1 (
    echo Starting API...
    start python api.py
)
timeout /t 300 /nobreak > nul
goto loop
