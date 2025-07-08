import os
import requests
import json

api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

# Test with a comprehensive schema that includes all fields
schema = [
    {"column_name": "vendor_name", "data_type": "character varying"},
    {"column_name": "invoice_number", "data_type": "character varying"},
    {"column_name": "invoice_date", "data_type": "date"},
    {"column_name": "due_date", "data_type": "date"},
    {"column_name": "total_amount", "data_type": "numeric"},
    {"column_name": "tax_amount", "data_type": "numeric"},
    {"column_name": "line_items", "data_type": "jsonb"}
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
    
    if 'data' in result and 'data' in result['data']:
        inner_data = result['data']['data']
        
        # Get the vision response
        if 'vision_response' in inner_data:
            try:
                vision_parsed = json.loads(inner_data['vision_response'])
                print("\nVision Model Response Fields:")
                for key, value in vision_parsed.items():
                    print(f"  {key}: {value}")
            except:
                print("Could not parse vision response as JSON")
        
        # Get the extracted data
        if 'extracted_data' in inner_data:
            extracted = inner_data['extracted_data']
            billing = extracted.get('billingDetails', {})
            charges = extracted.get('chargesSummary', {})
            
            print("\nExtracted Fields:")
            print(f"  due_date: '{billing.get('dueDate', 'MISSING')}'")
            print(f"  total_amount: {charges.get('document_total', 'MISSING')}")
            print(f"  tax_amount: {charges.get('secondary_tax', 'MISSING')}")
else:
    print(f"Error: {resp.text}")