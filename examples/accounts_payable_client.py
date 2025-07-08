"""
Client-side Accounts Payable Example
This version calls the Memra API hosted on Fly.io instead of running tools locally
"""

import os
from memra import Agent, Department, LLM, check_api_health, get_api_status
from memra.execution import ExecutionEngine
import sys

# Check for required API key
if not os.getenv("MEMRA_API_KEY"):
    print("❌ Error: MEMRA_API_KEY environment variable is required")
    print("Please set your API key: export MEMRA_API_KEY='your-key-here'")
    print("Contact info@memra.co for API access")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEFAULT_LLM_CONFIG, AGENT_LLM_CONFIG

# Set API configuration
os.environ["MEMRA_API_URL"] = "https://api.memra.co"  # Use production API

# Check API health before starting
print("🔍 Checking Memra API status...")
api_status = get_api_status()
print(f"API Health: {'✅ Healthy' if api_status['api_healthy'] else '❌ Unavailable'}")
print(f"API URL: {api_status['api_url']}")
print(f"Tools Available: {api_status['tools_available']}")

if not api_status['api_healthy']:
    print("❌ Cannot proceed - Memra API is not available")
    print("Make sure the API server is running on localhost:8080")
    exit(1)

# Define LLMs (these are just metadata - actual LLM calls happen on the server)
default_llm = LLM(
    model="llama-3.2-11b-vision-preview",
    temperature=0.1,
    max_tokens=2000
)

parsing_llm = LLM(
    model="llama-3.2-11b-vision-preview", 
    temperature=0.0,
    max_tokens=4000
)

manager_llm = LLM(
    model="llama-3.2-11b-vision-preview",
    temperature=0.2,
    max_tokens=1000
)

# Define agents (same declarative interface as before)
etl_agent = Agent(
    role="Data Engineer",
    job="Extract invoice schema from database",
    llm=default_llm,
    sops=[
        "Connect to database using credentials",
        "Query information_schema for invoices table", 
        "Extract column names, types, and constraints",
        "Return schema as structured JSON"
    ],
    systems=["Database"],
    tools=[
        {"name": "DatabaseQueryTool", "hosted_by": "memra"}
    ],
    output_key="invoice_schema"
)

parser_agent = Agent(
    role="Invoice Parser",
    job="Extract structured data from invoice PDF using schema",
    llm=parsing_llm,
    sops=[
        "Load invoice PDF file",
        "Send to vision model for field extraction",
        "Validate extracted data against schema types",
        "Return structured invoice data"
    ],
    systems=["InvoiceStore"],
    tools=[
        {"name": "PDFProcessor", "hosted_by": "memra"},
        {"name": "InvoiceExtractionWorkflow", "hosted_by": "memra"}
    ],
    input_keys=["file", "invoice_schema"],
    output_key="invoice_data"
)

writer_agent = Agent(
    role="Data Entry Specialist", 
    job="Write validated invoice data to database",
    llm=default_llm,
    sops=[
        "Validate invoice data completeness",
        "Map fields to database columns using schema",
        "Connect to database",
        "Insert record into invoices table",
        "Return confirmation with record ID"
    ],
    systems=["Database"],
    tools=[
        {"name": "DataValidator", "hosted_by": "mcp"},
        {"name": "PostgresInsert", "hosted_by": "mcp"}
    ],
    input_keys=["invoice_data", "invoice_schema"],
    output_key="write_confirmation"
)

manager_agent = Agent(
    role="Accounts Payable Manager",
    job="Coordinate invoice processing pipeline and handle exceptions",
    llm=manager_llm,
    sops=[
        "Check if schema extraction succeeded",
        "Validate parsed invoice has required fields", 
        "Ensure invoice total matches line items before DB write",
        "Handle and log any errors with appropriate escalation"
    ],
    allow_delegation=True,
    output_key="workflow_status"
)

# Create department
ap_department = Department(
    name="Accounts Payable",
    mission="Process invoices accurately into financial system per company data standards",
    agents=[etl_agent, parser_agent, writer_agent],
    manager_agent=manager_agent,
    workflow_order=["Data Engineer", "Invoice Parser", "Data Entry Specialist"],
    dependencies=["Database", "InvoiceStore"],
    execution_policy={
        "retry_on_fail": True,
        "max_retries": 2,
        "halt_on_validation_error": True,
        "timeout_seconds": 300
    },
    context={
        "company_id": "acme_corp",
        "fiscal_year": "2024",
        "mcp_bridge_url": "http://localhost:8081",
        "mcp_bridge_secret": "test-secret-for-development"
    }
)

# Execute the department (tools will run on Fly.io)
print("\n🚀 Starting invoice processing workflow...")
print("📡 Tools will execute on Memra API server")

engine = ExecutionEngine()
input_data = {
    "file": "invoices/10352259310.PDF",  # For development - users should update to their invoice path
    "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db"
}

result = engine.execute_department(ap_department, input_data)

# Display results (same as before)
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
        
        # Show recommendations
        if 'recommendations' in manager_report and manager_report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in manager_report['recommendations']:
                print(f"   • {rec}")
    
    # Try to get record_id if it exists
    if result.data and 'write_confirmation' in result.data:
        confirmation = result.data['write_confirmation']
        if isinstance(confirmation, dict) and 'record_id' in confirmation:
            print(f"\n💾 Invoice processed successfully: Record ID {confirmation['record_id']}")
        else:
            print(f"\n💾 Write confirmation: {confirmation}")
    
    print(f"\n📡 All tools executed remotely on Memra API server")
    
else:
    print(f"❌ Processing failed: {result.error}")

# Show execution trace
print("\n=== Execution Trace ===")
print(f"Agents executed: {', '.join(result.trace.agents_executed)}")
print(f"Tools invoked: {', '.join(result.trace.tools_invoked)}")
if result.trace.errors:
    print(f"Errors: {', '.join(result.trace.errors)}")

print(f"\n🌐 API Calls made to: {api_status['api_url']}") 