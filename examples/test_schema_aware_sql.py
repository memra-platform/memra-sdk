#!/usr/bin/env python3
"""
Test script to verify schema-aware SQL generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memra import ExecutionEngine, Agent, Tool

def create_test_system():
    """Create a test system with schema-aware SQL generation"""
    
    # Create execution engine
    engine = ExecutionEngine()
    
    # Create schema agent
    schema_agent = Agent(
        role="database_schema_analyst", 
        job="Extract and analyze database schema information for SQL generation",
        output_key="schema_data",
        tools=[
            Tool(
                name="SchemaExtractor",
                hosted_by="memra",
                config={
                    "api_key": "memra-prod-2024-001"
                }
            )
        ]
    )
    
    # Create SQL generator agent with schema awareness
    sql_generator_agent = Agent(
        role="text_to_sql_converter",
        job="Convert natural language questions to SQL using database schema context",
        output_key="generated_sql",
        tools=[
            Tool(
                name="TextToSQLGenerator",
                hosted_by="mcp",
                config={
                    "mcp_bridge_url": "http://localhost:8081",
                    "bridge_secret": "test-secret-for-development"
                }
            )
        ]
    )
    
    return engine, schema_agent, sql_generator_agent

def test_schema_aware_sql_generation():
    """Test that SQL generation uses schema information"""
    print("🧪 Testing Schema-Aware SQL Generation")
    print("=" * 50)
    
    engine, schema_agent, sql_generator_agent = create_test_system()
    
    # Step 1: Extract schema
    print("\n1️⃣ Extracting database schema...")
    schema_task = {
        "task": "Extract the complete schema for the invoices table",
        "table_name": "invoices",
        "include_sample_data": True
    }
    
    schema_result = engine.execute_task(schema_agent, schema_task)
    
    if not schema_result.get("success"):
        print(f"❌ Schema extraction failed: {schema_result.get('error')}")
        return
    
    schema_data = schema_result.get("result", {})
    print(f"✅ Schema extracted successfully")
    
    # Display schema info
    if "schema" in schema_data:
        print("\n📊 Database Schema:")
        schema = schema_data["schema"]
        for table_name, table_info in schema.items():
            print(f"  Table: {table_name}")
            if "columns" in table_info:
                for col in table_info["columns"]:
                    print(f"    - {col['name']} ({col['type']})")
    
    # Step 2: Test various questions with schema context
    test_questions = [
        "Show me all invoices from Air Liquide",
        "What is the total amount of all invoices?", 
        "How many invoices do we have?",
        "Show me the 5 most recent invoices",
        "What is the average invoice amount?",
        "Count invoices from Microsoft"
    ]
    
    print(f"\n2️⃣ Testing SQL generation with schema context...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Test {i}: {question} ---")
        
        sql_task = {
            "question": question,
            "schema_info": schema_data,
            "context": "Generate SQL using provided schema information"
        }
        
        sql_result = engine.execute_task(sql_generator_agent, sql_task)
        
        if sql_result.get("success"):
            sql_data = sql_result.get("result", {})
            generated_sql = sql_data.get("generated_sql", "")
            explanation = sql_data.get("explanation", "")
            confidence = sql_data.get("confidence", "unknown")
            schema_used = sql_data.get("schema_used", {})
            
            print(f"✅ SQL Generated (confidence: {confidence})")
            print(f"   Query: {generated_sql}")
            print(f"   Explanation: {explanation}")
            
            if schema_used:
                columns_used = schema_used.get("columns", [])
                print(f"   Schema columns available: {', '.join(columns_used)}")
        else:
            print(f"❌ SQL generation failed: {sql_result.get('error')}")
    
    print(f"\n✨ Schema-aware SQL generation test completed!")

def main():
    """Main function"""
    try:
        test_schema_aware_sql_generation()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main() 