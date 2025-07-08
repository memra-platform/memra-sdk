#!/usr/bin/env python3
"""
Smart Invoice Processor with Intelligent File Discovery

This system automatically:
1. Empty invoices/ directory → Ask user for file path
2. Single file in invoices/ → Process it automatically  
3. Multiple files in invoices/ → Show list, let user choose or batch process
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

def get_file_to_process():
    """Intelligent file discovery logic"""
    files = discover_invoice_files()
    
    if len(files) == 0:
        print("📂 The invoices/ directory is empty.")
        print("Please provide the path to the invoice you want to process:")
        file_path = input("File path: ").strip()
        
        if not file_path:
            print("❌ No file path provided.")
            return None
            
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
            
        # Copy file to invoices directory
        import shutil
        filename = os.path.basename(file_path)
        dest_path = f"invoices/{filename}"
        shutil.copy2(file_path, dest_path)
        print(f"📁 Copied {filename} to invoices/ directory")
        return dest_path
        
    elif len(files) == 1:
        print(f"📄 Found 1 invoice file: {files[0]}")
        print("🚀 Processing automatically...")
        return files[0]
        
    else:
        print(f"📄 Found {len(files)} invoice files:")
        for i, file in enumerate(files, 1):
            filename = os.path.basename(file)
            size = os.path.getsize(file)
            size_kb = size // 1024
            print(f"  {i}. {filename} ({size_kb}KB)")
        
        print("\nOptions:")
        print("  • Enter a number (1-{}) to process that file".format(len(files)))
        print("  • Enter 'all' to process all files in batch")
        print("  • Enter 'quit' to exit")
        
        choice = input("Your choice: ").strip().lower()
        
        if choice == 'quit':
            return None
        elif choice == 'all':
            return 'batch'
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(files):
                    return files[index]
                else:
                    print("❌ Invalid selection")
                    return None
            except ValueError:
                print("❌ Invalid input")
                return None

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
        name="Smart Invoice Processing",
        mission="Intelligently process invoices from PDF to database",
        agents=[schema_agent, processor_agent, writer_agent],
        workflow_order=["Schema Engineer", "Invoice Processor", "Database Writer"],
        context={
            "mcp_bridge_url": "http://localhost:8081",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )

def process_single_invoice(file_path):
    """Process a single invoice file"""
    print(f"\n🔄 Processing: {os.path.basename(file_path)}")
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
        elif confirmation.get('_mock'):
            print("🔄 Database: Mock insertion (MCP bridge issue)")
        
        return True
    else:
        print(f"❌ Failed to process {os.path.basename(file_path)}: {result.error}")
        return False

def process_batch(file_list):
    """Process multiple invoice files in batch"""
    print(f"\n🔄 Batch Processing: {len(file_list)} files")
    print("=" * 60)
    
    results = []
    for i, file_path in enumerate(file_list, 1):
        print(f"\n📄 File {i}/{len(file_list)}: {os.path.basename(file_path)}")
        success = process_single_invoice(file_path)
        results.append((file_path, success))
    
    # Summary
    print(f"\n📊 Batch Processing Summary:")
    successful = sum(1 for _, success in results if success)
    print(f"✅ Successful: {successful}/{len(file_list)}")
    
    if successful < len(file_list):
        print("❌ Failed files:")
        for file_path, success in results:
            if not success:
                print(f"  • {os.path.basename(file_path)}")

def main():
    print("🧠 Smart Invoice Processor")
    print("Intelligent file discovery and processing")
    print("=" * 60)
    
    # Discover what to process
    target = get_file_to_process()
    
    if target is None:
        print("👋 Goodbye!")
        return
    
    if target == 'batch':
        files = discover_invoice_files()
        process_batch(files)
    else:
        process_single_invoice(target)

if __name__ == "__main__":
    main() 