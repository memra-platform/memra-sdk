import os
import requests
import json

api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

# Test with a more detailed schema format
schema = {
    "fields": [
        {"name": "invoice_number", "type": "string", "required": True},
        {"name": "vendor_name", "type": "string", "required": True},
        {"name": "invoice_date", "type": "date", "required": True},
        {"name": "total_amount", "type": "numeric", "required": True}
    ]
}

print("Testing PDFProcessor with schema:")
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

if resp.status_code == 200:
    result = resp.json()
    if result.get('success') and 'data' in result and 'data' in result['data']:
        prompt = result['data']['data'].get('vision_prompt', '')
        print("\nVision prompt generated:")
        print(prompt[:500])
