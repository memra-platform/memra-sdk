#!/usr/bin/env python3
"""
Complete Text-to-SQL System
Demonstrates the full pipeline: English Question → Schema → SQL Generation → Execution → Real Results
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import memra
sys.path.insert(0, str(Path(__file__).parent.parent))

from memra import ExecutionEngine, Agent, Tool

def create_text_to_sql_system():
    """Create a complete text-to-SQL system with real database integration"""
    
    # Initialize execution engine
    engine = ExecutionEngine()
    
    # Schema Extraction Agent
    schema_agent = Agent(
        role="Database Schema Analyst",
        job="Extract and analyze database schemas",
        output_key="schema_data",
        tools=[
            Tool(
                name="DatabaseQueryTool",
                hosted_by="memra",
                description="Query database schemas and structure"
            )
        ]
    )
    
    # SQL Generation Agent  
    sql_generator_agent = Agent(
        role="SQL Generator",
        job="Convert natural language to SQL queries",
        output_key="generated_sql",
        tools=[
            Tool(
                name="TextToSQLGenerator",
                hosted_by="mcp",
                description="Generate SQL from natural language questions",
                config={
                    "bridge_url": "http://localhost:8081",
                    "bridge_secret": "test-secret-for-development"
                }
            )
        ]
    )
    
    # SQL Execution Agent
    sql_executor_agent = Agent(
        role="SQL Executor",
        job="Execute SQL queries and return results",
        output_key="query_results",
        tools=[
            Tool(
                name="SQLExecutor", 
                hosted_by="mcp",
                description="Execute SQL queries against PostgreSQL database",
                config={
                    "bridge_url": "http://localhost:8081",
                    "bridge_secret": "test-secret-for-development"
                }
            )
        ]
    )
    
    return engine, schema_agent, sql_generator_agent, sql_executor_agent

def extract_database_schema(engine, schema_agent):
    """Extract the database schema for context"""
    print("🔍 Extracting database schema...")
    
    schema_task = {
        "task": "Extract the complete schema for the invoices table including column names, types, and sample data",
        "table_name": "invoices",
        "include_sample_data": True
    }
    
    result = engine.execute_task(schema_agent, schema_task)
    
    if result.get("success"):
        print(f"✅ Schema extracted successfully ({result.get('execution_time', 0):.1f}s)")
        schema_data = result.get("result", {})
        
        # Display schema info
        if "schema" in schema_data:
            print("\n📊 Database Schema:")
            schema = schema_data["schema"]
            for table_name, table_info in schema.items():
                print(f"  Table: {table_name}")
                if "columns" in table_info:
                    for col in table_info["columns"]:
                        print(f"    - {col['name']} ({col['type']})")
        
        return schema_data
    else:
        print(f"❌ Schema extraction failed: {result.get('error', 'Unknown error')}")
        return {}

def generate_sql_from_question(engine, sql_generator_agent, question, schema_info):
    """Generate SQL from natural language question"""
    print(f"\n🤖 Generating SQL for: '{question}'")
    
    sql_generation_task = {
        "question": question,
        "schema_info": schema_info,
        "context": "Generate SQL query for invoice database analysis"
    }
    
    result = engine.execute_task(sql_generator_agent, sql_generation_task)
    
    if result.get("success"):
        print(f"✅ SQL generated successfully ({result.get('execution_time', 0):.1f}s)")
        sql_data = result.get("result", {})
        
        generated_sql = sql_data.get("generated_sql", "")
        print(f"\n📝 Generated SQL:")
        print(f"   {generated_sql}")
        
        return generated_sql
    else:
        print(f"❌ SQL generation failed: {result.get('error', 'Unknown error')}")
        return None

def execute_sql_query(engine, sql_executor_agent, sql_query):
    """Execute the generated SQL query"""
    print(f"\n⚡ Executing SQL query...")
    
    execution_task = {
        "sql_query": sql_query,
        "timeout": 30
    }
    
    result = engine.execute_task(sql_executor_agent, execution_task)
    
    if result.get("success"):
        print(f"✅ SQL executed successfully ({result.get('execution_time', 0):.1f}s)")
        query_results = result.get("result", {})
        
        # Display results
        results = query_results.get("results", [])
        row_count = query_results.get("row_count", 0)
        
        print(f"\n📋 Query Results ({row_count} rows):")
        if results:
            # Display first few results
            for i, row in enumerate(results[:5]):
                print(f"  Row {i+1}: {row}")
            
            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more rows")
        else:
            print("  No results found")
        
        return query_results
    else:
        print(f"❌ SQL execution failed: {result.get('error', 'Unknown error')}")
        return {}

def run_text_to_sql_query(engine, schema_agent, sql_generator_agent, sql_executor_agent, question):
    """Run the complete text-to-SQL pipeline"""
    print(f"\n{'='*60}")
    print(f"🎯 Processing Question: {question}")
    print(f"{'='*60}")
    
    # Step 1: Extract schema (cached after first run)
    if not hasattr(run_text_to_sql_query, 'cached_schema'):
        run_text_to_sql_query.cached_schema = extract_database_schema(engine, schema_agent)
    
    schema_info = run_text_to_sql_query.cached_schema
    
    # Step 2: Generate SQL
    sql_query = generate_sql_from_question(engine, sql_generator_agent, question, schema_info)
    
    if not sql_query:
        return None
    
    # Step 3: Execute SQL
    results = execute_sql_query(engine, sql_executor_agent, sql_query)
    
    return {
        "question": question,
        "sql_query": sql_query,
        "results": results
    }

def main():
    """Main function to demonstrate the complete text-to-SQL system"""
    print("🚀 Starting Complete Text-to-SQL System")
    print("=" * 60)
    
    # Create the system
    engine, schema_agent, sql_generator_agent, sql_executor_agent = create_text_to_sql_system()
    
    # Example questions to test
    test_questions = [
        "Show me all invoices from Air Liquide",
        "What is the total amount of all invoices?",
        "How many invoices do we have in the database?",
        "Show me the most recent 5 invoices",
        "What is the average invoice amount?",
    ]
    
    print("📝 Available test questions:")
    for i, question in enumerate(test_questions, 1):
        print(f"  {i}. {question}")
    
    print("\n" + "="*60)
    
    # Interactive mode
    while True:
        print("\n🤔 What would you like to know about the invoices?")
        print("   (Enter a question, number 1-5 for examples, or 'quit' to exit)")
        
        user_input = input("\n❓ Your question: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        # Check if it's a number for example questions
        if user_input.isdigit():
            question_num = int(user_input)
            if 1 <= question_num <= len(test_questions):
                question = test_questions[question_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(test_questions)}")
                continue
        else:
            question = user_input
        
        if not question:
            print("❌ Please enter a question")
            continue
        
        # Run the complete pipeline
        try:
            result = run_text_to_sql_query(
                engine, schema_agent, sql_generator_agent, sql_executor_agent, question
            )
            
            if result:
                print(f"\n✨ Query completed successfully!")
                
                # Check if results are real or mock
                results_data = result.get("results", {})
                if results_data.get("_mock"):
                    print("ℹ️  Note: Results are mocked (MCP bridge not fully connected)")
                else:
                    print("🎉 Real database results!")
            else:
                print("❌ Query failed")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Query interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 