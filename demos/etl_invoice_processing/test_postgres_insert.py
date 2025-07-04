#!/usr/bin/env python3
"""
Test PostgresInsert tool with new invoice_json table
"""

import os
import sys
import json
import requests

# Add the parent directory to the path to import memra
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from memra.tool_registry import ToolRegistry

def test_postgres_insert():
    """Test PostgresInsert tool with sample invoice data"""
    
    # Sample invoice data that includes due date
    sample_invoice_data = {
        "headerSection": {
            "vendorName": "Test Vendor Inc.",
            "subtotal": 1500.00
        },
        "billingDetails": {
            "invoiceNumber": "TEST-001",
            "invoiceDate": "2024-12-01",
            "dueDate": "2024-12-31"  # This was previously lost!
        },
        "chargesSummary": {
            "document_total": 1695.00,
            "secondary_tax": 195.00,
            "lineItemsBreakdown": [
                {
                    "description": "Test Service",
                    "quantity": 1,
                    "unit_price": 1500.00,
                    "amount": 1500.00
                }
            ]
        }
    }
    
    print("🔧 Testing PostgresInsert tool with new invoice_json table...")
    print(f"📄 Sample data includes due date: {sample_invoice_data['billingDetails']['dueDate']}")
    
    # Test input data
    input_data = {
        "invoice_data": sample_invoice_data,
        "table_name": "invoice_json"
    }
    
    # Execute the tool
    try:
        registry = ToolRegistry()
        result = registry.execute_tool(
            tool_name="PostgresInsert",
            hosted_by="mcp",
            input_data=input_data,
            config={
                "bridge_url": "http://localhost:8081",
                "bridge_secret": "test-secret-for-development"
            }
        )
        
        print(f"📊 Result: {json.dumps(result, indent=2)}")
        
        if result.get("success"):
            print("✅ PostgresInsert executed successfully!")
            print(f"📝 Record ID: {result['data']['record_id']}")
            print(f"📊 JSON size: {result['data']['inserted_data']['raw_json_size']} bytes")
            print(f"🔑 JSON keys: {result['data']['inserted_data']['json_keys']}")
            
            # Now let's verify the data was stored correctly
            print("\n🔍 Verifying stored data...")
            verify_stored_data(result['data']['record_id'])
            
        else:
            print(f"❌ PostgresInsert failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error executing PostgresInsert: {str(e)}")

def verify_stored_data(record_id):
    """Verify that the data was stored correctly in the database"""
    
    # Query to get the stored JSON
    query = f"SELECT raw_json FROM invoice_json WHERE id = {record_id}"
    
    try:
        registry = ToolRegistry()
        result = registry.execute_tool(
            tool_name="SQLExecutor",
            hosted_by="mcp",
            input_data={"sql_query": query},
            config={
                "bridge_url": "http://localhost:8081",
                "bridge_secret": "test-secret-for-development"
            }
        )
        
        if result.get("success") and result["data"]["results"]:
            stored_json = result["data"]["results"][0]["raw_json"]
            print(f"📄 Stored JSON: {json.dumps(stored_json, indent=2)}")
            
            # Check if due date is preserved
            due_date = stored_json.get("billingDetails", {}).get("dueDate")
            if due_date:
                print(f"✅ Due date preserved: {due_date}")
            else:
                print("❌ Due date not found in stored data")
                
        else:
            print(f"❌ Failed to retrieve stored data: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error verifying stored data: {str(e)}")

if __name__ == "__main__":
    test_postgres_insert() 