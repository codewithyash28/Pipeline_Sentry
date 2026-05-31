import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

# Initialize Vertex AI (Ensure your GOOGLE_APPLICATION_CREDENTIALS env var is set)
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # For testing purposes if no key is provided
        return None
    return genai.Client(api_key=api_key)

client = None
if os.getenv("GEMINI_API_KEY"):
    client = get_client()

# Define the precise system instruction for the Triage Engine
SYSTEM_INSTRUCTION = """
You are the Triage Brain for Pipeline Sentry. Your job is to analyze Fivetran error payloads and generate an immediate response plan.

Classify the incoming JSON into one of two categories:
1. Transient Errors (e.g., 500, Network Timeout, Rate Limits):
   - Set Priority to Medium/Low.
   - Suggest an automated retry window.
   - remediation.requires_human_approval = false
2. Fatal Errors (e.g., 401 Unauthorized, Expired Keys, Schema Drifts):
   - Set Priority to High.
   - Require immediate human rotation or configuration updates.
   - remediation.requires_human_approval = true

You must strictly output your response in JSON format:
{
  "priority": "High | Medium | Low",
  "root_cause": "1-sentence plain English summary of what broke",
  "suggested_fix": "Actionable, specific next step",
  "remediation": {
    "requires_human_approval": true | false,
    "step_by_step_plan": "Detailed plan for remediation"
  }
}
"""

def run_triage(data=None):
    # 1. Load the mock data if not provided
    if data is None:
        try:
            with open("tests/mock_logs.json", "r") as f:
                mock_data = f.read()
        except FileNotFoundError:
            mock_data = '{"error": "mock_logs.json not found"}'
    else:
        mock_data = data
    
    # 2. Instantiate Gemini
    if client is None:
        raise ValueError("Gemini client is not initialized. Please set GEMINI_API_KEY.")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=mock_data,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            response_mime_type="application/json"
        )
    )
    
    # 3. Request the evaluation
    print("\n--- Gemini Triage Report Output ---")
    print(response.text)

    # 4. Log usage metadata
    if hasattr(response, 'usage_metadata'):
        print(f"Tokens used: Prompt={response.usage_metadata.prompt_token_count}, Candidates={response.usage_metadata.candidates_token_count}")

    return response
   
if __name__ == "__main__":
    run_triage()