#!/usr/bin/env python3
"""
Simple Text-to-SQL Interface
Direct connection to MCP bridge for asking questions about invoices
"""

import requests
import json

def ask_question(question):
    """Ask a question and get SQL + results"""
    bridge_url = "http://localhost:8081"
    bridge_secret = "test-secret-for-development"
    
    # Simulated schema info (in real system this would come from schema extraction)
    schema_info = {
        "schema": {
            "invoices": {
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": "vendor_name", "type": "text"},
                    {"name": "invoice_number", "type": "text"},
                    {"name": "invoice_date", "type": "date"},
                    {"name": "total_amount", "type": "numeric"},
                    {"name": "tax_amount", "type": "numeric"},
                    {"name": "line_items", "type": "jsonb"},
                    {"name": "status", "type": "text"}
                ]
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Bridge-Secret": bridge_secret
    }
    
    print(f"\n🤖 Processing: {question}")
    print("-" * 50)
    
    # Step 1: Generate SQL
    sql_request = {
        "tool_name": "TextToSQLGenerator",
        "input_data": {
            "question": question,
            "schema_info": schema_info
        }
    }
    
    try:
        response = requests.post(f"{bridge_url}/execute_tool", json=sql_request, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ SQL generation failed: HTTP {response.status_code}")
            return
        
        result = response.json()
        if not result.get("success"):
            print(f"❌ SQL generation failed: {result.get('error')}")
            return
        
        data = result.get("data", {})
        sql_query = data.get("generated_sql", "")
        explanation = data.get("explanation", "")
        
        print(f"📝 Generated SQL: {sql_query}")
        print(f"💡 Explanation: {explanation}")
        
        # Step 2: Execute SQL
        exec_request = {
            "tool_name": "SQLExecutor",
            "input_data": {
                "sql_query": sql_query
            }
        }
        
        response = requests.post(f"{bridge_url}/execute_tool", json=exec_request, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ SQL execution failed: HTTP {response.status_code}")
            return
        
        result = response.json()
        if not result.get("success"):
            print(f"❌ SQL execution failed: {result.get('error')}")
            return
        
        exec_data = result.get("data", {})
        results = exec_data.get("results", [])
        row_count = exec_data.get("row_count", 0)
        
        print(f"\n📊 Results ({row_count} rows):")
        if results:
            # Show first 10 results
            for i, row in enumerate(results[:10], 1):
                print(f"  {i}. {row}")
            
            if len(results) > 10:
                print(f"  ... and {len(results) - 10} more rows")
        else:
            print("  No results found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Interactive text-to-SQL interface"""
    print("🚀 Simple Text-to-SQL Interface")
    print("=" * 50)
    print("Ask questions about your invoice database!")
    print("Examples:")
    print("  • Show me all invoices from Air Liquide")
    print("  • What is the total amount of all invoices?")
    print("  • How many invoices do we have?")
    print("  • Show me the 5 most recent invoices")
    print("  • What is the average invoice amount?")
    print("\nType 'quit' to exit")
    print("=" * 50)
    
    # Check if MCP bridge is running
    try:
        response = requests.get("http://localhost:8081/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Bridge server is running")
        else:
            print("❌ MCP Bridge server is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to MCP Bridge server: {str(e)}")
        print("💡 Make sure to start the MCP bridge server first:")
        print("   source /Users/tarpus/miniconda3/bin/activate memra && \\")
        print("   export MCP_POSTGRES_URL=\"postgresql://tarpus@localhost:5432/memra_invoice_db\" && \\")
        print("   export MCP_BRIDGE_SECRET=\"test-secret-for-development\" && \\")
        print("   python3 mcp_bridge_server.py")
        return
    
    while True:
        try:
            question = input("\n❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not question:
                print("Please enter a question")
                continue
            
            ask_question(question)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 