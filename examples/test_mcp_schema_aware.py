#!/usr/bin/env python3
"""
Direct test of MCP bridge server schema-aware SQL generation
"""

import requests
import json

def test_schema_aware_sql():
    """Test schema-aware SQL generation directly via MCP bridge"""
    print("🧪 Testing Schema-Aware SQL Generation (Direct MCP)")
    print("=" * 55)
    
    bridge_url = "http://localhost:8081"
    bridge_secret = "test-secret-for-development"
    
    # First, get the schema information (simulated)
    schema_info = {
        "schema": {
            "invoices": {
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": "vendor_name", "type": "text"},
                    {"name": "invoice_number", "type": "text"},
                    {"name": "invoice_date", "type": "date"},
                    {"name": "total_amount", "type": "numeric"},
                    {"name": "line_items", "type": "jsonb"}
                ]
            }
        }
    }
    
    # Test questions
    test_questions = [
        "Show me all invoices from Air Liquide",
        "What is the total amount of all invoices?",
        "How many invoices do we have?",
        "Show me the 3 most recent invoices",
        "What is the average invoice amount?",
        "Count invoices from Microsoft"
    ]
    
    print(f"\n🔍 Testing {len(test_questions)} questions with schema context...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Test {i}: {question} ---")
        
        # Prepare request data
        request_data = {
            "tool_name": "TextToSQLGenerator",
            "input_data": {
                "question": question,
                "schema_info": schema_info
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Bridge-Secret": bridge_secret
        }
        
        try:
            # Make request to MCP bridge
            response = requests.post(
                f"{bridge_url}/execute_tool",
                json=request_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    data = result.get("data", {})
                    generated_sql = data.get("generated_sql", "")
                    explanation = data.get("explanation", "")
                    confidence = data.get("confidence", "unknown")
                    schema_used = data.get("schema_used", {})
                    
                    print(f"✅ SQL Generated (confidence: {confidence})")
                    print(f"   Query: {generated_sql}")
                    print(f"   Explanation: {explanation}")
                    
                    if schema_used:
                        columns = schema_used.get("columns", [])
                        print(f"   Schema columns used: {', '.join(columns)}")
                    
                    # Check if SQL uses actual column names
                    schema_columns = ["vendor_name", "total_amount", "invoice_date", "invoice_number"]
                    uses_schema = any(col in generated_sql for col in schema_columns)
                    
                    if uses_schema:
                        print("🎯 SQL appears to use actual schema column names!")
                    else:
                        print("⚠️  SQL might not be using schema information")
                        
                else:
                    print(f"❌ SQL generation failed: {result.get('error')}")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
    
    print(f"\n✨ Schema-aware SQL generation test completed!")

def main():
    """Main function"""
    try:
        # Check if MCP bridge is running
        response = requests.get("http://localhost:8081/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Bridge server is running")
            test_schema_aware_sql()
        else:
            print("❌ MCP Bridge server is not responding")
    except Exception as e:
        print(f"❌ Cannot connect to MCP Bridge server: {str(e)}")
        print("💡 Make sure the MCP bridge server is running on port 8081")

if __name__ == "__main__":
    main() 