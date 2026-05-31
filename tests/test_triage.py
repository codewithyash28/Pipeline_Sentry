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
        "root_cause": "401 Unauthorized: Invalid API Key",
        "suggested_fix": "Rotate Stripe API Key",
        "remediation": {
            "requires_human_approval": True,
            "step_by_step_plan": "1. Fetch new key from Stripe. 2. Update Secret Manager."
        }
    })
    # Add usage metadata for later testing
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

@patch("agents.triage_agent.client")
def test_triage_fatal_error(mock_client, mock_gemini_response_401):
    mock_client.models.generate_content.return_value = mock_gemini_response_401

    mock_data = '{"error_message": "401 Unauthorized"}'
    response = run_triage(data=mock_data)

    result = json.loads(response.text)
    assert result["priority"] == "High"
    assert result["remediation"]["requires_human_approval"] is True

    decision = handle_agent_decision(result)
    assert decision == "AWAITING_APPROVAL"

@patch("agents.triage_agent.client")
def test_triage_transient_error(mock_client, mock_gemini_response_timeout):
    mock_client.models.generate_content.return_value = mock_gemini_response_timeout

    mock_data = '{"error_message": "ETIMEDOUT"}'
    response = run_triage(data=mock_data)

    result = json.loads(response.text)
    assert result["priority"] == "Medium"
    assert result["remediation"]["requires_human_approval"] is False

    decision = handle_agent_decision(result)
    assert decision == "EXECUTE_IMMEDIATELY"
