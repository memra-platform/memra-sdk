#!/usr/bin/env python3
"""
Test Agent 1: Pre-ETL Database Monitor
"""

import os
import sys
sys.path.append('/Users/tarpus/memra')

from memra import Agent, LLM, Department
from memra.execution import ExecutionEngine
from database_monitor_agent import create_simple_monitor_agent

def test_pre_monitor_agent():
    """Test the Pre-ETL Database Monitor agent"""
    
    print("🧪 TESTING AGENT 1: Pre-ETL Database Monitor")
    print("=" * 60)
    
    # Create the pre-monitor agent
    pre_monitor_agent = create_simple_monitor_agent()
    pre_monitor_agent.role = "Pre-ETL Database Monitor"
    
    print(f"✅ Created agent: {pre_monitor_agent.role}")
    print(f"   Job: {pre_monitor_agent.job}")
    print(f"   Tools: {[tool.name for tool in pre_monitor_agent.tools]}")
    print(f"   Input keys: {pre_monitor_agent.input_keys}")
    print(f"   Output key: {pre_monitor_agent.output_key}")
    
    # Create a simple department with just this agent
    test_department = Department(
        name="Test Pre-Monitor",
        mission="Test the Pre-ETL Database Monitor agent",
        agents=[pre_monitor_agent],
        workflow_order=["Pre-ETL Database Monitor"],
        context={
            "mcp_bridge_url": "http://localhost:8082",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )
    
    # Prepare test inputs
    test_inputs = {
        "table_name": "invoices",
        "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db",
        "monitoring_phase": "before",
        "sql_query": "SELECT COUNT(*) as row_count FROM invoices"
    }
    
    print(f"\n📊 Test Inputs:")
    for key, value in test_inputs.items():
        print(f"   {key}: {value}")
    
    # Test the agent using the execution engine
    print(f"\n🚀 Running agent through execution engine...")
    try:
        engine = ExecutionEngine()
        result = engine.execute_department(test_department, test_inputs)
        
        print(f"\n✅ Agent execution successful!")
        print(f"📄 Success: {result.success}")
        print(f"📄 Error: {result.error}")
        print(f"📄 Trace: {result.trace}")
        
        if result.success:
            print(f"\n📊 Execution trace:")
            print(f"   Agents executed: {result.trace.agents_executed}")
            print(f"   Tools invoked: {result.trace.tools_invoked}")
            print(f"   Execution times: {result.trace.execution_times}")
            print(f"   Errors: {result.trace.errors}")
        
        return result.success
        
    except Exception as e:
        print(f"\n❌ Agent execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pre_monitor_agent()
    if success:
        print(f"\n🎉 Agent 1 test PASSED!")
    else:
        print(f"\n💥 Agent 1 test FAILED!") 