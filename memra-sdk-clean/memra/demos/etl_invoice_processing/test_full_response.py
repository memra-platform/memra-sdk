import os
import requests
import json

api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

resp = requests.post(
    f"{api_url}/tools/execute",
    json={
        "tool_name": "PDFProcessor",
        "hosted_by": "memra",
        "input_data": {
            "file": "/uploads/6f4538c0-8fce-4488-be49-1a78afc58a4a.pdf",
            "schema": [{"column_name": "vendor_name", "data_type": "character varying"}]
        }
    },
    headers={"X-API-Key": api_key}
)

print("Full response:")
print(json.dumps(resp.json(), indent=2))
