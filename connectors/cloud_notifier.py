import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_slack_alert(triage_data: dict = None, usage_metadata: dict = None) -> bool:
    """Sends a formatted markdown message to the configured Slack Webhook."""
    if triage_data:
        priority = triage_data.get("priority", "N/A")
        root_cause = triage_data.get("root_cause", "N/A")
        suggested_fix = triage_data.get("suggested_fix", "N/A")

        message = f"""
🚨 *Pipeline Sentry Triage Report* 🚨
• *Priority:* {priority}
• *Root Cause:* {root_cause}
• *Suggested Fix:* {suggested_fix}"""

        if usage_metadata:
            # Handle both dictionary and object attributes
            if isinstance(usage_metadata, dict):
                prompt_tokens = usage_metadata.get("prompt_token_count", 0)
                candidate_tokens = usage_metadata.get("candidates_token_count", 0)
            else:
                prompt_tokens = getattr(usage_metadata, "prompt_token_count", 0)
                candidate_tokens = getattr(usage_metadata, "candidates_token_count", 0)

            message += f"\n\n*Cost Tracking:* {prompt_tokens + candidate_tokens} tokens used."
    else:
        message="""
🚨 *Pipeline Sentry Triage Report* 🚨
• *Priority:* High
• *Root Cause:* The Stripe connector failed to authenticate due to an invalid or expired API key.
• *Suggested Fix:* Update the Stripe connector's API key and secret in Fivetran with valid credentials from the Stripe dashboard."""

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