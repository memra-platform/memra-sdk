#!/usr/bin/env python3
"""
Test MCP integration with proper data
"""

import os
import sys
import logging

# Add the parent directory to the path so we can import memra
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memra.models import Agent, Department
from memra.execution import ExecutionEngine

# Set up environment
os.environ['MEMRA_API_KEY'] = 'memra-prod-2024-001'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🧪 Testing MCP Integration with Simple Data")
    print("=" * 60)
    
    # Create a simple agent that uses MCP tools
    test_agent = Agent(
        role="MCP Tester",
        job="Test MCP tools with simple data",
        tools=[
            {
                "name": "DataValidator", 
                "hosted_by": "mcp",
                "config": {
                    "bridge_url": "https://c210-2607-f598-ba9a-99-93d-4606-5e29-a28d.ngrok-free.app",
                    "bridge_secret": "test-secret-for-development"
                }
            },
            {
                "name": "PostgresInsert", 
                "hosted_by": "mcp",
                "config": {
                    "bridge_url": "https://c210-2607-f598-ba9a-99-93d-4606-5e29-a28d.ngrok-free.app",
                    "bridge_secret": "test-secret-for-development"
                }
            }
        ],
        input_keys=["test_data"],
        output_key="mcp_result"
    )
    
    # Create a simple department
    test_department = Department(
        name="MCP Test",
        mission="Test MCP integration",
        agents=[test_agent],
        workflow_order=["MCP Tester"]
    )
    
    # Create execution engine
    engine = ExecutionEngine()
    print(f"🔍 Debug: Tool registry type = {type(engine.tool_registry)}")
    
    # Test with simple, valid data
    input_data = {
        "test_data": {
            "invoice_number": "TEST-001",
            "vendor_name": "Test Vendor",
            "total_amount": 100.50,
            "invoice_date": "2024-01-15"
        },
        "connection": "postgresql://tarpus@localhost:5432/memra_invoice_db"
    }
    
    result = engine.execute_department(test_department, input_data)
    
    if result.success:
        print("✅ MCP integration test completed successfully!")
        print(f"Result: {result.data}")
    else:
        print(f"❌ MCP integration test failed: {result.error}")
        print(f"Errors: {result.trace.errors}")

if __name__ == "__main__":
    main() 