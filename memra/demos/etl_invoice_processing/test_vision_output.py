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
    print(f"\nSuccess: {result.get('success')}")
    
    if 'data' in result and 'data' in result['data']:
        inner_data = result['data']['data']
        
        # Print the vision response
        if 'vision_response' in inner_data:
            print("\n=== VISION MODEL RAW RESPONSE ===")
            vision_resp = inner_data['vision_response']
            try:
                # Try to parse and pretty print if it's JSON
                parsed = json.loads(vision_resp)
                print(json.dumps(parsed, indent=2))
            except:
                print(vision_resp)
            print("=" * 40)
        
        # Print the extracted data after transformation
        if 'extracted_data' in inner_data:
            print("\n=== TRANSFORMED DATA (MCP Format) ===")
            extracted = inner_data['extracted_data']
            print(json.dumps(extracted, indent=2))
            
            # Check specific fields
            print("\n=== FIELD ANALYSIS ===")
            billing = extracted.get('billingDetails', {})
            charges = extracted.get('chargesSummary', {})
            
            print(f"due_date: '{billing.get('dueDate', 'MISSING')}'")
            print(f"total_amount: {charges.get('document_total', 'MISSING')}")
            print(f"tax_amount: {charges.get('secondary_tax', 'MISSING')}")
            print("=" * 40)
            
            # Save to file for easier viewing
            with open("vision_output.json", "w") as f:
                json.dump({
                    "vision_response": inner_data.get('vision_response', ''),
                    "extracted_data": extracted
                }, f, indent=2)
else:
    print(f"Error: {resp.text}")