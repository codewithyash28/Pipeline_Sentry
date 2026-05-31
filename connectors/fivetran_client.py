"""
Custom wrappers for Fivetran MCP tools.
Handles get_sync_status & list_logs.
"""
import os

import requests

FIVETRAN_BASE_URL = "https://api.fivetran.com"


class FivetranClient:
    def get_sync_status(self, connector_id: str):
        pass

    def list_logs(self, connector_id: str):
        pass

    def get_broken_connectors(self):
        broken_connectors = []
        connector_resp = requests.get(
            f"{FIVETRAN_BASE_URL}/v1/connectors?limit=5",
            headers={
                "Authorization": f"Basic {os.getenv('Base64_Encoded_apiKey')}",
                "Content-Type": "application/json",
            },
        )
        for connector in connector_resp.json().get("data", {}).get("items", []):
            print(
                f"Name: {connector['name']} | ID: {connector['id']} | Status: {connector['status']}"
            )
            if connector.get("status", {}).get("setup_state") == "broken":
                broken_connectors.append(connector)
        return broken_connectors


