import os
import requests
import json

api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

schema = [
    {"column_name": "vendor_name", "data_type": "character varying"}
]

resp = requests.post(
    f"{api_url}/tools/execute",
    json={
        "tool_name": "PDFProcessor",
        "hosted_by": "memra",
        "input_data": {
            "file": "/uploads/6f4538c0-8fce-4488-be49-1a78afc58a4a.pdf",
            "schema": schema
        }
    },
    headers={"X-API-Key": api_key}
)

print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    result = resp.json()
    print(f"Success: {result.get('success')}")
    print(f"Keys: {list(result.keys())}")
    if 'data' in result:
        print(f"Data keys: {list(result['data'].keys())}")
        if 'data' in result['data']:
            inner_data = result['data']['data']
            print(f"Inner data keys: {list(inner_data.keys())}")
            if 'vision_prompt' in inner_data:
                prompt = inner_data['vision_prompt']
                print(f"\nPrompt length: {len(prompt)}")
                print("Prompt preview:")
                print(prompt[:200])
else:
    print(f"Error: {resp.text}")
