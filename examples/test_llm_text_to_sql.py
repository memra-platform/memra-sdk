#!/usr/bin/env python3
"""
Test script to verify LLM-based text-to-SQL generation
"""

import requests
import json
import time

def test_llm_text_to_sql():
    """Test the new LLM-based text-to-SQL generation"""
    bridge_url = "http://localhost:8081"
    bridge_secret = "test-secret-for-development"
    
    # Test questions to verify LLM vs pattern matching
    test_questions = [
        "Show me all invoices from Air Liquide",
        "What is the total amount of all invoices?",
        "How many invoices do we have?",
        "Show me the 3 most recent invoices",
        "What is the average invoice amount?",
        "Find invoices with amounts greater than 1000",  # This should test LLM capabilities
        "Show me invoices from last month",  # This should test LLM capabilities
        "Which vendor has the highest total invoice amount?"  # Complex query for LLM
    ]
    
    # Schema info for context
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
    
    print("🧪 Testing LLM-based Text-to-SQL Generation")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🎯 Test {i}: {question}")
        print("-" * 50)
        
        # Prepare request
        request_data = {
            "tool_name": "TextToSQLGenerator",
            "input_data": {
                "question": question,
                "schema_info": schema_info
            }
        }
        
        try:
            start_time = time.time()
            
            # Make request to MCP bridge
            response = requests.post(
                f"{bridge_url}/execute_tool",
                json=request_data,
                headers=headers,
                timeout=30  # Longer timeout for LLM calls
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    data = result.get("data", {})
                    sql_query = data.get("generated_sql", "")
                    explanation = data.get("explanation", "")
                    confidence = data.get("confidence", "unknown")
                    method = data.get("method", "unknown")
                    
                    print(f"✅ Success ({duration:.1f}s)")
                    print(f"📝 SQL: {sql_query}")
                    print(f"💡 Method: {method}")
                    print(f"🎯 Confidence: {confidence}")
                    print(f"📖 Explanation: {explanation}")
                    
                    # Highlight if this is using LLM
                    if method == "llm":
                        print("🚀 Using LLM generation!")
                    elif method == "pattern_matching":
                        print("⚠️  Fallback to pattern matching")
                    
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print(f"\n✨ LLM Text-to-SQL testing completed!")

if __name__ == "__main__":
    test_llm_text_to_sql() 