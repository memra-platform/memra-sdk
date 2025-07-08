#!/usr/bin/env python3
"""
Test API client directly to see what PDFProcessor returns
"""

import os
import sys
import json

# Add the parent directory to the path to import memra modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from memra.tool_registry_client import ToolRegistryClient

# Set environment variables
os.environ["MEMRA_API_URL"] = "https://api.memra.co"
os.environ["MEMRA_API_KEY"] = "test-secret-for-development"

def test_api_client_direct():
    """Test API client directly"""
    print("🧪 Testing API Client Direct Call")
    print("=" * 50)
    
    # Create API client
    client = ToolRegistryClient()
    
    # Test with the same file path that the ETL workflow uses
    file_path = "/uploads/22526d2e-dfcf-45eb-9e1a-47f093cd05ab.PDF"  # From the latest ETL upload
    
    print(f"📄 Testing with file: {file_path}")
    
    # Execute the PDFProcessor tool
    result = client.execute_tool(
        tool_name="PDFProcessor",
        hosted_by="memra",
        input_data={"file": file_path},
        config=None
    )
    
    print(f"\n📊 Raw API Client Result:")
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
    
    if result.get('success'):
        print(f"\n📄 Data keys: {list(result.keys())}")
        
        if 'data' in result:
            data = result['data']
            print(f"\n🔧 Data field:")
            print(f"Type: {type(data)}")
            print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            
            if isinstance(data, dict):
                print(f"\n📄 Data content:")
                print(json.dumps(data, indent=2, default=str))
                
                # Check for nested data
                if 'data' in data:
                    nested_data = data['data']
                    print(f"\n🔧 Nested data:")
                    print(f"Type: {type(nested_data)}")
                    print(f"Keys: {list(nested_data.keys()) if isinstance(nested_data, dict) else 'not a dict'}")
                    
                    if isinstance(nested_data, dict):
                        print(f"\n📄 Nested data content:")
                        print(json.dumps(nested_data, indent=2, default=str))
                        
                        # Check for vision_response and extracted_data
                        if 'vision_response' in nested_data:
                            print(f"\n📝 Vision Response found!")
                            print(f"Length: {len(nested_data['vision_response'])} characters")
                            try:
                                parsed = json.loads(nested_data['vision_response'].replace('```json','').replace('```','').strip())
                                print("✅ Valid JSON response:")
                                print(json.dumps(parsed, indent=2))
                            except Exception as e:
                                print(f"❌ JSON parsing error: {e}")
                                print(f"Raw response: {nested_data['vision_response'][:500]}...")
                        
                        if 'extracted_data' in nested_data:
                            print(f"\n🎯 Extracted Data found!")
                            print(json.dumps(nested_data['extracted_data'], indent=2))
        else:
            print("❌ No 'data' field in result")
    else:
        print(f"❌ API call failed: {result.get('error')}")

if __name__ == "__main__":
    test_api_client_direct() 