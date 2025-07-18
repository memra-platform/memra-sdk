#!/usr/bin/env python3
"""
Test Agent 4: Data Entry Specialist
"""

import os
import sys
sys.path.append('/Users/tarpus/memra')

from memra import Agent, LLM, Department
from memra.execution import ExecutionEngine

def test_data_entry_specialist_agent():
    """Test the Data Entry Specialist agent"""
    
    print("🧪 TESTING AGENT 4: Data Entry Specialist")
    print("=" * 60)
    
    # Create the Data Entry Specialist agent
    default_llm = LLM(
        model="llama-3.2-11b-vision-preview",
        temperature=0.1,
        max_tokens=1000
    )
    
    writer_agent = Agent(
        role="Data Entry Specialist", 
        job="Write validated invoice data to database",
        llm=default_llm,
        sops=[
            "Validate invoice data completeness",
            "Map fields to database columns using schema",
            "Print out the data being inserted into database",
            "Connect to database",
            "Insert record into invoices table",
            "Return confirmation with record ID"
        ],
        systems=["Database"],
        tools=[
            {"name": "DataValidator", "hosted_by": "mcp"},
            {"name": "PostgresInsert", "hosted_by": "mcp"}
        ],
        input_keys=["invoice_data"],
        output_key="write_confirmation"
    )
    
    print(f"✅ Created agent: {writer_agent.role}")
    print(f"   Job: {writer_agent.job}")
    print(f"   Tools: {[tool.name for tool in writer_agent.tools]}")
    print(f"   Input keys: {writer_agent.input_keys}")
    print(f"   Output key: {writer_agent.output_key}")
    
    # Create a simple department with just this agent
    test_department = Department(
        name="Test Data Entry Specialist",
        mission="Test the Data Entry Specialist agent",
        agents=[writer_agent],
        workflow_order=["Data Entry Specialist"],
        context={
            "mcp_bridge_url": "http://localhost:8082",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )
    
    # Prepare test invoice data (real data from Agent 3 test)
    test_invoice_data = {
        "headerSection": {
            "vendorName": "Air Liquide Canada Inc.",
            "subtotal": 280.4
        },
        "billingDetails": {
            "invoiceNumber": "10352259401",
            "invoiceDate": "2024-09-19"
        },
        "chargesSummary": {
            "document_total": 457.06,
            "secondary_tax": 32.8,
            "lineItemsBreakdown": [
                {
                    "description": "PROPANE, C3H8, 33 1/3LB, (14KG / 30.8LB)",
                    "quantity": 20,
                    "unit_price": 14.02,
                    "amount": 280.4,
                    "main_product": True
                },
                {
                    "description": "EMPTY CYLINDER PROPANE, 30.8LB (14KG)",
                    "quantity": 28,
                    "unit_price": 0.0,
                    "amount": 0.0,
                    "main_product": False
                },
                {
                    "description": "CHARGE, FUEL SURCHARGE",
                    "quantity": 1.0,
                    "unit_price": 0.0,
                    "amount": 0.0,
                    "main_product": False
                },
                {
                    "description": "CHARGE, CARBON TAX PROPANE, ON, NB, SASK, MANITOBA, 33 1/3LB CYLINDER",
                    "quantity": 20,
                    "unit_price": 7.19,
                    "amount": 143.86,
                    "main_product": False
                }
            ]
        }
    }
    
    # Prepare test inputs
    test_inputs = {
        "invoice_data": test_invoice_data
    }
    
    print(f"\n📊 Test Inputs:")
    print(f"   invoice_data: {test_invoice_data['headerSection']['vendorName']} - ${test_invoice_data['chargesSummary']['document_total']}")
    
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
            
            # Show the write confirmation results
            if hasattr(result, 'data') and result.data:
                print(f"\n📋 Write Confirmation Results:")
                write_confirmation = result.data.get('write_confirmation', {})
                if 'data' in write_confirmation:
                    confirmation_data = write_confirmation['data']
                    print(f"   Write Confirmation Structure:")
                    if 'success' in confirmation_data:
                        print(f"     Success: {confirmation_data['success']}")
                    if 'record_id' in confirmation_data:
                        print(f"     Record ID: {confirmation_data['record_id']}")
                    if 'database_table' in confirmation_data:
                        print(f"     Database Table: {confirmation_data['database_table']}")
                    if 'inserted_data' in confirmation_data:
                        inserted = confirmation_data['inserted_data']
                        print(f"     Inserted Data:")
                        print(f"       Vendor: {inserted.get('vendor_name', 'N/A')}")
                        print(f"       Invoice #: {inserted.get('invoice_number', 'N/A')}")
                        print(f"       Date: {inserted.get('invoice_date', 'N/A')}")
                        print(f"       Total: ${inserted.get('total_amount', 'N/A')}")
                        print(f"       Tax: ${inserted.get('tax_amount', 'N/A')}")
                else:
                    print(f"   No confirmation data found")
                    print(f"   Available keys: {list(write_confirmation.keys())}")
        
        return result.success
        
    except Exception as e:
        print(f"\n❌ Agent execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_entry_specialist_agent()
    if success:
        print(f"\n🎉 Agent 4 test PASSED!")
    else:
        print(f"\n💥 Agent 4 test FAILED!") 