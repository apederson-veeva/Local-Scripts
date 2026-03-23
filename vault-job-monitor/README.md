# Vault Job Monitor

A Python script to monitor the status of a Veeva Vault job and send periodic updates to a Google Chat webhook.

## Features

- Authenticates with Veeva Vault API.
- Polls job status at a configurable interval.
- Executes VQL queries to track progress (e.g., counting created records).
- Sends notifications to Google Chat.
- Supports local environment variables or Google Colab Secrets.

## Setup Instructions

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd vault-job-monitor
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    - Copy `.env.example` to `.env`.
    - Fill in your Vault credentials and job details:
      ```env
      VAULT_DOMAIN=https://your-vault-domain.veevavault.com
      VEEVA_USERNAME=your-username@example.com
      VEEVA_PASSWORD=your-password
      CHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/...
      JOB_ID=1234567
      ```

4.  **Run the script:**
    ```bash
    python monitor.py
    ```

### Google Colab Setup

1.  **Open the Notebook:**
    Upload `vault_job_monitor.ipynb` to Google Colab.

2.  **Configure Secrets:**
    - In the left sidebar, click the **Key icon (Secrets)**.
    - Add the following keys and their corresponding values:
        - `VAULT_DOMAIN`
        - `VEEVA_USERNAME`
        - `VEEVA_PASSWORD`
        - `CHAT_WEBHOOK_URL`
        - `JOB_ID`
        - `API_VERSION` (optional, defaults to v25.3)
        - `POLL_INTERVAL_SECONDS` (optional, defaults to 600)
        - `TOTAL_EXPECTED` (optional)
    - Ensure the "Notebook access" toggle is turned **ON** for these secrets.

3.  **Run the Cells:**
    Follow the instructions in the notebook to install dependencies and start the monitor.

## Configuration Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `VAULT_DOMAIN` | Your Veeva Vault domain URL. | `https://cdms-vault-training.veevavault.com` |
| `API_VERSION` | Veeva Vault API version. | `v25.3` |
| `JOB_ID` | The ID of the job to monitor. | `1122914` |
| `CHAT_WEBHOOK_URL` | Google Chat Webhook URL. | (Required) |
| `POLL_INTERVAL_SECONDS` | Interval between status checks. | `600` |
| `TOTAL_EXPECTED` | Total expected records to be created. | `268367` |
| `VEEVA_USERNAME` | Your Veeva Vault username. | (Required) |
| `VEEVA_PASSWORD` | Your Veeva Vault password. | (Required) |
