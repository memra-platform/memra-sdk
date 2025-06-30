#!/usr/bin/env python3
"""
Complete Invoice Processing System with Natural Language Queries

This system:
1. Processes invoices from PDF to database (like smart_invoice_processor.py)
2. Adds a Query Agent that can answer natural language questions about the data
"""

import os
import sys
import glob
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memra import Agent, Department, ExecutionEngine

# Set up environment
os.environ['MEMRA_API_KEY'] = 'memra-prod-2024-001'

def discover_invoice_files():
    """Discover invoice files in the invoices directory"""
    invoice_dir = Path("invoices")
    if not invoice_dir.exists():
        invoice_dir.mkdir()
        return []
    
    # Look for PDF files
    pdf_files = list(invoice_dir.glob("*.pdf")) + list(invoice_dir.glob("*.PDF"))
    return [str(f) for f in pdf_files]

def create_invoice_processing_department():
    """Create the invoice processing department"""
    
    # Schema extraction agent
    schema_agent = Agent(
        role="Schema Engineer",
        job="Extract invoice database schema",
        tools=[
            {"name": "DatabaseQueryTool", "hosted_by": "memra"}
        ],
        output_key="invoice_schema"
    )
    
    # Invoice processing agent
    processor_agent = Agent(
        role="Invoice Processor",
        job="Extract structured data from invoice PDF",
        tools=[
            {"name": "PDFProcessor", "hosted_by": "memra"},
            {"name": "InvoiceExtractionWorkflow", "hosted_by": "memra"}
        ],
        input_keys=["file", "invoice_schema"],
        output_key="invoice_data"
    )
    
    # Database writer agent
    writer_agent = Agent(
        role="Database Writer",
        job="Insert validated invoice data into database",
        tools=[
            {"name": "DataValidator", "hosted_by": "mcp"},
            {"name": "PostgresInsert", "hosted_by": "mcp"}
        ],
        input_keys=["invoice_data", "invoice_schema"],
        output_key="write_confirmation"
    )
    
    return Department(
        name="Invoice Processing",
        mission="Process invoices from PDF to database",
        agents=[schema_agent, processor_agent, writer_agent],
        workflow_order=["Schema Engineer", "Invoice Processor", "Database Writer"],
        context={
            "mcp_bridge_url": "http://localhost:8081",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )

def create_query_department():
    """Create the natural language query department"""
    
    # Schema extraction for queries
    schema_agent = Agent(
        role="Query Schema Engineer",
        job="Extract database schema for query generation",
        tools=[
            {"name": "DatabaseQueryTool", "hosted_by": "memra"}
        ],
        output_key="query_schema"
    )
    
    # Natural language query agent
    query_agent = Agent(
        role="Query Assistant",
        job="Answer natural language questions about invoice data",
        tools=[
            {"name": "TextToSQL", "hosted_by": "mcp"}
        ],
        input_keys=["question", "query_schema"],
        output_key="query_results"
    )
    
    return Department(
        name="Invoice Query System",
        mission="Answer natural language questions about invoice data",
        agents=[schema_agent, query_agent],
        workflow_order=["Query Schema Engineer", "Query Assistant"],
        context={
            "mcp_bridge_url": "http://localhost:8081",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )

def process_invoice(file_path):
    """Process a single invoice file"""
    print(f"\n🔄 Processing Invoice: {os.path.basename(file_path)}")
    print("=" * 60)
    
    department = create_invoice_processing_department()
    engine = ExecutionEngine()
    
    input_data = {
        "file": file_path,
        "connection": "postgresql://tarpus@localhost:5432/memra_invoice_db"
    }
    
    result = engine.execute_department(department, input_data)
    
    if result.success:
        print(f"✅ Successfully processed {os.path.basename(file_path)}")
        
        # Show extracted data
        invoice_data = result.data.get('invoice_data', {})
        if 'headerSection' in invoice_data:
            vendor = invoice_data['headerSection'].get('vendorName', 'Unknown')
            print(f"🏢 Vendor: {vendor}")
        
        # Show database result
        confirmation = result.data.get('write_confirmation', {})
        if 'record_id' in confirmation:
            print(f"💾 Database Record ID: {confirmation['record_id']}")
            return True
        elif confirmation.get('_mock'):
            print("🔄 Database: Mock insertion (MCP bridge issue)")
            return True
        
    else:
        print(f"❌ Failed to process {os.path.basename(file_path)}: {result.error}")
        return False

def query_invoices():
    """Interactive query system for invoices"""
    print(f"\n🔍 Invoice Query System")
    print("Ask natural language questions about your invoice data!")
    print("Examples:")
    print("  • 'Show me all invoices from Air Liquide'")
    print("  • 'What's the total amount of all invoices?'")
    print("  • 'List invoices over $1000'")
    print("  • 'Show me the latest 5 invoices'")
    print("=" * 60)
    
    query_dept = create_query_department()
    engine = ExecutionEngine()
    
    while True:
        print(f"\n💬 Ask a question (or 'quit' to exit):")
        question = input("Question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if not question:
            print("❌ Please enter a question.")
            continue
        
        print(f"\n🤔 Processing your question: '{question}'")
        
        input_data = {
            "question": question,
            "connection": "postgresql://tarpus@localhost:5432/memra_invoice_db"
        }
        
        result = engine.execute_department(query_dept, input_data)
        
        if result.success:
            query_results = result.data.get('query_results', {})
            
            if 'generated_sql' in query_results:
                print(f"\n🔧 Generated SQL:")
                print(f"   {query_results['generated_sql']}")
            
            if 'results' in query_results:
                results = query_results['results']
                print(f"\n📊 Results ({query_results.get('row_count', len(results))} rows):")
                
                if results:
                    # Display results in a table format
                    for i, row in enumerate(results, 1):
                        print(f"  {i}. {row}")
                else:
                    print("  No results found.")
                    
                if query_results.get('_mock'):
                    print("🔄 (This was mock data - MCP bridge not fully connected)")
            else:
                print(f"📝 {query_results.get('message', 'Query completed')}")
        else:
            print(f"❌ Query failed: {result.error}")

def main():
    print("🧠 Complete Invoice Processing System")
    print("Process invoices AND query them with natural language!")
    print("=" * 60)
    
    # Check if we have invoices to process
    files = discover_invoice_files()
    
    if files:
        print(f"\n📄 Found {len(files)} invoice file(s):")
        for file in files:
            filename = os.path.basename(file)
            size = os.path.getsize(file)
            size_kb = size // 1024
            print(f"  • {filename} ({size_kb}KB)")
        
        print(f"\nOptions:")
        print(f"  1. Process invoices first")
        print(f"  2. Go directly to query system")
        print(f"  3. Exit")
        
        choice = input("Your choice (1-3): ").strip()
        
        if choice == "1":
            # Process invoices
            print(f"\n🔄 Processing {len(files)} invoice(s)...")
            for file_path in files:
                process_invoice(file_path)
            
            print(f"\n✅ Invoice processing complete!")
            print(f"Now you can query the data...")
            query_invoices()
            
        elif choice == "2":
            # Go directly to queries
            query_invoices()
            
        elif choice == "3":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice")
            return
    else:
        print(f"\n📂 No invoice files found in invoices/ directory.")
        print(f"Add some PDF invoices to the invoices/ directory first, then run:")
        print(f"  python3 examples/smart_invoice_processor.py")
        print(f"\nOr you can still try the query system with existing data:")
        
        choice = input("Try query system anyway? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            query_invoices()
        else:
            print("👋 Goodbye!")

if __name__ == "__main__":
    main() 