#!/usr/bin/env python3
"""
Test SQLExecutor tool execution with extra fields (like agent_input)
"""

import sys
import os
sys.path.insert(0, '/Users/tarpus/memra')

from memra.tool_registry import ToolRegistry
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_sql_executor_with_extra_fields():
    """Test SQLExecutor tool execution with extra fields like agent_input"""
    
    # Create tool registry
    registry = ToolRegistry()
    
    # Test configuration
    config = {
        "bridge_url": "http://localhost:8081",
        "bridge_secret": "test-secret-for-development"
    }
    
    # Test input data with extra fields (like agent_input)
    input_data = {
        "sql_query": "SELECT COUNT(*) as row_count FROM invoices",
        "table_name": "invoices",
        "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db",
        "monitoring_phase": "before"
    }
    
    print("🔧 Testing SQLExecutor tool execution with extra fields...")
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
    test_sql_executor_with_extra_fields() 