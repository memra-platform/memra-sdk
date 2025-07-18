#!/usr/bin/env python3
"""
Test Agent 5: Post-ETL Database Monitor
"""

import os
import sys
sys.path.append('/Users/tarpus/memra')

from memra import Agent, LLM, Department
from memra.execution import ExecutionEngine
from database_monitor_agent import create_simple_monitor_agent

def test_post_monitor_agent():
    """Test the Post-ETL Database Monitor agent"""
    
    print("🧪 TESTING AGENT 5: Post-ETL Database Monitor")
    print("=" * 60)
    
    # Create the Post-ETL Database Monitor agent
    post_monitor_agent = create_simple_monitor_agent()
    post_monitor_agent.role = "Post-ETL Database Monitor"
    
    print(f"✅ Created agent: {post_monitor_agent.role}")
    print(f"   Job: {post_monitor_agent.job}")
    print(f"   Tools: {[tool.name for tool in post_monitor_agent.tools]}")
    print(f"   Input keys: {post_monitor_agent.input_keys}")
    print(f"   Output key: {post_monitor_agent.output_key}")
    
    # Create a simple department with just this agent
    test_department = Department(
        name="Test Post-ETL Monitor",
        mission="Test the Post-ETL Database Monitor agent",
        agents=[post_monitor_agent],
        workflow_order=["Post-ETL Database Monitor"],
        context={
            "mcp_bridge_url": "http://localhost:8082",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )
    
    # Prepare test inputs for post-ETL monitoring
    test_inputs = {
        "table_name": "invoices",
        "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db",
        "monitoring_phase": "after",
        "sql_query": "SELECT COUNT(*) as row_count, SUM(total_amount) as total_value, AVG(total_amount) as avg_amount FROM invoices WHERE status = 'processed'"
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
        
        if result.success:
            print(f"\n📊 Execution trace:")
            print(f"   Agents executed: {result.trace.agents_executed}")
            print(f"   Tools invoked: {result.trace.tools_invoked}")
            print(f"   Execution times: {result.trace.execution_times}")
            print(f"   Errors: {result.trace.errors}")
            
            # Show the monitoring report results
            if hasattr(result, 'data') and result.data:
                print(f"\n📋 Monitoring Report Results:")
                monitoring_report = result.data.get('monitoring_report', {})
                if 'data' in monitoring_report:
                    report_data = monitoring_report['data']
                    if 'results' in report_data:
                        results = report_data['results']
                        print(f"   Post-ETL Database Status:")
                        for row in results:
                            print(f"     Row Count: {row.get('row_count', 'N/A')}")
                            print(f"     Total Value: ${row.get('total_value', 'N/A')}")
                            print(f"     Average Amount: ${row.get('avg_amount', 'N/A')}")
                    else:
                        print(f"   No results found in monitoring report")
                        print(f"   Available keys: {list(report_data.keys())}")
                else:
                    print(f"   No monitoring report data found")
                    print(f"   Available keys: {list(monitoring_report.keys())}")
        
        return result.success
        
    except Exception as e:
        print(f"\n❌ Agent execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_post_monitor_agent()
    if success:
        print(f"\n🎉 Agent 5 test PASSED!")
    else:
        print(f"\n💥 Agent 5 test FAILED!") 