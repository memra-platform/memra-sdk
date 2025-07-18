#!/usr/bin/env python3
"""
Test Agent 3: Invoice Parser
"""

import os
import sys
sys.path.append('/Users/tarpus/memra')

from memra import Agent, LLM, Department
from memra.execution import ExecutionEngine

def test_invoice_parser_agent():
    """Test the Invoice Parser agent"""
    
    print("🧪 TESTING AGENT 3: Invoice Parser")
    print("=" * 60)
    
    # Create the Invoice Parser agent
    parsing_llm = LLM(
        model="llama-3.2-11b-vision-preview",
        temperature=0.1,
        max_tokens=1000
    )
    
    parser_agent = Agent(
        role="Invoice Parser",
        job="Extract structured data from invoice PDF using vision model",
        llm=parsing_llm,
        sops=[
            "Load invoice PDF file",
            "Send to vision model for field extraction",
            "Print out the raw JSON data returned by vision model tools",
            "Validate extracted data against schema types",
            "Return structured invoice data"
        ],
        systems=["InvoiceStore"],
        tools=[
            {"name": "PDFProcessor", "hosted_by": "mcp"}
        ],
        input_keys=["file"],
        output_key="invoice_data"
    )
    
    print(f"✅ Created agent: {parser_agent.role}")
    print(f"   Job: {parser_agent.job}")
    print(f"   Tools: {[tool.name for tool in parser_agent.tools]}")
    print(f"   Input keys: {parser_agent.input_keys}")
    print(f"   Output key: {parser_agent.output_key}")
    
    # Create a simple department with just this agent
    test_department = Department(
        name="Test Invoice Parser",
        mission="Test the Invoice Parser agent",
        agents=[parser_agent],
        workflow_order=["Invoice Parser"],
        context={
            "mcp_bridge_url": "http://localhost:8082",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )
    
    # Use a real invoice PDF file instead of the academic paper
    test_pdf_path = "/Users/tarpus/memra/demos/etl_invoice_processing/data/invoices/10352259401.PDF"
    
    if not os.path.exists(test_pdf_path):
        print(f"❌ Test PDF file not found: {test_pdf_path}")
        return False
    
    # Prepare test inputs
    test_inputs = {
        "file": test_pdf_path
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
            
            # Show the extracted invoice data
            if hasattr(result, 'data') and result.data:
                print(f"\n📋 Invoice Data Results:")
                invoice_data = result.data.get('invoice_data', {})
                if 'data' in invoice_data:
                    pdf_result = invoice_data['data']
                    if 'extracted_data' in pdf_result:
                        extracted = pdf_result['extracted_data']
                        print(f"   Extracted Data Structure:")
                        if 'headerSection' in extracted:
                            header = extracted['headerSection']
                            print(f"     Vendor: {header.get('vendorName', 'N/A')}")
                            print(f"     Subtotal: {header.get('subtotal', 'N/A')}")
                        if 'billingDetails' in extracted:
                            billing = extracted['billingDetails']
                            print(f"     Invoice #: {billing.get('invoiceNumber', 'N/A')}")
                            print(f"     Date: {billing.get('invoiceDate', 'N/A')}")
                        if 'chargesSummary' in extracted:
                            charges = extracted['chargesSummary']
                            print(f"     Total: {charges.get('document_total', 'N/A')}")
                            print(f"     Tax: {charges.get('secondary_tax', 'N/A')}")
                            print(f"     Line Items: {len(charges.get('lineItemsBreakdown', []))} items")
                    else:
                        print(f"   No extracted_data found in PDF result")
                        print(f"   Available keys: {list(pdf_result.keys())}")
        
        return result.success
        
    except Exception as e:
        print(f"\n❌ Agent execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_invoice_parser_agent()
    if success:
        print(f"\n🎉 Agent 3 test PASSED!")
    else:
        print(f"\n💥 Agent 3 test FAILED!") 