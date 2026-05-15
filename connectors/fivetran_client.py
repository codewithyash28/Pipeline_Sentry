"""
Custom wrappers for Fivetran MCP tools.
Handles get_sync_status & list_logs.
"""
import requests
import requests
import os
url="https://fivetran.com"
class FivetranClient:
    def get_sync_status(self, connector_id: str):
        pass

    def list_logs(self, connector_id: str):
        pass
    
    def get_broken_connectors(self):
        BrokenConnectors=[]
        connectorResp=requests.get(
            url+"/v1/connectors?limit=5",
            headers={
                "Authorization":f"Basic {os.getenv("Base64_Encoded_apiKey")}",
                "content-type":"application/json"
            }
        )
        for connector in connectorResp.json().get('data', {}).get('items', []):
            print(f"Name: {connector['name']} | ID: {connector['id']} | Status: {connector['status']}")
        return 
        

