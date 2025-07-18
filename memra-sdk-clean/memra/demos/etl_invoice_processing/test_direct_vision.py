import os
import requests
import json
import base64

# Upload a test PDF and process it
api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

# First, upload a PDF file
pdf_path = "data/invoices/10352259401.PDF"  # Superior Propane invoice

# Read and encode the PDF
with open(pdf_path, 'rb') as f:
    pdf_content = f.read()

pdf_b64 = base64.b64encode(pdf_content).decode('utf-8')

# Upload the file
print("📤 Uploading PDF file...")
upload_resp = requests.post(
    f"{api_url}/upload",
    json={
        "filename": os.path.basename(pdf_path),
        "content": pdf_b64,
        "content_type": "application/pdf"
    },
    headers={"X-API-Key": api_key}
)

if upload_resp.status_code != 200:
    print(f"Upload failed: {upload_resp.text}")
    exit(1)

upload_result = upload_resp.json()
remote_path = upload_result["data"]["remote_path"]
print(f"✅ Uploaded to: {remote_path}")

# Now process with PDFProcessor
print("\n🔍 Processing with PDFProcessor...")
schema = [
    {"column_name": "vendor_name", "data_type": "character varying"},
    {"column_name": "invoice_number", "data_type": "character varying"},
    {"column_name": "invoice_date", "data_type": "date"},
    {"column_name": "due_date", "data_type": "date"},
    {"column_name": "total_amount", "data_type": "numeric"},
    {"column_name": "tax_amount", "data_type": "numeric"},
    {"column_name": "line_items", "data_type": "jsonb"}
]

process_resp = requests.post(
    f"{api_url}/tools/execute",
    json={
        "tool_name": "PDFProcessor",
        "hosted_by": "memra",
        "input_data": {
            "file": remote_path,
            "schema": schema
        }
    },
    headers={"X-API-Key": api_key}
)

if process_resp.status_code == 200:
    result = process_resp.json()
    
    if result.get('success') and 'data' in result and 'data' in result['data']:
        inner_data = result['data']['data']
        
        print("\n=== VISION MODEL RAW RESPONSE ===")
        if 'vision_response' in inner_data:
            vision_resp = inner_data['vision_response']
            print(f"Raw response: {vision_resp[:200]}...")
            try:
                vision_data = json.loads(vision_resp)
                print("\nVision model extracted:")
                for key, value in vision_data.items():
                    print(f"  {key}: {value}")
            except Exception as e:
                print(f"Could not parse vision response: {e}")
                
        print("\n=== VISION PROMPT USED ===")
        if 'vision_prompt' in inner_data:
            print(inner_data['vision_prompt'][:500] + "...")
        
        print("\n=== TRANSFORMED DATA (MCP Format) ===")
        if 'extracted_data' in inner_data:
            extracted = inner_data['extracted_data']
            header = extracted.get('headerSection', {})
            billing = extracted.get('billingDetails', {})
            charges = extracted.get('chargesSummary', {})
            
            print(f"Vendor: {header.get('vendorName', 'MISSING')}")
            print(f"Invoice Number: {billing.get('invoiceNumber', 'MISSING')}")
            print(f"Invoice Date: {billing.get('invoiceDate', 'MISSING')}")
            print(f"Due Date: {billing.get('dueDate', 'MISSING')}")
            print(f"Total Amount: ${charges.get('document_total', 'MISSING')}")
            print(f"Tax Amount: ${charges.get('secondary_tax', 'MISSING')}")
            
            print("\n=== ANALYSIS ===")
            missing_fields = []
            if not billing.get('dueDate'):
                missing_fields.append('due_date')
            if not charges.get('document_total'):
                missing_fields.append('total_amount')
            if not charges.get('secondary_tax'):
                missing_fields.append('tax_amount')
                
            if missing_fields:
                print(f"❌ Missing fields: {', '.join(missing_fields)}")
            else:
                print("✅ All fields extracted successfully!")
else:
    print(f"Processing failed: {process_resp.text}")