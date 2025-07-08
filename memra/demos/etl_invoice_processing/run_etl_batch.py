#!/usr/bin/env python3
"""
Run ETL workflow in batch mode
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import memra
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memra import Agent, Department, LLM, check_api_health, get_api_status
from memra.execution import ExecutionEngine
from etl_invoice_demo import etl_department, upload_file_to_api

# Set API key for authentication
os.environ['MEMRA_API_KEY'] = 'test-secret-for-development'
os.environ['MEMRA_API_URL'] = 'https://api.memra.co'

# Check API health
print("🔍 Checking Memra API status...")
api_status = get_api_status()
print(f"API Health: {'✅ Healthy' if api_status['api_healthy'] else '❌ Unavailable'}")

if not api_status['api_healthy']:
    print("❌ Cannot proceed - Memra API is not available")
    sys.exit(1)

# Process one invoice
invoice_path = "data/invoices/10352259401.PDF"  # Superior Propane invoice
print(f"\n📄 Processing invoice: {invoice_path}")

# Upload file to remote API
remote_path = upload_file_to_api(invoice_path)
if not remote_path:
    print("❌ Failed to upload file")
    sys.exit(1)

# Database connection info
connection = "postgresql://postgres:postgres@localhost:5433/local_workflow"

# Prepare input for department
input_data = {
    "file": remote_path,
    "file_path": invoice_path,
    "table_name": "invoices",
    "connection": connection,
    "sql_query": "SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'invoices' ORDER BY ordinal_position"
}

# Execute department
engine = ExecutionEngine()
result = engine.execute_department(etl_department, input_data)

if result.success:
    print("\n✅ ETL workflow completed successfully!")
    print(f"Data written to database: {result.data.get('write_confirmation', {})}")
else:
    print(f"\n❌ ETL workflow failed: {result.error}")