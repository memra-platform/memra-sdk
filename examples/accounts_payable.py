from memra import Agent, Department, LLM
from memra.execution import ExecutionEngine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEFAULT_LLM_CONFIG, AGENT_LLM_CONFIG

# Define LLMs for different agent types
default_llm = LLM(
    model=DEFAULT_LLM_CONFIG["model"],
    temperature=DEFAULT_LLM_CONFIG["temperature"],
    max_tokens=DEFAULT_LLM_CONFIG["max_tokens"]
)

parsing_llm = LLM(
    model=AGENT_LLM_CONFIG["parsing"]["model"],
    temperature=AGENT_LLM_CONFIG["parsing"]["temperature"],
    max_tokens=AGENT_LLM_CONFIG["parsing"]["max_tokens"]
)

manager_llm = LLM(
    model=AGENT_LLM_CONFIG["manager"]["model"],
    temperature=AGENT_LLM_CONFIG["manager"]["temperature"],
    max_tokens=AGENT_LLM_CONFIG["manager"]["max_tokens"]
)

# Define the agents with their roles, jobs, tools, and systems
etl_agent = Agent(
    role="Data Engineer",
    job="Extract invoice schema from Postgres database",
    llm=default_llm,
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

# Fallback agent if schema extraction fails
schema_loader = Agent(
    role="Schema Loader", 
    job="Load invoice schema from local file",
    llm=default_llm,
    sops=[
        "Read schema file from disk",
        "Validate schema format",
        "Return parsed schema"
    ],
    systems=["FileSystem"],
    tools=[
        {"name": "FileReader", "hosted_by": "memra"}
    ],
    config={"path": "/local/dependencies/data_model.json"},
    output_key="invoice_schema"
)

parser_agent = Agent(
    role="Invoice Parser",
    job="Extract structured data from invoice PDF using schema",
    llm=parsing_llm,  # Use specialized parsing LLM
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

writer_agent = Agent(
    role="Data Entry Specialist",
    job="Write validated invoice data to Postgres database",
    llm=default_llm,
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

# Define the manager who oversees the workflow
manager_agent = Agent(
    role="Accounts Payable Manager",
    job="Coordinate invoice processing pipeline and handle exceptions",
    llm=manager_llm,  # Use specialized manager LLM
    sops=[
        "Check if schema extraction succeeded",
        "If schema missing, delegate to Schema Loader",
        "Validate parsed invoice has required fields",
        "Ensure invoice total matches line items before DB write",
        "Handle and log any errors with appropriate escalation"
    ],
    allow_delegation=True,
    fallback_agents={
        "Data Engineer": "Schema Loader"
    },
    output_key="workflow_status"
)

# Create the department with all agents
ap_department = Department(
    name="Accounts Payable",
    mission="Process invoices accurately into financial system per company data standards",
    agents=[etl_agent, schema_loader, parser_agent, writer_agent],
    manager_agent=manager_agent,
    workflow_order=["Data Engineer", "Invoice Parser", "Data Entry Specialist"],
    dependencies=["PostgresDB", "InvoiceStore", "PaymentGateway"],
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

# Execute the department
engine = ExecutionEngine()
input_data = {
    "file": "path/to/your/invoice.pdf",  # Update this path to your invoice file
    "connection": "postgresql://your_username@localhost:5432/memra_invoice_db"
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