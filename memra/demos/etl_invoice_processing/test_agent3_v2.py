import os
import requests

api_url = "https://api.memra.co"
api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")

# Try with 'file' instead of 'file_path'
remote_path = "/uploads/6f4538c0-8fce-4488-be49-1a78afc58a4a.pdf"

print("Testing with 'file' parameter:")
resp = requests.post(
    f"{api_url}/tools/execute",
    json={
        "tool_name": "PDFProcessor",
        "hosted_by": "memra",
        "input_data": {"file": remote_path}
    },
    headers={"X-API-Key": api_key}
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    import json
    result = resp.json()
    print(f"Success: {result.get('success')}")
    if result.get('success') and 'data' in result:
        data = result['data']
        if 'data' in data:
            print("Found nested data structure")
            inner_data = data['data']
            if 'vision_response' in inner_data:
                print("✅ Found vision_response\!")
                print(inner_data['vision_response'][:200])
