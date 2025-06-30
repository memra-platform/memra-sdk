"""
ETL Invoice Processing Demo
Complete ETL workflow with database monitoring before and after
"""

import os
import sys
from memra import Agent, Department, LLM, check_api_health, get_api_status
from memra.execution import ExecutionEngine
from database_monitor_agent import create_simple_monitor_agent, get_monitoring_queries

# Check for required API key
if not os.getenv("MEMRA_API_KEY"):
    print("❌ Error: MEMRA_API_KEY environment variable is required")
    print("Please set your API key: export MEMRA_API_KEY='your-key-here'")
    print("Contact info@memra.co for API access")
    sys.exit(1)

# Set API configuration
os.environ["MEMRA_API_URL"] = "https://api.memra.co"

# Check API health before starting
print("🔍 Checking Memra API status...")
api_status = get_api_status()
print(f"API Health: {'✅ Healthy' if api_status['api_healthy'] else '❌ Unavailable'}")
print(f"API URL: {api_status['api_url']}")
print(f"Tools Available: {api_status['tools_available']}")

if not api_status['api_healthy']:
    print("❌ Cannot proceed - Memra API is not available")
    sys.exit(1)

# Define LLMs
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
    max_tokens=1500
)

# Define agents
pre_monitor_agent = create_simple_monitor_agent()
pre_monitor_agent.role = "Pre-ETL Database Monitor"

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

post_monitor_agent = create_simple_monitor_agent()
post_monitor_agent.role = "Post-ETL Database Monitor"

manager_agent = Agent(
    role="ETL Process Manager",
    job="Coordinate ETL pipeline and validate data integrity",
    llm=manager_llm,
    sops=[
        "Review pre-ETL database state",
        "Validate ETL process completion",
        "Compare pre and post database states",
        "Generate ETL summary report",
        "Flag any data quality issues"
    ],
    allow_delegation=True,
    output_key="etl_summary"
)

# Create ETL department
etl_department = Department(
    name="ETL Invoice Processing",
    mission="Complete end-to-end ETL process with comprehensive monitoring",
    agents=[pre_monitor_agent, etl_agent, parser_agent, writer_agent, post_monitor_agent],
    manager_agent=manager_agent,
    workflow_order=[
        "Pre-ETL Database Monitor", 
        "Data Engineer", 
        "Invoice Parser", 
        "Data Entry Specialist",
        "Post-ETL Database Monitor"
    ],
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

def main():
    """Run the ETL demo workflow"""
    
    print("\n🚀 Starting ETL Invoice Processing Demo...")
    print("📊 This demo includes comprehensive database monitoring")
    print("📡 Tools will execute on Memra API server")
    
    engine = ExecutionEngine()
    
    # Generate monitoring queries for before and after
    table_name = "invoices"
    before_queries = get_monitoring_queries(table_name, "before")
    after_queries = get_monitoring_queries(table_name, "after")
    
    input_data = {
        "file": "invoices/10352259310.PDF",
        "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db",
        "table_name": table_name,
        "monitoring_phase": "before",
        "sql_query": before_queries[0]  # Pass the first query for row count
    }
    
    # Execute the department
    result = engine.execute_department(etl_department, input_data)
    
    # Display results
    if result.success:
        print("\n✅ ETL process completed successfully!")
        
        # Show manager summary
        if 'etl_summary' in result.data:
            summary = result.data['etl_summary']
            print(f"\n📋 ETL Summary Report:")
            print(f"Status: {summary.get('status', 'unknown')}")
            print(f"Summary: {summary.get('summary', 'No summary available')}")
            
            # Show monitoring comparison
            if 'monitoring_comparison' in summary:
                comparison = summary['monitoring_comparison']
                print(f"\n📊 Database State Comparison:")
                print(f"Pre-ETL Rows: {comparison.get('pre_rows', 'N/A')}")
                print(f"Post-ETL Rows: {comparison.get('post_rows', 'N/A')}")
                print(f"New Records: {comparison.get('new_records', 'N/A')}")
                print(f"Data Quality: {comparison.get('data_quality', 'N/A')}")
        
        # Show record details
        if 'write_confirmation' in result.data:
            confirmation = result.data['write_confirmation']
            if isinstance(confirmation, dict) and 'record_id' in confirmation:
                print(f"\n💾 Invoice processed: Record ID {confirmation['record_id']}")
        
        print(f"\n📡 All tools executed remotely on Memra API server")
        
    else:
        print(f"\n❌ ETL process failed: {result.error}")
    
    # Show execution trace
    print("\n=== Execution Trace ===")
    print(f"Agents executed: {', '.join(result.trace.agents_executed)}")
    print(f"Tools invoked: {', '.join(result.trace.tools_invoked)}")
    if result.trace.errors:
        print(f"Errors: {', '.join(result.trace.errors)}")
    
    print(f"\n🌐 API Calls made to: {api_status['api_url']}")

if __name__ == "__main__":
    main() 