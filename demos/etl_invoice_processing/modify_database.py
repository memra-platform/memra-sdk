#!/usr/bin/env python3
"""
Modify database through MCP bridge
"""

import requests
import json

def modify_database():
    """Remove constraint and show table contents"""
    
    bridge_url = "http://localhost:8081"
    bridge_secret = "test-secret-for-development"
    
    headers = {
        "Content-Type": "application/json",
        "X-Bridge-Secret": bridge_secret
    }
    
    print("🔧 Modifying database through MCP bridge...")
    
    # 1. Show current table contents
    print("\n📊 Current table contents:")
    payload = {
        "tool_name": "SQLExecutor",
        "input_data": {
            "sql_query": "SELECT * FROM invoices;"
        }
    }
    
    response = requests.post(f"{bridge_url}/execute_tool", json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result["data"]
            print(f"Query: {data['query']}")
            print(f"Rows: {data['row_count']}")
            for row in data['results']:
                print(f"  {row}")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print(f"HTTP Error: {response.status_code}")
    
    # 2. Remove the unique constraint
    print("\n🔧 Removing unique constraint on invoice_number...")
    payload = {
        "tool_name": "SQLExecutor",
        "input_data": {
            "sql_query": "ALTER TABLE invoices DROP CONSTRAINT IF EXISTS invoices_invoice_number_key;"
        }
    }
    
    response = requests.post(f"{bridge_url}/execute_tool", json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ Constraint removed successfully!")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print(f"HTTP Error: {response.status_code}")

if __name__ == "__main__":
    modify_database() 