#!/usr/bin/env python3
"""
Test SQLExecutor fix in execution engine
"""

import sys
import os
sys.path.insert(0, '/Users/tarpus/memra')

from memra.execution import ExecutionEngine

def test_sql_executor_real_work():
    """Test that SQLExecutor is correctly identified as real work"""
    
    engine = ExecutionEngine()
    
    # Mock SQLExecutor result (what the MCP bridge returns)
    sql_executor_result = {
        "query": "SELECT COUNT(*) as row_count FROM invoices",
        "results": [{"row_count": 3}],
        "row_count": 1,
        "columns": ["row_count"],
        "success": True
    }
    
    print("🔧 Testing SQLExecutor real work detection...")
    print(f"SQLExecutor result: {sql_executor_result}")
    
    # Test the _is_real_work method
    is_real = engine._is_real_work("SQLExecutor", sql_executor_result)
    
    print(f"✅ Is real work: {is_real}")
    
    if is_real:
        print("🎉 SQLExecutor fix is working!")
    else:
        print("❌ SQLExecutor fix is not working!")

if __name__ == "__main__":
    test_sql_executor_real_work() 