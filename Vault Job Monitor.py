import requests
import time
import os

# --- Configuration ---
VAULT_DOMAIN = "https://cdms-vault-training.veevavault.com"
API_VERSION = "v25.3" # Update to your current API version if needed
JOB_ID = "1122914" # The ID of the job you are monitoring
CHAT_WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQAayWH0qg/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=eod_3nC3gj9_v_ewyA_cGpiHAiKF-qS3gIkus6rMg9A"
POLL_INTERVAL_SECONDS = 600 # Check every 10 minutes

# The total number of records you expect the job to create
TOTAL_EXPECTED = 268367

# Credentials (preferably set as environment variables in your OS)
USERNAME = os.environ.get("VEEVA_USERNAME", "")
PASSWORD = os.environ.get("VEEVA_PASSWORD", "")

# Global variable to hold the active session token
SESSION_ID = None

def authenticate():
    """Authenticates with Veeva Vault and retrieves a new Session ID."""
    global SESSION_ID
    print("Authenticating with Veeva Vault...")
    
    url = f"{VAULT_DOMAIN}/api/{API_VERSION}/auth"
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status() 
    
    data = response.json()
    if data.get("responseStatus") == "SUCCESS":
        SESSION_ID = data["sessionId"]
        print("Successfully authenticated.")
    else:
        raise Exception(f"Authentication failed. Check credentials: {data}")

def check_vault_job_status():
    """Checks the status of the job in Veeva Vault."""
    global SESSION_ID
    
    # If this is the first run and we don't have a session, authenticate
    if not SESSION_ID:
        authenticate()
        
    url = f"{VAULT_DOMAIN}/api/{API_VERSION}/services/jobs/{JOB_ID}"
    headers = {
        "Authorization": SESSION_ID,
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    # Catch an expired session, re-authenticate, and retry the request
    if response.status_code == 401:
        print("Session expired or invalid. Attempting to re-authenticate...")
        authenticate()
        headers["Authorization"] = SESSION_ID
        response = requests.get(url, headers=headers)
        
    response.raise_for_status() # Catch any other HTTP errors
    
    data = response.json()
    
    if data.get("responseStatus") == "SUCCESS":
        return data["data"]["status"]
    else:
        raise Exception(f"Failed to fetch job: {data}")

def get_training_assignment_count():
    """Executes a VQL query to get the total number of training assignments created."""
    query = "SELECT id, status__v FROM training_assignment__v WHERE (training_requirement__v = 'V1G000000008001') PAGESIZE 0"
    url = f"{VAULT_DOMAIN}/api/{API_VERSION}/query"
    
    headers = {
        "Authorization": SESSION_ID,
        "Accept": "application/json"
    }
    params = {"q": query} 
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    if data.get("responseStatus") == "SUCCESS":
        return data["responseDetails"]["total"]
    else:
        print(f"⚠️ Warning: Failed to execute VQL: {data}")
        return "Error"

def send_chat_notification(status, total_created, is_finished=False):
    """Sends a formatted message to the Google Chat webhook."""
    
    if not is_finished:
        message_text = f"⏳ *Veeva Vault Polling Update*\nJob ID: `{JOB_ID}` is currently processing.\nCurrent Status: *{status}*\nTotal Created: *{total_created} / {TOTAL_EXPECTED}*"
    else:
        if status == "SUCCESS":
            message_text = f"✅ *Veeva Vault Update*\nJob ID: `{JOB_ID}` has finished running.\nFinal Status: *{status}*\nTotal Created: *{total_created} / {TOTAL_EXPECTED}*"
        else:
            message_text = f"⚠️ *Veeva Vault Alert*\nJob ID: `{JOB_ID}` ended with status: *{status}*.\nTotal Created: *{total_created} / {TOTAL_EXPECTED}*\nYou might want to check the logs."

    payload = {"text": message_text}
    response = requests.post(CHAT_WEBHOOK_URL, json=payload)
    
    if response.status_code == 429:
        print("⚠️ Warning: Google Chat is rate-limiting your webhook. Consider increasing your poll interval.")

def monitor_job():
    """Main polling loop."""
    print(f"Starting monitor for Vault Job {JOB_ID}...")
    
    finished_statuses = ["SUCCESS", "ERRORS", "ABORTED", "CANCELLED"]
    
    while True:
        try:
            status = check_vault_job_status()
            print(f"[{time.strftime('%X')}] Current status: {status}")
            
            is_finished = status in finished_statuses
            
            # Get the current total created and send a chat message on EVERY check
            total_created = get_training_assignment_count()
            send_chat_notification(status, total_created, is_finished)
            
            if is_finished:
                print("Job finished. Final notification sent. Exiting.")
                break
                
            time.sleep(POLL_INTERVAL_SECONDS)
            
        except Exception as e:
            print(f"Monitor stopped due to an error: {e}")
            break

if __name__ == "__main__":
    monitor_job()