#!/usr/bin/env python3
"""
Accounts Payable Example with MCP Integration
This example demonstrates using MCP tools for database operations
"""

import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memra import Agent, Department
from memra.execution import ExecutionEngine

# Set up environment
os.environ['MEMRA_API_KEY'] = 'memra-prod-2024-001'
# Note: MEMRA_API_URL defaults to https://api.memra.co if not set

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the agents - using MCP for database operations
etl_agent = Agent(
    role="Data Engineer",
    job="Extract invoice schema from Postgres database",
    sops=[
        "Connect to PostgresDB using credentials",
        "Query information_schema for invoices table",
        "Extract column names, types, and constraints",
        "Return schema as structured JSON"
    ],
    systems=["PostgresDB"],
    tools=[
        {"name": "DatabaseQueryTool", "hosted_by": "memra"}
    ],
    output_key="invoice_schema"
)

parser_agent = Agent(
    role="Invoice Parser",
    job="Extract structured data from invoice PDF using schema",
    sops=[
        "Load invoice PDF file",
        "Convert to high-contrast images if needed",
        "Run OCR to extract text",
        "Use schema to identify and extract fields",
        "Validate extracted data against schema types",
        "Return structured invoice data"
    ],
    systems=["InvoiceStore"],
    tools=[
        {"name": "PDFProcessor", "hosted_by": "memra"},
        {"name": "OCRTool", "hosted_by": "memra"},
        {"name": "InvoiceExtractionWorkflow", "hosted_by": "memra"}
    ],
    input_keys=["file", "invoice_schema"],
    output_key="invoice_data"
)

# THIS IS THE KEY CHANGE: Using MCP tools for database operations
writer_agent = Agent(
    role="Data Entry Specialist",
    job="Write validated invoice data to Postgres database via MCP",
    sops=[
        "Validate invoice data completeness",
        "Map fields to database columns using schema",
        "Use MCP bridge to connect to PostgresDB",
        "Insert record into invoices table via MCP",
        "Return confirmation with record ID"
    ],
    systems=["PostgresDB"],
    tools=[
        {
            "name": "DataValidator", 
            "hosted_by": "mcp",
            "config": {
                "bridge_url": "http://localhost:8081",
                "bridge_secret": "test-secret-for-development"
            }
        },
        {
            "name": "PostgresInsert", 
            "hosted_by": "mcp",
            "config": {
                "bridge_url": "http://localhost:8081",
                "bridge_secret": "test-secret-for-development"
            }
        }
    ],
    input_keys=["invoice_data", "invoice_schema"],
    output_key="write_confirmation"
)

# Define the manager
manager_agent = Agent(
    role="Accounts Payable Manager",
    job="Coordinate invoice processing pipeline and handle exceptions",
    sops=[
        "Check if schema extraction succeeded",
        "Validate parsed invoice has required fields",
        "Ensure invoice total matches line items before DB write",
        "Handle and log any errors with appropriate escalation"
    ],
    allow_delegation=True,
    output_key="workflow_status"
)

# Create the department
ap_department = Department(
    name="Accounts Payable with MCP",
    mission="Process invoices accurately into financial system using MCP bridge",
    agents=[etl_agent, parser_agent, writer_agent],
    manager_agent=manager_agent,
    workflow_order=["Data Engineer", "Invoice Parser", "Data Entry Specialist"],
    dependencies=["PostgresDB", "InvoiceStore"],
    execution_policy={
        "retry_on_fail": True,
        "max_retries": 2,
        "halt_on_validation_error": True,
        "timeout_seconds": 300
    },
    context={
        "company_id": "acme_corp",
        "fiscal_year": "2024"
    }
)

def main():
    print("🧪 Testing Accounts Payable with MCP Integration")
    print("=" * 60)
    
    # Create execution engine
    engine = ExecutionEngine()
    
    # Execute the department
    input_data = {
        "file": "invoices/10352259310.PDF",
        "connection": "postgresql://tarpus@localhost:5432/memra_invoice_db"
    }

    result = engine.execute_department(ap_department, input_data)

    if result.success:
        print("✅ Invoice processing completed successfully!")
        
        # Show manager validation results
        if 'workflow_status' in result.data:
            manager_report = result.data['workflow_status']
            print(f"\n🔍 Manager Validation Report:")
            print(f"Status: {manager_report.get('validation_status', 'unknown')}")
            print(f"Summary: {manager_report.get('summary', 'No summary available')}")
            
            # Show agent performance analysis
            if 'agent_performance' in manager_report:
                print(f"\n📊 Agent Performance Analysis:")
                for agent_role, performance in manager_report['agent_performance'].items():
                    work_quality = performance['work_quality']
                    status_emoji = "✅" if work_quality == "real" else "🔄"
                    print(f"{status_emoji} {agent_role}: {performance['status']}")
                    if performance['tools_real_work']:
                        print(f"   Real work: {', '.join(performance['tools_real_work'])}")
                    if performance['tools_mock_work']:
                        print(f"   Mock work: {', '.join(performance['tools_mock_work'])}")
            
            # Show workflow analysis
            if 'workflow_analysis' in manager_report:
                analysis = manager_report['workflow_analysis']
                print(f"\n📈 Workflow Analysis:")
                print(f"Overall Quality: {analysis['overall_quality']}")
                print(f"Real Work: {analysis['real_work_agents']}/{analysis['total_agents']} agents ({analysis['real_work_percentage']:.1f}%)")
        
        # Try to get record_id if it exists
        if result.data and 'write_confirmation' in result.data:
            confirmation = result.data['write_confirmation']
            print(f"\n💾 Write confirmation: {confirmation}")
        
        # Show execution trace
        print("\n=== Execution Trace ===")
        print(f"Agents executed: {', '.join(result.trace.agents_executed)}")
        print(f"Tools invoked: {', '.join(result.trace.tools_invoked)}")
        if result.trace.errors:
            print(f"Errors: {', '.join(result.trace.errors)}")
    else:
        print(f"❌ Processing failed: {result.error}")
        print("\n=== Execution Trace ===")
        print(f"Agents executed: {', '.join(result.trace.agents_executed)}")
        print(f"Tools invoked: {', '.join(result.trace.tools_invoked)}")
        print(f"Errors: {', '.join(result.trace.errors)}")

    # Show audit information
    audit = engine.get_last_audit()
    if audit:
        print(f"\n=== Audit ===")
        print(f"Agents executed: {audit.agents_run}")
        print(f"Tools used: {audit.tools_invoked}")
        print(f"Total duration: {audit.duration_seconds:.1f}s")

if __name__ == "__main__":
    main() 