#!/usr/bin/env python3
"""
Check database after workflow
"""

import requests
import json

def check_database_after():
    """Show table contents after workflow"""
    
    bridge_url = "http://localhost:8081"
    bridge_secret = "test-secret-for-development"
    
    headers = {
        "Content-Type": "application/json",
        "X-Bridge-Secret": bridge_secret
    }
    
    print("📊 Database contents AFTER workflow:")
    payload = {
        "tool_name": "SQLExecutor",
        "input_data": {
            "sql_query": "SELECT * FROM invoices ORDER BY id;"
        }
    }
    
    response = requests.post(f"{bridge_url}/execute_tool", json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            data = result["data"]
            print(f"Query: {data['query']}")
            print(f"Total Rows: {data['row_count']}")
            print("\nAll records:")
            for i, row in enumerate(data['results'], 1):
                print(f"\n{i}. ID: {row['id']}")
                print(f"   Invoice Number: {row['invoice_number']}")
                print(f"   Vendor: {row['vendor_name']}")
                print(f"   Date: {row['invoice_date']}")
                print(f"   Amount: ${row['total_amount']}")
                print(f"   Status: {row['status']}")
                print(f"   Created: {row['created_at']}")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print(f"HTTP Error: {response.status_code}")

if __name__ == "__main__":
    check_database_after() 