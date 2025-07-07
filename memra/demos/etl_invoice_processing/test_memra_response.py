#!/usr/bin/env python3
"""
Test script to see what the memra library receives from PDFProcessor
"""

import os
import sys
from pathlib import Path

# Set API key
os.environ['MEMRA_API_KEY'] = 'test-secret-for-development'
os.environ['MEMRA_API_URL'] = 'https://api.memra.co'

# Add the parent directory to the path so we can import memra
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memra import ExecutionEngine, Agent, LLM
import base64
import requests

def test_memra_pdf_processor():
    """Test what the memra library receives from PDFProcessor"""
    
    print("🧪 Testing Memra Library PDFProcessor Response")
    print("=" * 50)
    
    # Create a simple agent to test PDFProcessor
    test_llm = LLM(
        model="llama-3.2-11b-vision-preview",
        temperature=0.1,
        max_tokens=2000
    )
    
    test_agent = Agent(
        role="Test Parser",
        job="Test PDFProcessor response",
        llm=test_llm,
        tools=[
            {"name": "PDFProcessor", "hosted_by": "memra"}
        ],
        input_keys=["file"],
        output_key="test_result"
    )
    
    # First upload a file
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
        "https://api.memra.co/upload",
        json=upload_data,
        headers={
            "X-API-Key": "test-secret-for-development",
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
    
    # Now test with memra library
    print("\n2️⃣ Testing with memra library...")
    engine = ExecutionEngine()
    
    input_data = {
        "file": remote_path
    }
    
    result = engine.execute_agent(test_agent, input_data)
    
    print(f"\n📄 Memra Library Result:")
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
    
    if result.get('success'):
        test_result = result.get('result', {})
        print(f"\n🔍 Test Result Keys: {list(test_result.keys())}")
        
        # Check if there are tool results
        if hasattr(result, 'trace') and result.trace and hasattr(result.trace, 'tool_results'):
            tool_results = result.trace.tool_results
            print(f"\n🔧 Tool Results:")
            for tool_name, tool_result in tool_results.items():
                print(f"\n📊 Tool: {tool_name}")
                print(f"Success: {tool_result.get('success')}")
                print(f"Data Keys: {list(tool_result.get('data', {}).keys())}")
                
                data = tool_result.get('data', {})
                if 'data' in data:
                    inner_data = data['data']
                    print(f"Inner Data Keys: {list(inner_data.keys())}")
                    
                    if 'vision_response' in inner_data:
                        print(f"✅ Vision Response Found!")
                        vision_response = inner_data['vision_response']
                        print(f"Vision Response (first 200 chars): {vision_response[:200]}...")
                    
                    if 'extracted_data' in inner_data:
                        print(f"✅ Extracted Data Found!")
                        extracted_data = inner_data['extracted_data']
                        print(f"Extracted Data: {extracted_data}")

if __name__ == "__main__":
    test_memra_pdf_processor() 