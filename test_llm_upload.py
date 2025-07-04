#!/usr/bin/env python3
"""
Standalone test script to upload a PDF and test LLM processing on the server.
"""

import requests
import json
import os
import sys
import base64
from pathlib import Path

# Configuration
API_BASE_URL = "https://memra-api.fly.dev"
TEST_PDF_PATH = "demos/etl_invoice_processing/data/invoices/10352260169.PDF"
API_KEY = "memra-prod-2024-001"

def upload_file(file_path):
    """Upload a file to the server."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    print(f"Uploading {file_path} to {API_BASE_URL}/upload")
    
    # Read file and encode as base64
    with open(file_path, 'rb') as f:
        file_content = f.read()
        file_b64 = base64.b64encode(file_content).decode('utf-8')
    
    # Prepare upload data in the format the server expects
    upload_data = {
        "filename": os.path.basename(file_path),
        "content": file_b64,
        "content_type": "application/pdf"
    }
    
    headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
    
    response = requests.post(f"{API_BASE_URL}/upload", json=upload_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Upload successful: {result}")
        return result.get('data', {}).get('file_id')
    else:
        print(f"Upload failed: {response.status_code} - {response.text}")
        return None

def test_llm_processing(file_id):
    """Test LLM processing directly on the server."""
    print(f"\nTesting LLM processing for file_id: {file_id}")
    
    # Test the PDFProcessor tool using the tools/execute endpoint
    payload = {
        "tool_name": "PDFProcessor",
        "hosted_by": "memra",
        "input_data": {
            "file": f"/uploads/{file_id}.PDF"
        }
    }
    
    headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
    
    response = requests.post(f"{API_BASE_URL}/tools/execute", json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"LLM Processing Result:")
        print(json.dumps(result, indent=2))
        return result
    else:
        print(f"LLM Processing failed: {response.status_code} - {response.text}")
        return None

def test_file_reading(file_id):
    """Test file reading tool."""
    print(f"\nTesting file reading for file_id: {file_id}")
    
    payload = {
        "tool_name": "FileReader",
        "hosted_by": "memra",
        "input_data": {
            "file": f"/uploads/{file_id}.PDF"
        }
    }
    
    headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
    
    response = requests.post(f"{API_BASE_URL}/tools/execute", json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"File Reading Result:")
        print(json.dumps(result, indent=2))
        return result
    else:
        print(f"File Reading failed: {response.status_code} - {response.text}")
        return None

def main():
    print("=== Standalone LLM Upload Test ===")
    
    # Check if test PDF exists
    if not os.path.exists(TEST_PDF_PATH):
        print(f"Error: Test PDF not found at {TEST_PDF_PATH}")
        print("Please ensure you have a sample invoice PDF in the demos directory.")
        return
    
    # Step 1: Upload the file
    file_id = upload_file(TEST_PDF_PATH)
    if not file_id:
        print("Failed to upload file. Exiting.")
        return
    
    # Step 2: Test LLM processing
    llm_result = test_llm_processing(file_id)
    
    # Step 3: Test file reading
    file_result = test_file_reading(file_id)
    
    print("\n=== Test Summary ===")
    print(f"File ID: {file_id}")
    print(f"LLM Processing: {'SUCCESS' if llm_result else 'FAILED'}")
    print(f"File Reading: {'SUCCESS' if file_result else 'FAILED'}")

if __name__ == "__main__":
    main() 