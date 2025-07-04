#!/usr/bin/env python3
"""
Test script to verify file upload functionality
"""

import os
import base64
import requests
import json

def test_upload_functionality():
    """Test the complete upload and processing workflow"""
    
    # Test server URL (change this to api.memra.co when implementing on remote)
    API_BASE = "http://localhost:8000"
    
    print("🧪 Testing File Upload Functionality")
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
        print("💡 Make sure to start the test server: python3 test_upload_server.py")
        return
    
    # Step 2: Discover available tools
    print("\n2️⃣ Discovering available tools...")
    try:
        response = requests.get(f"{API_BASE}/tools/discover")
        if response.status_code == 200:
            tools = response.json().get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Tool discovery failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Tool discovery error: {e}")
        return
    
    # Step 3: Create a test PDF file
    print("\n3️⃣ Creating test PDF file...")
    test_pdf_path = "test_invoice.pdf"
    
    # Create a simple test PDF (this is just for testing - in real usage you'd use actual PDFs)
    try:
        # For testing, we'll create a simple text file and pretend it's a PDF
        with open(test_pdf_path, 'w') as f:
            f.write("Test Invoice\nVendor: Test Corp\nAmount: $1234.56\n")
        print(f"✅ Created test file: {test_pdf_path}")
    except Exception as e:
        print(f"❌ Failed to create test file: {e}")
        return
    
    # Step 4: Upload the file
    print("\n4️⃣ Uploading file to server...")
    try:
        with open(test_pdf_path, 'rb') as f:
            file_content = f.read()
        
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        upload_data = {
            "filename": os.path.basename(test_pdf_path),
            "content": file_b64,
            "content_type": "application/pdf"
        }
        
        response = requests.post(
            f"{API_BASE}/upload",
            json=upload_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                remote_path = result["data"]["remote_path"]
                print(f"✅ File uploaded successfully")
                print(f"   Remote path: {remote_path}")
                print(f"   File ID: {result['data']['file_id']}")
            else:
                print(f"❌ Upload failed: {result.get('error')}")
                return
        else:
            print(f"❌ Upload request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Step 5: Process the uploaded file
    print("\n5️⃣ Processing uploaded file...")
    try:
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
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                extracted_data = result["data"]["extracted_data"]
                print("✅ File processed successfully")
                print("📄 Extracted data:")
                print(f"   Vendor: {extracted_data['headerSection']['vendorName']}")
                print(f"   Invoice: {extracted_data['billingDetails']['invoiceNumber']}")
                print(f"   Amount: ${extracted_data['chargesSummary']['document_total']}")
            else:
                print(f"❌ Processing failed: {result.get('error')}")
                return
        else:
            print(f"❌ Processing request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return
    
    # Step 6: Cleanup
    print("\n6️⃣ Cleaning up...")
    try:
        os.remove(test_pdf_path)
        print("✅ Test file removed")
    except:
        pass
    
    print("\n🎉 All tests passed! File upload functionality is working correctly.")
    print("\n📋 Next Steps:")
    print("1. Implement the upload endpoint on the remote API (api.memra.co)")
    print("2. Update the demo to use the real remote API")
    print("3. Test with actual PDF files")

if __name__ == "__main__":
    test_upload_functionality() 