#!/usr/bin/env python3
"""
Test script to verify file upload functionality with remote API
"""

import os
import base64
import requests
import json

def test_remote_upload():
    """Test the complete upload and processing workflow with remote API"""
    
    # Remote API URL
    API_BASE = "https://api.memra.co"
    API_KEY = "test-secret-for-development"
    
    print("🧪 Testing Remote API File Upload Functionality")
    print("=" * 50)
    
    # Step 1: Check server health
    print("\n1️⃣ Checking server health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Step 2: Discover available tools
    print("\n2️⃣ Discovering available tools...")
    try:
        response = requests.get(f"{API_BASE}/tools/discover", headers={"X-API-Key": API_KEY})
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Tool discovery failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Tool discovery error: {e}")
        return
    
    # Step 3: Test with a real PDF file
    print("\n3️⃣ Testing with real PDF file...")
    pdf_path = "data/invoices/10352260169.PDF"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"✅ Found PDF file: {pdf_path}")
    
    # Step 4: Upload the file
    print("\n4️⃣ Uploading file to remote API...")
    try:
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
        
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                remote_path = result["data"]["remote_path"]
                print(f"✅ File uploaded successfully")
                print(f"   Remote path: {remote_path}")
                print(f"   File ID: {result['data']['file_id']}")
                
                # Step 5: Process the uploaded file
                print("\n5️⃣ Processing uploaded file...")
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
                
                print(f"Processing response status: {response.status_code}")
                print(f"Processing response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success") and result.get("data", {}).get("success"):
                        extracted_data = result["data"]["data"].get("extracted_data", {})
                        print("✅ File processed successfully")
                        print("📄 Extracted data:")
                        print(f"   Vendor: {extracted_data.get('headerSection', {}).get('vendorName', 'N/A')}")
                        print(f"   Invoice: {extracted_data.get('billingDetails', {}).get('invoiceNumber', 'N/A')}")
                        print(f"   Amount: ${extracted_data.get('chargesSummary', {}).get('document_total', 'N/A')}")
                    else:
                        print(f"❌ Processing failed: {result.get('data', {}).get('error', 'Unknown error')}")
                else:
                    print(f"❌ Processing request failed: {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print(f"❌ Upload failed: {result.get('error')}")
        else:
            print(f"❌ Upload request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload/Processing error: {e}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_remote_upload() 