import os
import requests
import json

api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

# Test the exact format we're sending
schema = {
    "columns": [
        {"name": "invoice_number", "type": "character varying"},
        {"name": "vendor_name", "type": "character varying"},
        {"name": "invoice_date", "type": "date"},
        {"name": "total_amount", "type": "numeric"}
    ]
}

print("Schema being sent:")
print(json.dumps(schema, indent=2))

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

print(f"\nResponse status: {resp.status_code}")
if resp.status_code == 200:
    result = resp.json()
    if result.get('success') and 'data' in result and 'data' in result['data']:
        data = result['data']['data']
        print(f"\nVision prompt length: {len(data.get('vision_prompt', ''))}")
        print("Vision prompt preview:")
        print(data.get('vision_prompt', '')[:500])
        
        # Check if vendor was mentioned in response
        vision_resp = data.get('vision_response', '')
        print(f"\nVision response includes 'vendor': {'vendor' in vision_resp.lower()}")
