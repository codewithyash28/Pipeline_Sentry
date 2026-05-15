import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

# Initialize Vertex AI (Ensure your GOOGLE_APPLICATION_CREDENTIALS env var is set)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Define the precise system instruction for the Triage Engine
SYSTEM_INSTRUCTION = """
You are the Triage Brain for Pipeline Sentry. Your job is to analyze Fivetran error payloads and generate an immediate response plan.

Classify the incoming JSON into one of two categories:
1. Transient Errors (e.g., 500, Network Timeout, Rate Limits):
   - Set Priority to Medium/Low.
   - Suggest an automated retry window.
2. Fatal Errors (e.g., 401 Unauthorized, Expired Keys, Schema Drifts):
   - Set Priority to High.
   - Require immediate human rotation or configuration updates.

You must strictly output your response using the following Slack-ready format:
🚨 *Pipeline Sentry Triage Report* 🚨
• *Priority:* [High / Medium / Low]
• *Root Cause:* [1-sentence plain English summary of what broke]
• *Suggested Fix:* [Actionable, specific next step]
"""

def run_triage():
    # 1. Load the mock data we built in the last step
    with open("tests/mock_error.json", "r") as f:
        mock_data = f.read()
    
    # 2. Instantiate Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=mock_data,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2
        )
    )
    
    # 3. Request the evaluation
    print("\n--- Gemini Triage Report Output ---")
    print(response.text)
   
if __name__ == "__main__":
    run_triage()