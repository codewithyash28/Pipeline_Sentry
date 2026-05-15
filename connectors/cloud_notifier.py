import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_slack_alert() -> bool:
    message="""
    🚨 *Pipeline Sentry Triage Report* 🚨
    • *Priority:* High
    • *Root Cause:* The Stripe connector failed to authenticate due to an invalid or expired API key.
    • *Suggested Fix:* Update the Stripe connector's API key and secret in Fivetran with valid credentials from the Stripe dashboard."""
    """Sends a formatted markdown message to the configured Slack Webhook."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("[Warning] SLACK_WEBHOOK_URL not set. Printing message to console instead:")
        print(message)
        return False

    payload = {"text": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        if response.status_code == 200:
            print("🚀 Triage report successfully pushed to Slack.")
            return True
        else:
            print(f"❌ Failed to send Slack alert. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Slack: {e}")
        return False



if __name__ == "__main__":
    send_slack_alert()