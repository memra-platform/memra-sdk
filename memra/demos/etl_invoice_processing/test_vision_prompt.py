# Test what happens when we pass schema to PDFProcessor
import os
import requests
import json

api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

# Schema that matches database fields
schema = [
    {"column_name": "invoice_number", "data_type": "character varying", "is_nullable": "NO"},
    {"column_name": "vendor_name", "data_type": "character varying", "is_nullable": "NO"},
    {"column_name": "invoice_date", "data_type": "date", "is_nullable": "NO"},
    {"column_name": "total_amount", "data_type": "numeric", "is_nullable": "NO"}
]

print("Testing with database schema format:")
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
        vision_prompt = result['data']['data'].get('vision_prompt', '')
        print("\nVision prompt with schema:")
        print(vision_prompt)
        
        # Check if vendor was extracted
        vision_resp = result['data']['data'].get('vision_response', '')
        if 'vendor' in vision_resp.lower():
            print("\n✅ Vision model extracted vendor info\!")
        else:
            print("\n❌ Vision model did not extract vendor info")
