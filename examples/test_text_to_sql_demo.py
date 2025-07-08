#!/usr/bin/env python3
"""
Text-to-SQL Demo Script
Automatically demonstrates the complete pipeline without user interaction
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import memra
sys.path.insert(0, str(Path(__file__).parent.parent))

from memra.tool_registry import ToolRegistry

def test_text_to_sql_pipeline():
    """Test the complete text-to-SQL pipeline using tool registry directly"""
    print("🚀 Starting Text-to-SQL Demo")
    print("=" * 60)
    
    # Initialize tool registry
    registry = ToolRegistry()
    
    # MCP bridge configuration
    mcp_config = {
        "bridge_url": "http://localhost:8081",
        "bridge_secret": "test-secret-for-development"
    }
    
    # Test questions
    test_questions = [
        "Show me all invoices from Air Liquide",
        "What is the total amount of all invoices?", 
        "How many invoices do we have in the database?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"🎯 Test {i}: {question}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Extract schema (using Memra API)
            print("🔍 Step 1: Extracting database schema...")
            schema_result = registry.execute_tool(
                tool_name="DatabaseQueryTool",
                hosted_by="memra",
                input_data={
                    "task": "Extract the complete schema for the invoices table",
                    "table_name": "invoices"
                }
            )
            
            if schema_result.get("success"):
                print(f"✅ Schema extracted")
                schema_data = schema_result.get("data", {})
            else:
                print(f"❌ Schema extraction failed: {schema_result.get('error')}")
                # Use mock schema for demo
                schema_data = {"tables": ["invoices"]}
                print("📝 Using mock schema for demo")
            
            # Step 2: Generate SQL (using MCP bridge)
            print(f"\n🤖 Step 2: Generating SQL for: '{question}'")
            sql_result = registry.execute_tool(
                tool_name="TextToSQLGenerator",
                hosted_by="mcp",
                input_data={
                    "question": question,
                    "schema_info": schema_data
                },
                config=mcp_config
            )
            
            if sql_result.get("success"):
                print(f"✅ SQL generated")
                sql_data = sql_result.get("data", {})
                generated_sql = sql_data.get("generated_sql", "")
                print(f"📝 Generated SQL: {generated_sql}")
                
                # Check if it's real or mock
                if sql_data.get("_mock"):
                    print("ℹ️  Note: SQL generation is mocked (MCP bridge not fully connected)")
                else:
                    print("🎉 Real SQL generation!")
            else:
                print(f"❌ SQL generation failed: {sql_result.get('error')}")
                continue
            
            # Step 3: Execute SQL (using MCP bridge)
            print(f"\n⚡ Step 3: Executing SQL query...")
            execution_result = registry.execute_tool(
                tool_name="SQLExecutor",
                hosted_by="mcp",
                input_data={
                    "sql_query": generated_sql
                },
                config=mcp_config
            )
            
            if execution_result.get("success"):
                print(f"✅ SQL executed")
                query_results = execution_result.get("data", {})
                
                # Display results
                results = query_results.get("results", [])
                row_count = query_results.get("row_count", 0)
                
                print(f"\n📋 Query Results ({row_count} rows):")
                if results:
                    # Display first few results
                    for j, row in enumerate(results[:3]):
                        print(f"  Row {j+1}: {row}")
                    
                    if len(results) > 3:
                        print(f"  ... and {len(results) - 3} more rows")
                else:
                    print("  No results found")
                
                # Check if results are real or mock
                if query_results.get("_mock"):
                    print("ℹ️  Note: Results are mocked (MCP bridge not fully connected)")
                else:
                    print("🎉 Real database results!")
                    
            else:
                print(f"❌ SQL execution failed: {execution_result.get('error')}")
            
            print(f"\n✨ Test {i} completed!")
            
        except Exception as e:
            print(f"\n❌ Test {i} failed with error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("🏁 Demo completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_text_to_sql_pipeline() 