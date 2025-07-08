#!/usr/bin/env python3
"""
Test script to directly test PDFProcessor and see the actual data structure
"""

import os
import sys
import json
import requests
from pathlib import Path
import base64

# Add the memra package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'memra'))

# API configuration
API_URL = "https://api.memra.co"
API_KEY = "test-secret-for-development"

def test_pdf_processor():
    """Test the PDFProcessor tool directly"""
    
    # Check if PDF file exists
    if not os.path.exists(PDF_FILE):
        print(f"❌ PDF file not found: {PDF_FILE}")
        return
    
    print(f"📄 Testing PDFProcessor with: {PDF_FILE}")
    print(f"🔗 API URL: {API_URL}")
    
    # First, discover available tools
    print("\n🔍 Discovering tools...")
    response = requests.get(f"{API_URL}/tools/discover", headers={"X-API-Key": API_KEY})
    
    if response.status_code != 200:
        print(f"❌ Tool discovery failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    tools = response.json().get("tools", [])
    pdf_tool = None
    
    for tool in tools:
        if tool.get("name") == "PDFProcessor":
            pdf_tool = tool
            break
    
    if not pdf_tool:
        print("❌ PDFProcessor tool not found")
        return
    
    print(f"✅ Found PDFProcessor: {pdf_tool}")
    
    # Read the PDF file and encode as base64
    print("\n📤 Reading PDF file...")
    with open(PDF_FILE, 'rb') as f:
        pdf_content = f.read()
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    
    print(f"📊 PDF file size: {len(pdf_content)} bytes")
    print(f"📊 Base64 encoded size: {len(pdf_base64)} characters")
    
    # Test the PDFProcessor with file content directly
    print("\n📤 Testing PDFProcessor with file content...")
    
    payload = {
        "tool_name": "PDFProcessor",
        "hosted_by": "memra",
        "input_data": {
            "file_content": pdf_base64,
            "filename": os.path.basename(PDF_FILE)
        }
    }
    
    response = requests.post(
        f"{API_URL}/tools/execute",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=120  # Longer timeout for PDF processing
    )
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📋 Response Headers: {dict(response.headers)}")
    
    try:
        result = response.json()
        print(f"📄 Response JSON: {json.dumps(result, indent=2)}")
        
        # Check for specific fields
        if 'extracted_text' in result:
            print(f"✅ Extracted text length: {len(result['extracted_text'])}")
        else:
            print("❌ No 'extracted_text' in response")
            
        if 'extracted_data' in result:
            print(f"✅ Extracted data: {result['extracted_data']}")
        else:
            print("❌ No 'extracted_data' in response")
            
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            
        # Check for success field
        if 'success' in result:
            print(f"✅ Success: {result['success']}")
            
    except json.JSONDecodeError:
        print(f"❌ Response is not JSON: {response.text}")

def test_upload_endpoint():
    """Test the /upload endpoint with a real PDF file"""
    if not os.path.exists(PDF_FILE):
        print(f"❌ PDF file not found: {PDF_FILE}")
        return
    print(f"\n📤 Testing /upload endpoint with: {PDF_FILE}")
    with open(PDF_FILE, 'rb') as f:
        pdf_content = f.read()
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    payload = {
        "filename": os.path.basename(PDF_FILE),
        "content": pdf_base64,
        "content_type": "application/pdf"
    }
    response = requests.post(
        f"{API_URL}/upload",
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json=payload
    )
    print(f"📊 Response Status: {response.status_code}")
    print(f"📋 Response Headers: {dict(response.headers)}")
    try:
        print(f"📄 Response JSON: {json.dumps(response.json(), indent=2)}")
    except Exception:
        print(f"❌ Response is not JSON: {response.text}")

def test_upload_and_process(pdf_file):
    """Upload a PDF and process it with PDFProcessor using the remote API."""
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        return
    print(f"\n📤 Uploading: {pdf_file}")
    with open(pdf_file, 'rb') as f:
        pdf_content = f.read()
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
    payload = {
        "filename": os.path.basename(pdf_file),
        "content": pdf_base64,
        "content_type": "application/pdf"
    }
    response = requests.post(
        f"{API_URL}/upload",
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json=payload
    )
    print(f"📊 Upload Response Status: {response.status_code}")
    try:
        upload_result = response.json()
        print(f"📄 Upload Response JSON: {json.dumps(upload_result, indent=2)}")
    except Exception:
        print(f"❌ Upload response is not JSON: {response.text}")
        return
    if not upload_result.get("success") or not upload_result.get("data", {}).get("remote_path"):
        print("❌ Upload failed or no remote_path returned.")
        return
    remote_path = upload_result["data"]["remote_path"]
    print(f"\n🚀 Calling PDFProcessor with file: {remote_path}")
    payload = {
        "tool_name": "PDFProcessor",
        "hosted_by": "memra",
        "input_data": {
            "file": remote_path
        }
    }
    response = requests.post(
        f"{API_URL}/tools/execute",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=120
    )
    print(f"📊 PDFProcessor Response Status: {response.status_code}")
    try:
        result = response.json()
        print(f"📄 PDFProcessor Response JSON: {json.dumps(result, indent=2)}")
        if 'extracted_text' in result:
            print(f"✅ Extracted text length: {len(result['extracted_text'])}")
        else:
            print("❌ No 'extracted_text' in response")
        if 'extracted_data' in result:
            print(f"✅ Extracted data: {result['extracted_data']}")
        else:
            print("❌ No 'extracted_data' in response")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        if 'success' in result:
            print(f"✅ Success: {result['success']}")
    except Exception:
        print(f"❌ PDFProcessor response is not JSON: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_pdf_processor.py <PDF_FILE_PATH>")
        sys.exit(1)
    pdf_file = sys.argv[1]
    test_upload_and_process(pdf_file) 