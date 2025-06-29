#!/usr/bin/env python3
"""
Simple interactive script to ask questions about invoices
"""

import requests
import json

def ask_question(question):
    """Ask a question and get SQL + results"""
    bridge_url = "http://localhost:8081"
    bridge_secret = "test-secret-for-development"
    
    # No hard-coded schema - let the server fetch it dynamically
    schema_info = {}
    
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
        response = requests.post(f"{bridge_url}/execute_tool", json=sql_request, headers=headers, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ SQL generation failed: HTTP {response.status_code}")
            return
        
        result = response.json()
        if not result.get("success"):
            print(f"❌ SQL generation failed: {result.get('error')}")
            return
        
        data = result.get("data", {})
        sql_query = data.get("generated_sql", "")
        method = data.get("method", "unknown")
        
        # Check if SQL is incomplete
        if not sql_query or sql_query.strip() == "SELECT" or len(sql_query.strip()) < 10:
            print(f"❌ Generated incomplete SQL: '{sql_query}'")
            print("💡 Try rephrasing your question more simply")
            return
        
        print(f"📝 Generated SQL: {sql_query}")
        print(f"💡 Method: {method}")
        
        # Step 2: Execute SQL
        exec_request = {
            "tool_name": "SQLExecutor",
            "input_data": {
                "sql_query": sql_query
            }
        }
        
        response = requests.post(f"{bridge_url}/execute_tool", json=exec_request, headers=headers, timeout=60)
        
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
            # Show first 5 results
            for i, row in enumerate(results[:5], 1):
                print(f"  {i}. {row}")
            
            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more rows")
        else:
            print("  No results found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Interactive question asking"""
    print("🎯 Invoice Question Assistant")
    print("=" * 50)
    print("Ask questions about your invoices in natural language!")
    print("Examples:")
    print("  - Show me all invoices from Air Liquide")
    print("  - Find invoices with amounts greater than 1000")
    print("  - What is the total amount of all invoices?")
    print("  - How many invoices do we have?")
    print("\nType 'quit' to exit")
    
    while True:
        print("\n" + "="*50)
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            print("Please enter a question")
            continue
        
        ask_question(question)

if __name__ == "__main__":
    main() 