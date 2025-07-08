#!/usr/bin/env python3
"""
Debug script to trace data flow between agents
"""

import os
import sys
from memra import Agent, Department, LLM, check_api_health, get_api_status
from memra.execution import ExecutionEngine
import requests
import base64

# Set API configuration
os.environ["MEMRA_API_URL"] = "https://api.memra.co"

def debug_data_flow():
    """Debug the data flow between agents"""
    
    print("🔍 DEBUGGING DATA FLOW BETWEEN AGENTS")
    print("=" * 60)
    
    # Create a simple test workflow
    test_llm = LLM(model="llama-3.2-11b-vision-preview", temperature=0.1)
    
    # Test agent that just returns data
    test_agent = Agent(
        role="Test Data Source",
        job="Return test data",
        llm=test_llm,
        tools=[{"name": "MockDataTool", "hosted_by": "memra"}],
        output_key="test_data"
    )
    
    # Test agent that receives data
    receiver_agent = Agent(
        role="Test Data Receiver", 
        job="Receive and display data",
        llm=test_llm,
        tools=[{"name": "DataValidator", "hosted_by": "mcp"}],
        input_keys=["test_data"],
        output_key="validation_result"
    )
    
    # Create test department
    test_department = Department(
        name="Data Flow Test",
        mission="Test data flow between agents",
        agents=[test_agent, receiver_agent],
        workflow_order=["Test Data Source", "Test Data Receiver"],
        context={
            "mcp_bridge_url": "http://localhost:8081",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )
    
    # Mock input data
    input_data = {
        "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db"
    }
    
    # Execute with debug logging
    engine = ExecutionEngine()
    
    print("\n🚀 Starting test workflow...")
    result = engine.execute_department(test_department, input_data)
    
    print(f"\n📊 Final Result: {result.success}")
    if result.data:
        print(f"📄 Data keys: {list(result.data.keys())}")
        for key, value in result.data.items():
            print(f"   {key}: {type(value)} = {value}")

if __name__ == "__main__":
    debug_data_flow() 