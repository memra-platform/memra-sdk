#!/usr/bin/env python3
"""
Test script to see what PDFProcessor actually returns
"""

import os
import base64
import requests
import json

def test_pdf_processor_response():
    """Test the PDFProcessor response structure"""
    
    # Set API key
    os.environ['MEMRA_API_KEY'] = 'test-secret-for-development'
    API_BASE = "https://api.memra.co"
    API_KEY = "test-secret-for-development"
    
    print("🧪 Testing PDFProcessor Response Structure")
    print("=" * 50)
    
    # Step 1: Upload a file
    print("\n1️⃣ Uploading file...")
    pdf_path = "data/invoices/10352260169.PDF"
    
    with open(pdf_path, 'rb') as f:
        file_content = f.read()
    
    file_b64 = base64.b64encode(file_content).decode('utf-8')
    
    upload_data = {
        "filename": os.path.basename(pdf_path),
        "content": file_b64,
        "content_type": "application/pdf"
    }
    
    response = requests.post(
        f"{API_BASE}/upload",
        json=upload_data,
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        return
    
    result = response.json()
    if not result.get("success"):
        print(f"❌ Upload failed: {result.get('error')}")
        return
    
    remote_path = result["data"]["remote_path"]
    print(f"✅ File uploaded: {remote_path}")
    
    # Step 2: Call PDFProcessor
    print("\n2️⃣ Calling PDFProcessor...")
    process_data = {
        "tool_name": "PDFProcessor",
        "hosted_by": "memra",
        "input_data": {
            "file": remote_path
        }
    }
    
    response = requests.post(
        f"{API_BASE}/tools/execute",
        json=process_data,
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📄 Full Response Structure:")
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            data = result.get("data", {})
            print(f"\n🔍 Data Keys: {list(data.keys())}")
            
            # Check for vision_response
            if "vision_response" in data:
                print(f"\n🎯 Vision Response Found!")
                vision_response = data["vision_response"]
                print(f"Vision Response (first 200 chars): {vision_response[:200]}...")
                
                # Try to parse as JSON
                try:
                    if vision_response.startswith("```json"):
                        vision_response = vision_response.replace("```json", "").replace("```", "").strip()
                    vision_data = json.loads(vision_response)
                    print(f"\n✅ Vision Response Parsed Successfully:")
                    print(json.dumps(vision_data, indent=2))
                except Exception as e:
                    print(f"❌ Failed to parse vision response: {e}")
            
            # Check for extracted_data
            if "extracted_data" in data:
                print(f"\n📊 Extracted Data Found:")
                extracted_data = data["extracted_data"]
                print(json.dumps(extracted_data, indent=2))
            else:
                print(f"\n❌ No extracted_data found")
        else:
            print(f"❌ API call failed: {result.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_pdf_processor_response() 