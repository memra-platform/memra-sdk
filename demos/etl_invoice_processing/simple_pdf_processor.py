#!/usr/bin/env python3
"""
Simple PDF Processor - Direct API call without complex post-processing
"""

import os
import sys
import json
import requests
import base64

# Add the parent directory to the path to import memra modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from memra.tool_registry_client import ToolRegistryClient

# Set environment variables
os.environ["MEMRA_API_URL"] = "https://api.memra.co"
os.environ["MEMRA_API_KEY"] = "test-secret-for-development"

def upload_file_to_api(file_path: str, api_url: str = "https://api.memra.co") -> str:
    """Upload a file to the remote API"""
    try:
        print(f"📤 Uploading {os.path.basename(file_path)} to remote API")
        
        # Read the file and encode as base64
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        # Prepare upload data
        upload_data = {
            "filename": os.path.basename(file_path),
            "content": file_b64,
            "content_type": "application/pdf"
        }
        
        # Upload to remote API
        api_key = os.getenv("MEMRA_API_KEY")
        response = requests.post(
            f"{api_url}/upload",
            json=upload_data,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                remote_path = result["data"]["remote_path"]
                print(f"✅ File uploaded successfully")
                print(f"   Remote path: {remote_path}")
                return remote_path
            else:
                print(f"❌ Upload failed: {result.get('error')}")
                return file_path
        else:
            print(f"❌ Upload request failed: {response.status_code}")
            return file_path
                
    except Exception as e:
        print(f"⚠️  Upload error: {e}")
        return file_path

def process_pdf_simple(file_path: str) -> dict:
    """Simple PDF processing - direct API call, no post-processing"""
    print(f"\n🔍 Processing PDF: {file_path}")
    print("=" * 50)
    
    # Step 1: Upload file to API
    remote_path = upload_file_to_api(file_path)
    
    # Step 2: Call PDFProcessor directly
    client = ToolRegistryClient()
    
    print(f"\n📄 Calling PDFProcessor with remote path: {remote_path}")
    
    result = client.execute_tool(
        tool_name="PDFProcessor",
        hosted_by="memra",
        input_data={"file": remote_path},
        config=None
    )
    
    print(f"\n📊 API Response:")
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
    
    # Debug: Print the full response structure
    print(f"\n🔍 DEBUG: Full API Response Structure:")
    print(f"Result keys: {list(result.keys())}")
    print(f"Result: {json.dumps(result, indent=2, default=str)}")
    
    if result.get('success') and 'data' in result:
        data = result['data']
        print(f"\n🎯 Raw JSON Response from Vision Model:")
        
        if 'vision_response' in data:
            vision_response = data['vision_response']
            print(f"📝 Vision Response (raw):")
            print(vision_response)
            
            # Parse the JSON response
            try:
                # Clean the response - remove markdown code blocks if present
                cleaned_response = vision_response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]  # Remove ```
                cleaned_response = cleaned_response.strip()
                
                parsed_json = json.loads(cleaned_response)
                print(f"\n✅ Parsed JSON Response:")
                print(json.dumps(parsed_json, indent=2))
                
                return {
                    "success": True,
                    "raw_vision_response": vision_response,
                    "parsed_json": parsed_json,
                    "extracted_data": data.get('extracted_data', {})
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                return {
                    "success": False,
                    "error": f"JSON parsing failed: {e}",
                    "raw_response": vision_response
                }
        else:
            print("❌ No vision_response in data")
            return {
                "success": False,
                "error": "No vision_response in API response",
                "data": data
            }
    else:
        print(f"❌ API call failed: {result.get('error')}")
        return {
            "success": False,
            "error": result.get('error', 'Unknown error'),
            "result": result
        }

def main():
    """Main function to process a PDF file"""
    if len(sys.argv) != 2:
        print("Usage: python3 simple_pdf_processor.py <pdf_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Process the PDF
    result = process_pdf_simple(file_path)
    
    if result.get('success'):
        print(f"\n🎉 SUCCESS! PDF processed successfully")
        print(f"📄 Invoice Number: {result['parsed_json'].get('InvoiceNumber', 'N/A')}")
        print(f"💰 Total Amount: ${result['parsed_json'].get('InvoiceTotal', 'N/A')}")
        print(f"📅 Date: {result['parsed_json'].get('InvoiceDate', 'N/A')}")
        
        # Save the result to a JSON file for later use
        output_file = f"{os.path.splitext(os.path.basename(file_path))[0]}_result.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Result saved to: {output_file}")
        
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main() 