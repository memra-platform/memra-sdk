import os
import requests
import base64

# Test the PDFProcessor API directly
api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

# Upload a test file
with open("data/invoices/10352260169.PDF", "rb") as f:
    content = base64.b64encode(f.read()).decode('utf-8')

upload_resp = requests.post(
    f"{api_url}/upload",
    json={
        "filename": "test.pdf",
        "content": content,
        "content_type": "application/pdf"
    },
    headers={"X-API-Key": api_key}
)

if upload_resp.status_code == 200:
    remote_path = upload_resp.json()["data"]["remote_path"]
    print(f"✅ Uploaded to: {remote_path}")
    
    # Try different parameter formats
    print("\n1. Testing with input_data format:")
    resp = requests.post(
        f"{api_url}/tools/execute",
        json={
            "tool_name": "PDFProcessor",
            "hosted_by": "memra",
            "input_data": {"file_path": remote_path}
        },
        headers={"X-API-Key": api_key}
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    
    print("\n2. Testing with parameters format:")
    resp = requests.post(
        f"{api_url}/tools/execute",
        json={
            "tool_name": "PDFProcessor",
            "hosted_by": "memra",
            "parameters": {"file_path": remote_path}
        },
        headers={"X-API-Key": api_key}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        import json
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    else:
        print(f"Response: {resp.text}")
