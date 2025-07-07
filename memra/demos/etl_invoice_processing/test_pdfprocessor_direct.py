#!/usr/bin/env python3
"""
Test PDFProcessor directly using the same mechanism as ETL workflow
"""

import os
import sys
import requests
import json

# Add the parent directory to the path to import memra modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from memra.execution import ExecutionEngine
from memra.models import Agent, ExecutionTrace

# Set environment variables
os.environ["MEMRA_API_URL"] = "https://api.memra.co"
os.environ["MEMRA_API_KEY"] = "test-secret-for-development"

def test_pdfprocessor_direct():
    """Test PDFProcessor directly"""
    print("🧪 Testing PDFProcessor Direct Call")
    print("=" * 50)
    
    # Create a simple agent that just calls PDFProcessor
    test_agent = Agent(
        role="Test Agent",
        job="Test PDFProcessor directly",
        llm=None,  # No LLM needed for direct tool call
        tools=[
            {"name": "PDFProcessor", "hosted_by": "memra"}
        ],
        input_keys=["file"],
        output_key="result"
    )
    
    # Create execution engine
    engine = ExecutionEngine()
    
    # Test with the same file path that the ETL workflow uses
    file_path = "/uploads/bd4b5a42-ff4b-4659-b050-e1f2d59f521a.PDF"  # From the upload test
    
    print(f"📄 Testing with file: {file_path}")
    
    # Prepare context and trace
    context = {
        "input": {"file": file_path},
        "department_context": {},
        "results": {}
    }
    trace = ExecutionTrace()

    # Execute the agent
    result = engine._execute_agent(test_agent, context, trace)
    
    print(f"\n📊 Result:")
    print(f"Success: {result.success}")
    print(f"Error: {result.error}")
    
    if result.success and result.data:
        print(f"\n📄 Data keys: {list(result.data.keys())}")
        
        if 'result' in result.data:
            tool_result = result.data['result']
            print(f"\n🔧 Tool Result:")
            print(f"Success: {tool_result.get('success')}")
            print(f"Error: {tool_result.get('error')}")
            
            if 'data' in tool_result:
                data = tool_result['data']
                print(f"Data keys: {list(data.keys())}")
                
                if 'vision_response' in data:
                    print(f"\n📝 Vision Response found!")
                    print(f"Length: {len(data['vision_response'])} characters")
                    try:
                        parsed = json.loads(data['vision_response'].replace('```json','').replace('```','').strip())
                        print("✅ Valid JSON response:")
                        print(json.dumps(parsed, indent=2))
                    except Exception as e:
                        print(f"❌ JSON parsing error: {e}")
                        print(f"Raw response: {data['vision_response'][:500]}...")
                
                if 'extracted_data' in data:
                    print(f"\n🎯 Extracted Data found!")
                    print(json.dumps(data['extracted_data'], indent=2))
            else:
                print("❌ No 'data' field in tool result")
        else:
            print("❌ No 'result' field in agent output")
    else:
        print(f"❌ Agent execution failed: {result.error}")

if __name__ == "__main__":
    test_pdfprocessor_direct() 