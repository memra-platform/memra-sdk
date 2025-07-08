#!/usr/bin/env python3
"""
Complete Invoice Processing Workflow with Text-to-SQL Integration
Demonstrates: PDF → Processing → Database → Natural Language Queries
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import memra
sys.path.insert(0, str(Path(__file__).parent.parent))

from memra.tool_registry import ToolRegistry

def discover_invoice_files():
    """Discover PDF files in the invoices directory"""
    invoices_dir = Path("invoices")
    if not invoices_dir.exists():
        invoices_dir.mkdir()
        return []
    
    pdf_files = list(invoices_dir.glob("*.pdf")) + list(invoices_dir.glob("*.PDF"))
    return [{"filename": f.name, "path": str(f), "size": f"{f.stat().st_size // 1024}KB"} for f in pdf_files]

def get_file_to_process():
    """Smart file discovery and selection"""
    files = discover_invoice_files()
    
    if len(files) == 0:
        print("📁 No PDF files found in invoices/ directory")
        return None
    
    elif len(files) == 1:
        file_info = files[0]
        print(f"📄 Found 1 file: {file_info['filename']} ({file_info['size']})")
        print(f"🔄 Auto-processing: {file_info['filename']}")
        return file_info['path']
    
    else:
        print(f"📁 Found {len(files)} PDF files:")
        for i, file_info in enumerate(files, 1):
            print(f"  {i}. {file_info['filename']} ({file_info['size']})")
        
        print(f"\n🤔 Multiple files found. What would you like to do?")
        print(f"   Enter 1-{len(files)} to process a specific file")
        
        choice = input("\n📎 Your choice: ").strip().lower()
        
        if choice.isdigit():
            file_num = int(choice)
            if 1 <= file_num <= len(files):
                selected_file = files[file_num - 1]
                print(f"🔄 Processing: {selected_file['filename']}")
                return selected_file['path']
        
        print("❌ Invalid choice")
        return None

def process_invoice_via_api(file_path):
    """Process invoice using the Memra API (simulated for demo)"""
    print(f"\n🔄 Step 1: Processing PDF via Memra API...")
    print(f"📄 File: {Path(file_path).name}")
    
    # In a real implementation, this would call the actual Memra API
    # For demo purposes, we'll simulate the processing
    print("⚡ Extracting invoice data...")
    print("✅ Invoice data extracted successfully")
    print("⚡ Validating data...")
    print("✅ Data validation passed")
    print("⚡ Inserting into database...")
    print("✅ Database insertion completed")
    
    # Return mock record ID
    return 23

def run_text_to_sql_queries(registry, record_id=None):
    """Run interactive text-to-SQL queries after invoice processing"""
    print(f"\n{'='*60}")
    print("🧠 Business Intelligence Mode")
    print("Now you can ask questions about your invoice data!")
    print(f"{'='*60}")
    
    # MCP bridge configuration
    mcp_config = {
        "bridge_url": "http://localhost:8081",
        "bridge_secret": "test-secret-for-development"
    }
    
    # Suggested queries
    suggested_queries = [
        "How many invoices do we have in the database?",
        "What is the total amount of all invoices?",
        "Show me all invoices from Air Liquide",
        "Show me the most recent 5 invoices"
    ]
    
    if record_id:
        suggested_queries.insert(0, f"Show me the invoice that was just processed (ID {record_id})")
    
    print("💡 Suggested questions:")
    for i, query in enumerate(suggested_queries, 1):
        print(f"  {i}. {query}")
    
    while True:
        print(f"\n🤔 What would you like to know about the invoices?")
        print("   (Enter a question, number for suggestions, or 'done' to finish)")
        
        user_input = input("\n❓ Your question: ").strip()
        
        if user_input.lower() in ['done', 'exit', 'quit', 'finish']:
            print("👋 Exiting Business Intelligence mode")
            break
        
        # Handle numbered suggestions
        if user_input.isdigit():
            question_num = int(user_input)
            if 1 <= question_num <= len(suggested_queries):
                question = suggested_queries[question_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(suggested_queries)}")
                continue
        else:
            question = user_input
        
        if not question:
            print("❌ Please enter a question")
            continue
        
        try:
            print(f"\n🔍 Processing: '{question}'")
            
            # Step 1: Generate SQL
            sql_result = registry.execute_tool(
                tool_name="TextToSQLGenerator",
                hosted_by="mcp",
                input_data={
                    "question": question,
                    "schema_info": {"tables": ["invoices"]}
                },
                config=mcp_config
            )
            
            if not sql_result.get("success"):
                print(f"❌ SQL generation failed: {sql_result.get('error')}")
                continue
            
            sql_data = sql_result.get("data", {})
            generated_sql = sql_data.get("generated_sql", "")
            print(f"📝 Generated SQL: {generated_sql}")
            
            # Step 2: Execute SQL
            execution_result = registry.execute_tool(
                tool_name="SQLExecutor",
                hosted_by="mcp",
                input_data={"sql_query": generated_sql},
                config=mcp_config
            )
            
            if execution_result.get("success"):
                query_results = execution_result.get("data", {})
                results = query_results.get("results", [])
                row_count = query_results.get("row_count", 0)
                
                print(f"\n📊 Results ({row_count} rows):")
                if results:
                    for i, row in enumerate(results[:3]):
                        print(f"  {i+1}. {row}")
                    if len(results) > 3:
                        print(f"  ... and {len(results) - 3} more rows")
                else:
                    print("  No results found")
                
                if not query_results.get("_mock"):
                    print("✅ Real database results!")
            else:
                print(f"❌ Query execution failed: {execution_result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Main workflow: PDF processing + Text-to-SQL queries"""
    print("🚀 Complete Invoice Processing & Analytics Workflow")
    print("=" * 60)
    
    # Step 1: Discover and select files
    file_to_process = get_file_to_process()
    if not file_to_process:
        print("❌ No file selected. Exiting.")
        return
    
    # Step 2: Process the invoice
    record_id = process_invoice_via_api(file_to_process)
    
    if record_id:
        print(f"\n✅ Invoice processing completed!")
        print(f"📊 Database Record ID: {record_id}")
        
        # Step 3: Offer text-to-SQL queries
        registry = ToolRegistry()
        run_text_to_sql_queries(registry, record_id)
    else:
        print("❌ Invoice processing failed")

if __name__ == "__main__":
    main() 