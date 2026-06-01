"""
Entry point for the polling loop.
Monitors Fivetran via MCP and triggers the agent on failure.
"""

import json

from agents.triage_agent import run_triage
from connectors.approval_gate import handle_agent_decision
from connectors.cloud_notifier import send_slack_alert


def main():
    print("Pipeline Sentry starting...")

    # Run triage on latest error logs
    response = run_triage()

    # Parse the triage result
    triage_data = json.loads(response.text)

    # Determine if human approval is needed
    decision = handle_agent_decision(triage_data)
    print(f"Decision: {decision}")

    # Send notification
    usage = None
    if hasattr(response, "usage_metadata"):
        usage = response.usage_metadata
    send_slack_alert(triage_data=triage_data, usage_metadata=usage)

    print("Pipeline Sentry run complete.")


if __name__ == "__main__":
    main()
