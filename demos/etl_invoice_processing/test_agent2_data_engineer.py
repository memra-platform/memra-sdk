#!/usr/bin/env python3
"""
Test Agent 2: Data Engineer
"""

import os
import sys
sys.path.append('/Users/tarpus/memra')

from memra import Agent, LLM, Department
from memra.execution import ExecutionEngine

def test_data_engineer_agent():
    """Test the Data Engineer agent"""
    
    print("🧪 TESTING AGENT 2: Data Engineer")
    print("=" * 60)
    
    # Create the Data Engineer agent
    default_llm = LLM(
        model="llama-3.2-11b-vision-preview",
        temperature=0.1,
        max_tokens=1000
    )
    
    etl_agent = Agent(
        role="Data Engineer",
        job="Extract invoice schema from database",
        llm=default_llm,
        sops=[
            "Connect to database using provided connection string",
            "Generate SQL query: SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'invoices' ORDER BY ordinal_position",
            "Execute the generated SQL query using SQLExecutor tool",
            "Extract column names, types, and constraints from results",
            "Return schema as structured JSON with column information"
        ],
        systems=["Database"],
        tools=[
            {"name": "SQLExecutor", "hosted_by": "mcp", "input_keys": ["sql_query"]}
        ],
        input_keys=["connection", "table_name", "sql_query"],
        output_key="invoice_schema"
    )
    
    print(f"✅ Created agent: {etl_agent.role}")
    print(f"   Job: {etl_agent.job}")
    print(f"   Tools: {[tool.name for tool in etl_agent.tools]}")
    print(f"   Input keys: {etl_agent.input_keys}")
    print(f"   Output key: {etl_agent.output_key}")
    
    # Create a simple department with just this agent
    test_department = Department(
        name="Test Data Engineer",
        mission="Test the Data Engineer agent",
        agents=[etl_agent],
        workflow_order=["Data Engineer"],
        context={
            "mcp_bridge_url": "http://localhost:8082",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )
    
    # Prepare test inputs
    test_inputs = {
        "table_name": "invoices",
        "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db",
        "sql_query": "SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'invoices' ORDER BY ordinal_position"
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
            
            # Show the schema results
            if hasattr(result, 'data') and result.data:
                print(f"\n📋 Schema Results:")
                schema_data = result.data.get('invoice_schema', {})
                if 'data' in schema_data:
                    sql_result = schema_data['data']
                    if 'results' in sql_result:
                        columns = sql_result['results']
                        print(f"   Found {len(columns)} columns in invoices table:")
                        for col in columns:
                            print(f"     - {col.get('column_name', 'N/A')}: {col.get('data_type', 'N/A')} (nullable: {col.get('is_nullable', 'N/A')})")
        
        return result.success
        
    except Exception as e:
        print(f"\n❌ Agent execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_engineer_agent()
    if success:
        print(f"\n🎉 Agent 2 test PASSED!")
    else:
        print(f"\n💥 Agent 2 test FAILED!") 