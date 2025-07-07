import os
import requests
import json

api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

# Test with the schema format the client sends
schema = [
    {"column_name": "invoice_number", "data_type": "character varying", "is_nullable": "NO"},
    {"column_name": "vendor_name", "data_type": "character varying", "is_nullable": "NO"},
    {"column_name": "invoice_date", "data_type": "date", "is_nullable": "NO"},
    {"column_name": "total_amount", "data_type": "numeric", "is_nullable": "NO"}
]

print("Testing updated server with client schema format:")
print(json.dumps(schema[:2], indent=2))  # Show first 2 fields

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
        vision_prompt = data.get('vision_prompt', '')
        print(f"\nVision prompt generated (first 500 chars):")
        print(vision_prompt[:500])
        
        # Check if vendor_name is in the prompt
        if 'vendor_name' in vision_prompt:
            print("\n✅ SUCCESS: vendor_name is now in the vision prompt\!")
        else:
            print("\n❌ FAIL: vendor_name is NOT in the vision prompt")
            
        # Check vision response
        vision_resp = data.get('vision_response', '')
        if vision_resp:
            print(f"\nVision response includes vendor info: {'vendor' in vision_resp.lower()}")
