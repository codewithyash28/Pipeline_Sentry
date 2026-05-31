import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def send_slack_approval_card(plan: str, context: dict = None):
    """Sends an interactive Slack message with Approve/Abort buttons."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🚨 *Manual Approval Required for Remediation*\n*Proposed Plan:* {plan}"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve Run"},
                    "style": "primary",
                    "value": "approve",
                    "action_id": "approve_action"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Abort"},
                    "style": "danger",
                    "value": "abort",
                    "action_id": "abort_action"
                }
            ]
        }
    ]

    if not webhook_url:
        print("[Warning] SLACK_WEBHOOK_URL not set. Printing HITL Approval Card to console:")
        print(json.dumps(blocks, indent=2))
        return False

    payload = {"blocks": blocks}
    try:
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error sending HITL card to Slack: {e}")
        return False

def handle_agent_decision(agent_json):
    """
    Parses agent decision and determines if HITL is required.
    Returns 'AWAITING_APPROVAL' or 'EXECUTE_IMMEDIATELY'.
    """
    remediation = agent_json.get("remediation", {})
    if remediation.get("requires_human_approval"):
        plan = remediation.get("step_by_step_plan", "No plan provided.")
        send_slack_approval_card(plan, context=agent_json)
        return "AWAITING_APPROVAL"
    else:
        return "EXECUTE_IMMEDIATELY"
