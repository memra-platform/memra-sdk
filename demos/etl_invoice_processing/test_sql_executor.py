#!/usr/bin/env python3
"""
Test SQLExecutor tool execution directly
"""

import sys
import os
sys.path.insert(0, '/Users/tarpus/memra')

from memra.tool_registry import ToolRegistry
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_sql_executor():
    """Test SQLExecutor tool execution"""
    
    # Create tool registry
    registry = ToolRegistry()
    
    # Test configuration
    config = {
        "bridge_url": "http://localhost:8081",
        "bridge_secret": "test-secret-for-development"
    }
    
    # Test input data
    input_data = {
        "sql_query": "SELECT COUNT(*) as row_count FROM invoices"
    }
    
    print("🔧 Testing SQLExecutor tool execution...")
    print(f"Config: {config}")
    print(f"Input: {input_data}")
    
    # Execute the tool
    result = registry.execute_tool(
        tool_name="SQLExecutor",
        hosted_by="mcp",
        input_data=input_data,
        config=config
    )
    
    print(f"\n📊 Result: {result}")
    
    if result.get("success"):
        print("✅ SQLExecutor executed successfully!")
        if "_mock" in result.get("data", {}):
            print("⚠️  But returned mock data")
        else:
            print("🎉 Real data returned!")
    else:
        print(f"❌ SQLExecutor failed: {result.get('error')}")

if __name__ == "__main__":
    test_sql_executor() 