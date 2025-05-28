from memra import Agent, Department, LLM

# Define LLMs that agents can use
default_llm = LLM(model="gpt-4", temperature=0.1)
parsing_llm = LLM(model="claude-3-opus", temperature=0)  # More accurate for structured extraction
manager_llm = LLM(model="gpt-4-turbo", temperature=0.3)  # Balanced for decision-making

# Define agents with specific LLMs
etl_agent = Agent(
    role="Data Engineer",
    job="Extract invoice schema from Postgres database",
    llm=default_llm,  # Standard LLM for SQL generation
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
    llm=parsing_llm,  # High-accuracy LLM for document parsing
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
        {"name": "PostgresInsert", "hosted_by": "mcp"}
    ],
    input_keys=["invoice_data", "invoice_schema"],
    output_key="write_confirmation"
)

# Manager with its own LLM
manager_agent = Agent(
    role="Accounts Payable Manager",
    job="Coordinate invoice processing pipeline and handle exceptions",
    llm=manager_llm,  # Manager gets a more flexible LLM
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

# Create the Accounts Payable Department
ap_department = Department(
    name="Accounts Payable",
    mission="Process invoices accurately into financial system per company data standards",
    agents=[etl_agent, parser_agent, writer_agent],
    manager_agent=manager_agent,
    default_llm=default_llm,  # Fallback for any agent without explicit LLM
    workflow_order=["Data Engineer", "Invoice Parser", "Data Entry Specialist"]
)

# Example usage
if __name__ == "__main__":
    from memra.execution import ExecutionEngine
    
    # This is how a developer would use the department
    engine = ExecutionEngine()
    input_data = {
        "file": "path/to/invoice.pdf",
        "connection": "postgres://ap_user:password@localhost:5432/finance"
    }
    
    result = engine.execute_department(ap_department, input_data)
    
    if result.success:
        print("✅ Invoice processing completed!")
        print(f"Result: {result.data}")
    else:
        print(f"❌ Processing failed: {result.error}")
    
    print(f"Workflow result: {result}") 