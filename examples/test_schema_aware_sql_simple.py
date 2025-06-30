#!/usr/bin/env python3
"""
Simple test to verify schema-aware SQL generation using the complete system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.complete_text_to_sql_system import create_text_to_sql_system, run_text_to_sql_query

def test_schema_awareness():
    """Test that SQL generation properly uses schema information"""
    print("🧪 Testing Schema-Aware SQL Generation")
    print("=" * 50)
    
    # Create the complete system
    engine, schema_agent, sql_generator_agent, sql_executor_agent = create_text_to_sql_system()
    
    # Test questions that should generate different SQL based on schema
    test_questions = [
        "Show me all invoices from Air Liquide",
        "What is the total amount of all invoices?",
        "How many invoices do we have?",
        "Show me the 3 most recent invoices",
        "What is the average invoice amount?"
    ]
    
    print("\n🔍 Testing schema-aware SQL generation...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Test {i}: {question} ---")
        
        try:
            result = run_text_to_sql_query(
                engine, schema_agent, sql_generator_agent, sql_executor_agent, question
            )
            
            if result:
                sql_query = result.get("sql_query", "")
                print(f"✅ Generated SQL: {sql_query}")
                
                # Check if the SQL looks schema-aware
                if "total_amount" in sql_query or "invoice_date" in sql_query or "vendor_name" in sql_query:
                    print("🎯 SQL appears to use actual column names from schema!")
                else:
                    print("⚠️  SQL might not be using schema information")
            else:
                print("❌ SQL generation failed")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n✨ Schema awareness test completed!")

def main():
    """Main function"""
    try:
        test_schema_awareness()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main() 