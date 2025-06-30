#!/usr/bin/env python3
"""
Smart Accounts Payable Example with File Discovery
This example demonstrates intelligent file discovery and management
"""

import os
import sys
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memra import Agent, Department
from memra.execution import ExecutionEngine

# Set up environment
os.environ['MEMRA_API_KEY'] = 'memra-prod-2024-001'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced agents with smart file discovery
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

# Smart Invoice Parser with file discovery
smart_parser_agent = Agent(
    role="Smart Invoice Parser",
    job="Extract structured data from invoice PDFs",
    sops=[
        "Load and process the invoice PDF file",
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
    input_keys=["file", "invoice_schema"],  # file is the correct key
    output_key="invoice_data"
)

writer_agent = Agent(
    role="Data Entry Specialist",
    job="Write validated invoice data to Postgres database",
    sops=[
        "Validate invoice data completeness",
        "Map fields to database columns using schema",
        "Connect to PostgresDB",
        "Insert record into invoices table",
        "Return confirmation with record ID"
    ],
    systems=["PostgresDB"],
    tools=[
        {"name": "DataValidator", "hosted_by": "memra"},
        {"name": "PostgresInsert", "hosted_by": "memra"}
    ],
    input_keys=["invoice_data", "invoice_schema"],
    output_key="write_confirmation"
)

# Smart manager that handles file discovery workflow
smart_manager_agent = Agent(
    role="Smart Accounts Payable Manager",
    job="Coordinate intelligent invoice processing with file discovery",
    sops=[
        "Check if specific file path was provided",
        "If no file specified, discover available files in invoices/ directory",
        "Handle file copying from external locations if needed",
        "Coordinate schema extraction and invoice processing",
        "Validate results and provide comprehensive reporting"
    ],
    allow_delegation=True,
    output_key="workflow_status"
)

# Create the smart department
smart_ap_department = Department(
    name="Smart Accounts Payable",
    mission="Intelligently discover and process invoices with minimal user input",
    agents=[etl_agent, smart_parser_agent, writer_agent],
    manager_agent=smart_manager_agent,
    workflow_order=["Data Engineer", "Smart Invoice Parser", "Data Entry Specialist"],
    dependencies=["PostgresDB", "InvoiceStore", "FileSystem"],
    execution_policy={
        "retry_on_fail": True,
        "max_retries": 2,
        "halt_on_validation_error": True,
        "timeout_seconds": 300
    },
    context={
        "company_id": "acme_corp",
        "fiscal_year": "2024",
        "default_invoice_dir": "invoices",
        "mcp_bridge_url": "http://localhost:8081",
        "mcp_bridge_secret": "test-secret-for-development"
    }
)

def main():
    print("🧠 Smart Accounts Payable with File Discovery")
    print("=" * 60)
    
    # Create execution engine
    engine = ExecutionEngine()
    
    # Example 1: Auto-discovery mode (no file specified)
    print("\n📂 Example 1: Auto-discovery mode")
    print("Scanning invoices/ directory for available files...")
    
    input_data_auto = {
        "file": "invoices/10352259310.PDF",  # Default file for auto-discovery demo
        "connection": "postgresql://tarpus@localhost:5432/memra_invoice_db"
    }
    
    result = engine.execute_department(smart_ap_department, input_data_auto)
    
    if result.success:
        print("✅ Auto-discovery workflow completed successfully!")
        display_results(result)
    else:
        print(f"❌ Auto-discovery failed: {result.error}")
    
    print("\n" + "="*60)
    
    # Example 2: External file mode
    print("\n📁 Example 2: External file processing")
    print("Processing file from external location...")
    
    input_data_external = {
        "file": "invoices/10352259310.PDF",  # Use existing file for demo
        "connection": "postgresql://tarpus@localhost:5432/memra_invoice_db"
    }
    
    result = engine.execute_department(smart_ap_department, input_data_external)
    
    if result.success:
        print("✅ External file workflow completed successfully!")
        display_results(result)
    else:
        print(f"❌ External file processing failed: {result.error}")
    
    print("\n" + "="*60)
    
    # Example 3: Specific file mode
    print("\n🎯 Example 3: Specific file processing")
    print("Processing specific file from invoices/ directory...")
    
    input_data_specific = {
        "file": "invoices/10352259310.PDF",  # Specific file
        "connection": "postgresql://tarpus@localhost:5432/memra_invoice_db"
    }
    
    result = engine.execute_department(smart_ap_department, input_data_specific)
    
    if result.success:
        print("✅ Specific file workflow completed successfully!")
        display_results(result)
    else:
        print(f"❌ Specific file processing failed: {result.error}")

def display_results(result):
    """Display comprehensive workflow results"""
    
    # Show manager validation results
    if 'workflow_status' in result.data:
        manager_report = result.data['workflow_status']
        print(f"\n🔍 Manager Report:")
        print(f"Status: {manager_report.get('validation_status', 'unknown')}")
        print(f"Summary: {manager_report.get('summary', 'No summary available')}")
        
        # Show agent performance
        if 'agent_performance' in manager_report:
            print(f"\n📊 Agent Performance:")
            for agent_role, performance in manager_report['agent_performance'].items():
                work_quality = performance['work_quality']
                status_emoji = "✅" if work_quality == "real" else "🔄"
                print(f"{status_emoji} {agent_role}: {performance['status']}")
                if performance['tools_real_work']:
                    print(f"   Real work: {', '.join(performance['tools_real_work'])}")
    
    # Show file discovery results
    if 'invoice_data' in result.data:
        invoice_data = result.data['invoice_data']
        if isinstance(invoice_data, dict) and 'file_metadata' in invoice_data:
            print(f"\n📄 File Processing:")
            metadata = invoice_data['file_metadata']
            print(f"Processed: {metadata.get('filename', 'unknown')}")
            print(f"Location: {metadata.get('path', 'unknown')}")
            print(f"Size: {metadata.get('size', 'unknown')}")
    
    # Show database results
    if 'write_confirmation' in result.data:
        confirmation = result.data['write_confirmation']
        if isinstance(confirmation, dict) and 'record_id' in confirmation:
            print(f"\n💾 Database: Record ID {confirmation['record_id']}")
    
    # Show execution trace
    print(f"\n🔄 Execution: {', '.join(result.trace.agents_executed)}")
    print(f"🛠 Tools: {', '.join(result.trace.tools_invoked)}")

if __name__ == "__main__":
    main() 