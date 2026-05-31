import json
import pytest
from unittest.mock import MagicMock, patch
from agents.triage_agent import run_triage
from connectors.approval_gate import handle_agent_decision

@pytest.fixture
def mock_gemini_response_401():
    response = MagicMock()
    response.text = json.dumps({
        "priority": "High",
        "root_cause": "401 Unauthorized: Access token expired",
        "suggested_fix": "Rotate Stripe API Key",
        "remediation": {
            "requires_human_approval": True,
            "step_by_step_plan": "1. Fetch new key from Stripe. 2. Update Secret Manager."
        }
    })
    response.usage_metadata = MagicMock()
    response.usage_metadata.prompt_token_count = 100
    response.usage_metadata.candidates_token_count = 50
    return response

@pytest.fixture
def mock_gemini_response_timeout():
    response = MagicMock()
    response.text = json.dumps({
        "priority": "Medium",
        "root_cause": "ETIMEDOUT: Connection timed out",
        "suggested_fix": "Retry sync in 10 minutes",
        "remediation": {
            "requires_human_approval": False,
            "step_by_step_plan": "Wait and retry."
        }
    })
    response.usage_metadata = MagicMock()
    response.usage_metadata.prompt_token_count = 80
    response.usage_metadata.candidates_token_count = 30
    return response

def test_mock_logs_integrity():
    """Ensure mock_logs.json contains the expected keys."""
    with open("tests/mock_logs.json", "r") as f:
        logs = json.load(f)
    assert len(logs) >= 2
    assert "error_message" in logs[0]
    assert "error_message" in logs[1]

@patch("agents.triage_agent.client")
def test_triage_escalation_on_401(mock_client, mock_gemini_response_401):
    """Test that a 401 error is categorized as high priority requiring approval."""
    mock_client.models.generate_content.return_value = mock_gemini_response_401

    with open("tests/mock_logs.json", "r") as f:
        logs = json.load(f)

    # Simulate processing the 401 error from mock_logs.json
    error_log = next(log for log in logs if "401" in log["error_message"])
    response = run_triage(data=json.dumps(error_log))

    result = json.loads(response.text)
    assert result["priority"] == "High"
    assert result["remediation"]["requires_human_approval"] is True

    decision = handle_agent_decision(result)
    assert decision == "AWAITING_APPROVAL"

@patch("agents.triage_agent.client")
def test_triage_retry_on_timeout(mock_client, mock_gemini_response_timeout):
    """Test that a timeout error is categorized as a low/medium risk retry."""
    mock_client.models.generate_content.return_value = mock_gemini_response_timeout

    with open("tests/mock_logs.json", "r") as f:
        logs = json.load(f)

    error_log = next(log for log in logs if "ETIMEDOUT" in log["error_message"])
    response = run_triage(data=json.dumps(error_log))

    result = json.loads(response.text)
    assert result["priority"] in ["Medium", "Low"]
    assert result["remediation"]["requires_human_approval"] is False

    decision = handle_agent_decision(result)
    assert decision == "EXECUTE_IMMEDIATELY"
