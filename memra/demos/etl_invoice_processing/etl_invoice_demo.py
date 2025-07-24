#!/usr/bin/env python3
"""
ETL Invoice Processing Demo
Complete ETL workflow with database monitoring before and after
"""

import os
import sys
import time
import random
from pathlib import Path
from memra import Agent, Department, LLM, check_api_health, get_api_status
from memra.execution import ExecutionEngine, ExecutionTrace
from memra.demos.etl_invoice_processing.database_monitor_agent import create_simple_monitor_agent, get_monitoring_queries
import glob
import requests
import base64
import json

# Set API key for authentication - use environment variable if set, otherwise use development key
if not os.getenv('MEMRA_API_KEY'):
    os.environ['MEMRA_API_KEY'] = 'test-secret-for-development'
if not os.getenv('MEMRA_API_URL'):
    os.environ['MEMRA_API_URL'] = 'https://api.memra.co'

# Add the parent directory to the path so we can import memra
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Check for required API key
if not os.getenv("MEMRA_API_KEY"):
    print("❌ Error: MEMRA_API_KEY environment variable is required")
    print("Please set your API key: export MEMRA_API_KEY='test-secret-for-development'")
    print("Using local MCP bridge server")
    sys.exit(1)

# Set API configuration - using remote API for all operations including PDF processing
os.environ["MEMRA_API_URL"] = "https://api.memra.co"

# Store the remote API URL for PDF processing
REMOTE_API_URL = "https://api.memra.co"

# Define the specific 15 files to process
TARGET_FILES = [
    "10352259401.PDF",
    "10352259823.PDF", 
    "10352260169.PDF",
    "10352260417.PDF",
    "10352260599.PDF",
    "10352260912.PDF",
    "10352261134.PDF",
    "10352261563.PDF",
    "10352261647.PDF",
    "10352261720.PDF",
    "10352261811.PDF",
    "10352262025.PDF",
    "10352262454.PDF",
    "10352262702.PDF",
    "10352262884.PDF"
]

# Configuration for robust processing
PROCESSING_CONFIG = {
    "delay_between_files": 2.5,  # seconds
    "max_retries": 3,
    "retry_delay_base": 2,  # seconds
    "retry_delay_max": 30,  # seconds
    "timeout_seconds": 120,
    "rate_limit_delay": 5  # additional delay if rate limited
}

# Check API health before starting
print("🔍 Checking Memra API status...")
api_status = get_api_status()
print(f"API Health: {'✅ Healthy' if api_status['api_healthy'] else '❌ Unavailable'}")
print(f"API URL: {api_status['api_url']}")
print(f"Tools Available: {api_status['tools_available']}")

if not api_status['api_healthy']:
    print("❌ Cannot proceed - Memra API is not available")
    sys.exit(1)

# Define LLMs
default_llm = LLM(
    model="llama-3.2-11b-vision-preview",
    temperature=0.1,
    max_tokens=2000
)

parsing_llm = LLM(
    model="llama-3.2-11b-vision-preview", 
    temperature=0.0,
    max_tokens=4000
)

manager_llm = LLM(
    model="llama-3.2-11b-vision-preview",
    temperature=0.2,
    max_tokens=1500
)

# Define agents
pre_monitor_agent = create_simple_monitor_agent()
pre_monitor_agent.role = "Pre-ETL Database Monitor"

etl_agent = Agent(
    role="Data Engineer",
    job="Extract invoice schema from database",
    llm=default_llm,
    sops=[
        "Connect to database using provided connection string",
        "Generate SQL query: SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'invoices' ORDER BY ordinal_position",
        "Execute the generated SQL query using SQLExecutor tool",
        "Extract column names, types, and constraints from results",
        "Return schema as structured JSON with column information"
    ],
    systems=["Database"],
    tools=[
        {"name": "SQLExecutor", "hosted_by": "mcp", "input_keys": ["sql_query"]}
    ],
    input_keys=["connection", "table_name", "sql_query"],
    output_key="invoice_schema"
)

def convert_vision_response_to_extracted_data(vision_response: str) -> dict:
    """Convert vision model response to extracted_data format"""
    try:
        # Clean up the response - remove markdown code blocks if present
        if vision_response.startswith("```json"):
            vision_response = vision_response.replace("```json", "").replace("```", "").strip()
        
        # Parse the JSON response
        data = json.loads(vision_response)
        
        # Extract fields with fallback to different naming conventions
        invoice_number = (
            data.get("invoice_number") or 
            data.get("InvoiceNumber") or 
            data.get("invoiceNumber") or 
            ""
        )
        
        invoice_date = (
            data.get("invoice_date") or 
            data.get("InvoiceDate") or 
            data.get("invoiceDate") or 
            ""
        )
        
        # Convert date format if needed
        if invoice_date:
            if "/" in invoice_date and len(invoice_date.split("/")) == 3:
                parts = invoice_date.split("/")
                month, day, year = parts[0], parts[1], parts[2]
                if len(year) == 2:
                    year = "20" + year
                invoice_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        amount = (
            data.get("total_amount") or  # Add this - matches vision model output
            data.get("amount") or 
            data.get("InvoiceTotal") or 
            data.get("invoiceTotal") or 
            data.get("total") or 
            0
        )
        
        vendor_name = (
            data.get("vendor_name") or 
            data.get("VendorName") or 
            data.get("vendorName") or 
            data.get("Company") or 
            data.get("company") or 
            data.get("Vendor") or
            data.get("vendor") or
            ""
        )
        
        # If vendor not found, try to infer from the data
        if not vendor_name:
            # Check if items mention specific vendors
            items = data.get("Items") or data.get("Order") or data.get("items") or []
            for item in items:
                desc = item.get("Description", "").upper()
                if "PROPANE" in desc:
                    vendor_name = "Superior Propane"
                    break
        
        tax_amount = (
            data.get("tax_amount") or 
            data.get("TaxAmount") or 
            data.get("taxAmount") or 
            0
        )
        
        due_date = (
            data.get("due_date") or 
            data.get("DueDate") or 
            data.get("dueDate") or 
            ""
        )
        
        line_items = (
            data.get("line_items") or 
            data.get("Order") or 
            data.get("order") or 
            data.get("LineItems") or 
            data.get("lineItems") or 
            []
        )
        
        # Convert to expected format
        extracted_data = {
            "headerSection": {
                "vendorName": vendor_name,
                "subtotal": float(amount)
            },
            "billingDetails": {
                "invoiceNumber": invoice_number,
                "invoiceDate": invoice_date,
                "dueDate": due_date
            },
            "chargesSummary": {
                "document_total": float(amount),
                "secondary_tax": float(tax_amount),
                "lineItemsBreakdown": line_items
            },
            "status": "processed"
        }
        
        return extracted_data
        
    except Exception as e:
        print(f"⚠️  Error converting vision response: {e}")
        return {
            "headerSection": {"vendorName": "", "subtotal": 0.0},
            "billingDetails": {"invoiceNumber": "", "invoiceDate": "", "dueDate": ""},
            "chargesSummary": {"document_total": 0.0, "secondary_tax": 0.0, "lineItemsBreakdown": []},
            "status": "conversion_error"
        }

def pdf_processing_with_remote_api(agent, tool_results, **kwargs):
    """Custom processing function that switches to remote API for PDF processing"""
    print("\n[DEBUG] pdf_processing_with_remote_api function called!")
    print(f"[DEBUG] Agent: {agent.role}")
    print(f"[DEBUG] Tool results keys: {list(tool_results.keys())}")
    import json
    original_url = switch_to_remote_api_for_pdf()
    try:
        for tool_name, result_data in tool_results.items():
            if tool_name == "PDFProcessor":
                print("\n[DEBUG] Full PDFProcessor result_data:")
                try:
                    print(json.dumps(result_data, indent=2, default=str))
                except Exception as e:
                    print(f"[DEBUG] Could not serialize result_data: {e}")
                    print(result_data)
            if tool_name == "PDFProcessor" and result_data.get("success"):
                data = result_data.get("data", {})
                # Double-nested
                if "data" in data and isinstance(data["data"], dict):
                    inner_data = data["data"]
                    if "data" in inner_data and isinstance(inner_data["data"], dict):
                        actual_data = inner_data["data"]
                        extracted = actual_data.get("extracted_data", {})
                        vision_response = actual_data.get("vision_response")
                        if vision_response and (not extracted or not extracted.get("headerSection")):
                            converted_data = convert_vision_response_to_extracted_data(vision_response)
                            actual_data["extracted_data"] = converted_data
                            print(f"\n🔄 [PATCHED] Applied field mapping conversion to {tool_name} (double-nested)")
                            print(f"   Invoice #: {converted_data['billingDetails']['invoiceNumber']}")
                            print(f"   Amount: ${converted_data['chargesSummary']['document_total']}")
                        # Always print the raw JSON response
                        if vision_response:
                            print("\n📝 [AGENT 3] Vision Model Raw JSON Response:")
                            try:
                                parsed = json.loads(vision_response.replace('```json','').replace('```','').strip())
                                print(json.dumps(parsed, indent=2))
                            except Exception:
                                print(vision_response)
                    else:
                        extracted = inner_data.get("extracted_data", {})
                        vision_response = inner_data.get("vision_response")
                        if vision_response and (not extracted or not extracted.get("headerSection")):
                            converted_data = convert_vision_response_to_extracted_data(vision_response)
                            inner_data["extracted_data"] = converted_data
                            print(f"\n🔄 [PATCHED] Applied field mapping conversion to {tool_name} (single-nested)")
                            print(f"   Invoice #: {converted_data['billingDetails']['invoiceNumber']}")
                            print(f"   Amount: ${converted_data['chargesSummary']['document_total']}")
                        if vision_response:
                            print("\n📝 [AGENT 3] Vision Model Raw JSON Response:")
                            try:
                                parsed = json.loads(vision_response.replace('```json','').replace('```','').strip())
                                print(json.dumps(parsed, indent=2))
                            except Exception:
                                print(vision_response)
                else:
                    extracted = data.get("extracted_data", {})
                    vision_response = data.get("vision_response")
                    if vision_response and (not extracted or not extracted.get("headerSection")):
                        converted_data = convert_vision_response_to_extracted_data(vision_response)
                        data["extracted_data"] = converted_data
                        print(f"\n🔄 [PATCHED] Applied field mapping conversion to {tool_name} (direct)")
                        print(f"   Invoice #: {converted_data['billingDetails']['invoiceNumber']}")
                        print(f"   Amount: ${converted_data['chargesSummary']['document_total']}")
                    if vision_response:
                        print("\n📝 [AGENT 3] Vision Model Raw JSON Response:")
                        try:
                            parsed = json.loads(vision_response.replace('```json','').replace('```','').strip())
                            print(json.dumps(parsed, indent=2))
                        except Exception:
                            print(vision_response)
        print_vision_model_data(agent, tool_results)
        return tool_results
    finally:
        restore_api_url(original_url)

def fix_pdfprocessor_response(agent, result_data, **kwargs):
    """Custom processing function that calls remote API for PDF processing and prints JSON"""
    print(f"\n[DEBUG] fix_pdfprocessor_response called for {agent.role}")
    print(f"[DEBUG] Result data type: {type(result_data)}")
    print(f"[DEBUG] Result data: {result_data}")
    
    # Get the file path from the result_data (the execution engine passes input data here)
    file_path = result_data.get('file', '')
    print(f"[DEBUG] File path from result_data: {file_path}")
    
    if not file_path:
        print("❌ No file path provided in result_data")
        print(f"[DEBUG] Available keys in result_data: {list(result_data.keys())}")
        return result_data
    
    try:
        import requests
        import json
        import os
        import base64
        
        # Use the remote API for PDF processing
        api_url = "https://api.memra.co"
        api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")
        
        # Since the file is already uploaded and we have the remote path, use it directly
        print(f"🔍 Using remote file path: {file_path}")
        
        # Call the PDFProcessor with the remote path
        print(f"🔍 Calling PDFProcessor with remote path...")
        
        pdf_data = {
            "file_path": file_path
        }
        
        response = requests.post(
            f"{api_url}/tools/execute",
            json={
                "tool_name": "PDFProcessor",
                "parameters": pdf_data
            },
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code != 200:
            print(f"❌ PDFProcessor call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return result_data
        
        pdf_result = response.json()
        print(f"\n🎯 AGENT 3 - FULL PDFPROCESSOR RESPONSE:")
        print("=" * 60)
        print(json.dumps(pdf_result, indent=2, default=str))
        print("=" * 60)
        
        # Extract the vision response from the nested structure
        vision_response = None
        if pdf_result.get("success") and "data" in pdf_result:
            data = pdf_result["data"]
            
            # Check for nested data structure
            if isinstance(data, dict) and "data" in data:
                actual_data = data["data"]
                if "vision_response" in actual_data:
                    vision_response = actual_data["vision_response"]
            elif "vision_response" in data:
                vision_response = data["vision_response"]
        
        if vision_response:
            print(f"\n🎯 AGENT 3 - RAW VISION MODEL JSON:")
            print("=" * 60)
            print(vision_response)
            print("=" * 60)
            
            # Try to parse the JSON response
            try:
                # Clean up the response - remove markdown code blocks if present
                cleaned_response = vision_response
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response.replace("```", "").strip()
                
                parsed_data = json.loads(cleaned_response)
                print(f"\n✅ [AGENT 3] Successfully parsed JSON:")
                print(json.dumps(parsed_data, indent=2))
                
                # Convert to the expected format
                extracted_data = convert_vision_response_to_extracted_data(cleaned_response)
                
                # Debug vendor extraction
                print(f"\n🔍 [AGENT 3] Extracted vendor: '{extracted_data['headerSection']['vendorName']}'")
                print(f"   Invoice #: {extracted_data['billingDetails']['invoiceNumber']}")
                print(f"   Amount: ${extracted_data['chargesSummary']['document_total']}")
                
                # Update the result_data
                result_data = {
                    "success": True,
                    "data": {
                        "vision_response": vision_response,
                        "extracted_data": extracted_data
                    },
                    "_memra_metadata": {
                        "agent_role": agent.role,
                        "tools_real_work": ["PDFProcessor"],
                        "tools_mock_work": [],
                        "work_quality": "real"
                    }
                }
                
                return result_data
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw response: {vision_response}")
                return result_data
        else:
            print(f"❌ No vision_response found in PDFProcessor result")
            return result_data
            
    except Exception as e:
        print(f"❌ Error in PDF processing: {e}")
        return result_data

def direct_vision_processing(agent, result_data, **kwargs):
    """Direct vision model processing without using tools with retry logic"""
    print(f"\n[DEBUG] direct_vision_processing called for {agent.role}")
    print(f"[DEBUG] Result data type: {type(result_data)}")
    print(f"[DEBUG] Result data: {result_data}")
    print(f"[DEBUG] Kwargs: {kwargs}")
    
    # Get the file path from the input data - check kwargs['input'] first
    input_data = kwargs.get('input', {})
    file_path = input_data.get('file', '') or kwargs.get('file', '') or result_data.get('file', '')
    print(f"[DEBUG] File path: {file_path}")
    
    # Get the invoice schema from previous agent results
    results = kwargs.get('results', {})
    invoice_schema = results.get('invoice_schema', {})
    schema_results = invoice_schema.get('results', [])
    print(f"[DEBUG] Schema fields: {[col['column_name'] for col in schema_results]}")
    
    if not file_path:
        print("❌ No file path provided")
        return result_data
    
    # Retry logic for vision processing
    for attempt in range(PROCESSING_CONFIG["max_retries"] + 1):
        try:
            import requests
            import json
            import os
            import base64
            
            # Use the remote API for PDF processing
            api_url = "https://api.memra.co"
            api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")
            
            # Check if file is already a remote path
            if file_path.startswith('/uploads/'):
                print(f"✅ File already uploaded to remote API: {file_path}")
                remote_path = file_path
            else:
                # Local file - need to upload
                print(f"📤 Uploading file to remote API (attempt {attempt + 1})...")
                
                # Read the file and encode as base64
                with open(file_path, 'rb') as f:
                    file_content = f.read()
            
                file_b64 = base64.b64encode(file_content).decode('utf-8')
                
                # Prepare upload data
                upload_data = {
                    "filename": os.path.basename(file_path),
                    "content": file_b64,
                    "content_type": "application/pdf"
                }
                
                # Upload to remote API with timeout
                response = requests.post(
                    f"{api_url}/upload",
                    json=upload_data,
                    headers={
                        "X-API-Key": api_key,
                        "Content-Type": "application/json"
                    },
                    timeout=PROCESSING_CONFIG["timeout_seconds"]
                )
                
                if response.status_code != 200:
                    print(f"❌ Upload failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
                    # Check for rate limiting
                    if response.status_code == 429:
                        delay = PROCESSING_CONFIG["rate_limit_delay"] * (2 ** attempt)
                        print(f"⏳ Rate limited, waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        return result_data
                
                upload_result = response.json()
                if not upload_result.get("success"):
                    print(f"❌ Upload failed: {upload_result.get('error')}")
                    return result_data
                
                remote_path = upload_result["data"]["remote_path"]
                print(f"✅ File uploaded successfully")
                print(f"   Remote path: {remote_path}")
            
            # Now call the PDFProcessor with the remote path
            print(f"🔍 Calling PDFProcessor with remote path (attempt {attempt + 1})...")
            
            # Convert schema to format expected by PDFProcessor
            schema_for_pdf = None
            if schema_results:
                # Send the raw schema array - server now handles both formats
                schema_for_pdf = [
                    col for col in schema_results
                    if col["column_name"] not in ["id", "created_at", "updated_at", "status", "raw_json"]
                ]
                print(f"📋 Passing schema with {len(schema_for_pdf)} fields to PDFProcessor")
                print(f"📋 Schema fields: {[c['column_name'] for c in schema_for_pdf]}")
            
            response = requests.post(
                f"{api_url}/tools/execute",
                json={
                    "tool_name": "PDFProcessor",
                    "hosted_by": "memra",
                    "input_data": {
                        "file": remote_path,
                        "schema": schema_for_pdf
                    }
                },
                headers={
                    "X-API-Key": api_key,
                    "Content-Type": "application/json"
                },
                timeout=PROCESSING_CONFIG["timeout_seconds"]
            )
            
            if response.status_code != 200:
                print(f"❌ PDFProcessor call failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Check for rate limiting
                if response.status_code == 429:
                    delay = PROCESSING_CONFIG["rate_limit_delay"] * (2 ** attempt)
                    print(f"⏳ Rate limited, waiting {delay}s before retry...")
                    time.sleep(delay)
                    continue
                else:
                    return result_data
            
            pdf_result = response.json()
            print(f"\n🎯 AGENT 3 - FULL PDFPROCESSOR RESPONSE:")
            print("=" * 60)
            print(json.dumps(pdf_result, indent=2, default=str))
            print("=" * 60)
            
            # Extract the vision response from the nested structure
            vision_response = None
            if pdf_result.get("success") and "data" in pdf_result:
                data = pdf_result["data"]
                
                # Check for nested data structure
                if isinstance(data, dict) and "data" in data:
                    actual_data = data["data"]
                    if "vision_response" in actual_data:
                        vision_response = actual_data["vision_response"]
                elif "vision_response" in data:
                    vision_response = data["vision_response"]
            
            if vision_response:
                print(f"\n🎯 AGENT 3 - RAW VISION MODEL JSON:")
                print("=" * 60)
                print(vision_response)
                print("=" * 60)
                
                # Try to parse the JSON response
                try:
                    # Clean up the response - remove markdown code blocks if present
                    cleaned_response = vision_response
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()
                    elif cleaned_response.startswith("```"):
                        cleaned_response = cleaned_response.replace("```", "").strip()
                    
                    parsed_data = json.loads(cleaned_response)
                    print(f"\n✅ [AGENT 3] Successfully parsed JSON:")
                    print(json.dumps(parsed_data, indent=2))
                    
                    # Convert to the expected format
                    extracted_data = convert_vision_response_to_extracted_data(cleaned_response)
                    
                    # Debug vendor extraction
                    print(f"\n🔍 [AGENT 3] Extracted vendor: '{extracted_data['headerSection']['vendorName']}'")
                    print(f"   Invoice #: {extracted_data['billingDetails']['invoiceNumber']}")
                    print(f"   Amount: ${extracted_data['chargesSummary']['document_total']}")
                    
                    # Update the result_data
                    result_data = {
                        "success": True,
                        "data": {
                            "vision_response": vision_response,
                            "extracted_data": extracted_data
                        },
                        "_memra_metadata": {
                            "agent_role": agent.role,
                            "tools_real_work": ["PDFProcessor"],
                            "tools_mock_work": [],
                            "work_quality": "real"
                        }
                    }
                    
                    return result_data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"Raw response: {vision_response}")
                    
                    # Don't retry on JSON parsing errors
                    return result_data
            else:
                print(f"❌ No vision_response found in PDFProcessor result")
                
                # Retry if no vision response (might be temporary API issue)
                if attempt < PROCESSING_CONFIG["max_retries"]:
                    delay = PROCESSING_CONFIG["retry_delay_base"] * (2 ** attempt)
                    print(f"⏳ No vision response, waiting {delay}s before retry...")
                    time.sleep(delay)
                    continue
                else:
                    return result_data
                    
        except requests.exceptions.Timeout:
            print(f"⏰ Vision processing timeout (attempt {attempt + 1})")
            if attempt < PROCESSING_CONFIG["max_retries"]:
                delay = PROCESSING_CONFIG["retry_delay_base"] * (2 ** attempt)
                print(f"⏳ Waiting {delay}s before retry...")
                time.sleep(delay)
            continue
        except Exception as e:
            print(f"❌ Error in PDF processing (attempt {attempt + 1}): {e}")
            if attempt < PROCESSING_CONFIG["max_retries"]:
                delay = PROCESSING_CONFIG["retry_delay_base"] * (2 ** attempt)
                print(f"⏳ Waiting {delay}s before retry...")
                time.sleep(delay)
            continue
    
    print(f"❌ Failed to process vision after {PROCESSING_CONFIG['max_retries'] + 1} attempts")
    return result_data

# Create a new Agent 3 that bypasses the tool system
direct_vision_agent = Agent(
    role="Invoice Parser",
    job="Extract structured data from invoice PDF using vision model",
    llm=parsing_llm,
    sops=[
        "Load invoice PDF file",
        "Send to vision model for field extraction",
        "Print out the raw JSON data returned by vision model tools",
        "Validate extracted data against schema types",
        "Return structured invoice data"
    ],
    systems=["InvoiceStore"],
    tools=[],  # No tools - we'll do direct API calls in custom processing
    input_keys=["file", "invoice_schema"],
    output_key="invoice_data",
    custom_processing=direct_vision_processing
)

parser_agent = Agent(
    role="Invoice Parser",
    job="Extract structured data from invoice PDF using vision model",
    llm=parsing_llm,
    sops=[
        "Load invoice PDF file",
        "Send to vision model for field extraction",
        "Print out the raw JSON data returned by vision model tools",
        "Validate extracted data against schema types",
        "Return structured invoice data"
    ],
    systems=["InvoiceStore"],
    tools=[
        {"name": "PDFProcessor", "hosted_by": "memra", "input_keys": ["file_path"]}
    ],
    input_keys=["file", "invoice_schema"],
    output_key="invoice_data",
    custom_processing=pdf_processing_with_remote_api
)

def process_database_insertion(agent, tool_results, **kwargs):
    """Custom processing for Agent 4 to properly map invoice data to database format"""
    print(f"\n[DEBUG] process_database_insertion called for {agent.role}")
    
    # Get the invoice data from kwargs
    input_data = kwargs.get('input', {})
    results = kwargs.get('results', {})
    
    # Try to get invoice_data from various sources
    invoice_data = (
        results.get('invoice_data') or 
        input_data.get('invoice_data') or 
        kwargs.get('invoice_data', {})
    )
    
    print(f"[DEBUG] Invoice data type: {type(invoice_data)}")
    print(f"[DEBUG] Invoice data keys: {list(invoice_data.keys()) if isinstance(invoice_data, dict) else 'Not a dict'}")
    
    # Transform the data for database insertion
    if isinstance(invoice_data, dict):
        # Create the properly formatted data for database
        db_data = {}
        
        # Check if data is in the new format (headerSection, billingDetails, etc.)
        if 'headerSection' in invoice_data and 'billingDetails' in invoice_data:
            header = invoice_data.get('headerSection', {})
            billing = invoice_data.get('billingDetails', {})
            charges = invoice_data.get('chargesSummary', {})
            
            db_data = {
                'vendor_name': header.get('vendorName', ''),
                'invoice_number': billing.get('invoiceNumber', ''),
                'invoice_date': billing.get('invoiceDate', ''),
                'due_date': billing.get('dueDate', ''),
                'total_amount': charges.get('document_total', 0),
                'tax_amount': charges.get('secondary_tax', 0),
                'line_items': json.dumps(charges.get('lineItemsBreakdown', []))
            }
            
            print(f"\n💾 [AGENT 4] Prepared database record:")
            print(f"   vendor_name: '{db_data['vendor_name']}'")
            print(f"   invoice_number: '{db_data['invoice_number']}'")
            print(f"   invoice_date: '{db_data['invoice_date']}'")
            print(f"   total_amount: {db_data['total_amount']}")
            
        # Check if data is in the old format
        elif 'extracted_data' in invoice_data:
            extracted = invoice_data['extracted_data']
            if isinstance(extracted, dict):
                if 'headerSection' in extracted:
                    # Nested new format
                    header = extracted.get('headerSection', {})
                    billing = extracted.get('billingDetails', {})
                    charges = extracted.get('chargesSummary', {})
                    
                    db_data = {
                        'vendor_name': header.get('vendorName', ''),
                        'invoice_number': billing.get('invoiceNumber', ''),
                        'invoice_date': billing.get('invoiceDate', ''),
                        'due_date': billing.get('dueDate', ''),
                        'total_amount': charges.get('document_total', 0),
                        'tax_amount': charges.get('secondary_tax', 0),
                        'line_items': json.dumps(charges.get('lineItemsBreakdown', []))
                    }
                else:
                    # Old flat format
                    db_data = {
                        'vendor_name': extracted.get('vendor_name', ''),
                        'invoice_number': extracted.get('invoice_number', ''),
                        'invoice_date': extracted.get('invoice_date', ''),
                        'due_date': extracted.get('due_date', ''),
                        'total_amount': extracted.get('amount', extracted.get('total_amount', 0)),
                        'tax_amount': extracted.get('tax_amount', 0),
                        'line_items': json.dumps(extracted.get('line_items', []))
                    }
        
        # Update tool parameters with the transformed data
        for tool_name, result in tool_results.items():
            if tool_name == "PostgresInsert" and db_data:
                # Inject the properly formatted data into the tool parameters
                if 'parameters' not in result:
                    result['parameters'] = {}
                # Pass the data in the format expected by PostgresInsert tool
                result['parameters']['invoice_data'] = invoice_data  # Pass the original invoice_data
                result['parameters']['table_name'] = 'invoices'
                print(f"\n✅ [AGENT 4] Injected invoice_data into PostgresInsert parameters")
    
    # Call the original print function for debugging
    print_database_data(agent, tool_results, invoice_data)
    
    return tool_results

writer_agent = Agent(
    role="Data Entry Specialist", 
    job="Write validated invoice data to database",
    llm=default_llm,
    sops=[
        "Validate invoice data completeness",
        "Map fields to database columns using schema",
        "Print out the data being inserted into database",
        "Connect to database",
        "Insert record into invoices table",
        "Return confirmation with record ID"
    ],
    systems=["Database"],
    tools=[
        {"name": "DataValidator", "hosted_by": "mcp"},
        {"name": "PostgresInsert", "hosted_by": "mcp"}
    ],
    input_keys=["invoice_data", "invoice_schema"],
    output_key="write_confirmation",
    custom_processing=process_database_insertion
)

post_monitor_agent = create_simple_monitor_agent()
post_monitor_agent.role = "Post-ETL Database Monitor"

manager_agent = Agent(
    role="ETL Process Manager",
    job="Coordinate ETL pipeline and validate data integrity",
    llm=manager_llm,
    sops=[
        "Review pre-ETL database state",
        "Validate ETL process completion",
        "Compare pre and post database states",
        "Generate ETL summary report",
        "Flag any data quality issues"
    ],
    allow_delegation=True,
    output_key="etl_summary"
)

# Create ETL department
etl_department = Department(
    name="ETL Invoice Processing",
    mission="Complete end-to-end ETL process with comprehensive monitoring",
    agents=[pre_monitor_agent, etl_agent, direct_vision_agent, writer_agent, post_monitor_agent],
    manager_agent=manager_agent,
    workflow_order=[
        "Pre-ETL Database Monitor", 
        "Data Engineer", 
        "Invoice Parser", 
        "Data Entry Specialist",
        "Post-ETL Database Monitor"
    ],
    dependencies=["Database", "InvoiceStore"],
    execution_policy={
        "retry_on_fail": True,
        "max_retries": 2,
        "halt_on_validation_error": True,
        "timeout_seconds": 300
    },
    context={
        "company_id": "acme_corp",
        "fiscal_year": "2024",
        "mcp_bridge_url": "http://localhost:8081",
        "mcp_bridge_secret": "test-secret-for-development"
    }
)

def upload_file_to_api(file_path: str, api_url: str = "https://api.memra.co", max_retries: int = 3) -> str:
    """Upload a file to the remote API for vision-based PDF processing with retry logic"""
    
    for attempt in range(max_retries + 1):
        try:
            print(f"📤 Uploading {os.path.basename(file_path)} to remote API (attempt {attempt + 1}/{max_retries + 1})")
            print(f"   File path: {file_path}")
            
            # Read the file and encode as base64
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            file_b64 = base64.b64encode(file_content).decode('utf-8')
            
            # Prepare upload data
            upload_data = {
                "filename": os.path.basename(file_path),
                "content": file_b64,
                "content_type": "application/pdf"
            }
            
            # Upload to remote API
            api_key = os.getenv("MEMRA_API_KEY")
            response = requests.post(
                f"{api_url}/upload",
                json=upload_data,
                headers={
                    "X-API-Key": api_key,
                    "Content-Type": "application/json"
                },
                timeout=PROCESSING_CONFIG["timeout_seconds"]
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    remote_path = result["data"]["remote_path"]
                    print(f"✅ File uploaded successfully")
                    print(f"   Remote path: {remote_path}")
                    return remote_path
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ Upload failed: {error_msg}")
                    
                    # Check if it's a rate limit error
                    if "rate limit" in error_msg.lower() or "too many requests" in error_msg.lower():
                        delay = PROCESSING_CONFIG["rate_limit_delay"] * (2 ** attempt)
                        print(f"⏳ Rate limited, waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
            elif response.status_code == 429:  # Rate limited
                delay = PROCESSING_CONFIG["rate_limit_delay"] * (2 ** attempt)
                print(f"⏳ Rate limited (HTTP 429), waiting {delay}s before retry...")
                time.sleep(delay)
                continue
            else:
                print(f"❌ Upload request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Don't retry on client errors (4xx) except 429
                if 400 <= response.status_code < 500 and response.status_code != 429:
                    break
                    
        except requests.exceptions.Timeout:
            print(f"⏰ Upload timeout (attempt {attempt + 1})")
            if attempt < max_retries:
                delay = PROCESSING_CONFIG["retry_delay_base"] * (2 ** attempt)
                print(f"⏳ Waiting {delay}s before retry...")
                time.sleep(delay)
            continue
        except Exception as e:
            print(f"⚠️  Upload error (attempt {attempt + 1}): {e}")
            if attempt < max_retries:
                delay = PROCESSING_CONFIG["retry_delay_base"] * (2 ** attempt)
                print(f"⏳ Waiting {delay}s before retry...")
                time.sleep(delay)
            continue
    
    print(f"❌ Failed to upload {os.path.basename(file_path)} after {max_retries + 1} attempts")
    return file_path

def print_vision_model_data(agent, tool_results):
    """Print out the JSON data returned by vision model tools"""
    print(f"\n🔍 {agent.role}: VISION MODEL DATA ANALYSIS")
    print("=" * 60)
    
    for tool_name, result in tool_results.items():
        print(f"\n📊 Tool: {tool_name}")
        print(f"✅ Success: {result.get('success', 'Unknown')}")
        
        if 'data' in result:
            data = result['data']
            print(f"📄 Data Structure:")
            print(f"   - Keys: {list(data.keys())}")
            
            # Print extracted text if available
            if 'extracted_text' in data:
                text = data['extracted_text']
                print(f"📝 Extracted Text ({len(text)} chars):")
                print(f"   {text[:200]}{'...' if len(text) > 200 else ''}")
            
            # Print extracted data if available
            if 'extracted_data' in data:
                extracted = data['extracted_data']
                print(f"🎯 Extracted Data:")
                
                # Handle both old and new formats
                if 'headerSection' in extracted:
                    # New format (converted)
                    header = extracted.get('headerSection', {})
                    billing = extracted.get('billingDetails', {})
                    charges = extracted.get('chargesSummary', {})
                    print(f"   Vendor: {header.get('vendorName', 'N/A')}")
                    print(f"   Invoice #: {billing.get('invoiceNumber', 'N/A')}")
                    print(f"   Date: {billing.get('invoiceDate', 'N/A')}")
                    print(f"   Amount: ${charges.get('document_total', 'N/A')}")
                    print(f"   Tax: ${charges.get('secondary_tax', 'N/A')}")
                    print(f"   Line Items: {len(charges.get('lineItemsBreakdown', []))} items")
                else:
                    # Old format (direct)
                    print(f"   Vendor: {extracted.get('vendor_name', 'N/A')}")
                    print(f"   Invoice #: {extracted.get('invoice_number', 'N/A')}")
                    print(f"   Date: {extracted.get('invoice_date', 'N/A')}")
                    print(f"   Amount: ${extracted.get('amount', 'N/A')}")
                    print(f"   Tax: ${extracted.get('tax_amount', 'N/A')}")
                    print(f"   Line Items: {extracted.get('line_items', 'N/A')}")
            
            # Print screenshot info if available
            if 'screenshots_dir' in data:
                print(f"📸 Screenshots:")
                print(f"   Directory: {data.get('screenshots_dir', 'N/A')}")
                print(f"   Count: {data.get('screenshot_count', 'N/A')}")
                print(f"   Invoice ID: {data.get('invoice_id', 'N/A')}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
    
    print("=" * 60)

def print_database_data(agent, tool_results, invoice_data):
    """Print out the data being inserted into database"""
    print(f"\n💾 {agent.role}: DATABASE INSERTION DATA")
    print("=" * 60)
    
    if invoice_data:
        print(f"📊 Invoice Data to Insert:")
        if isinstance(invoice_data, dict) and 'extracted_data' in invoice_data:
            data = invoice_data['extracted_data']
            print(f"   Vendor: '{data.get('vendor_name', '')}'")
            print(f"   Invoice #: '{data.get('invoice_number', '')}'")
            print(f"   Date: '{data.get('invoice_date', '')}'")
            print(f"   Amount: {data.get('amount', 0)}")
            print(f"   Tax: {data.get('tax_amount', 0)}")
            print(f"   Line Items: '{data.get('line_items', '')}'")
        else:
            print(f"   Raw data: {invoice_data}")
    
    for tool_name, result in tool_results.items():
        print(f"\n🔧 Tool: {tool_name}")
        print(f"✅ Success: {result.get('success', 'Unknown')}")
        
        if 'data' in result:
            data = result['data']
            print(f"📄 Result Data:")
            for key, value in data.items():
                print(f"   {key}: {value}")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
    
    print("=" * 60)

def switch_to_remote_api_for_pdf():
    """Temporarily switch to remote API for PDF processing"""
    original_url = os.environ.get("MEMRA_API_URL")
    os.environ["MEMRA_API_URL"] = REMOTE_API_URL
    return original_url

def restore_api_url(original_url):
    """Restore the original API URL"""
    if original_url:
        os.environ["MEMRA_API_URL"] = original_url

def validate_agent_configuration(department):
    """Validate that critical agents have required tools configured"""
    critical_agents = {
        "Invoice Parser": ["PDFProcessor"],
        "Data Entry Specialist": ["DataValidator", "PostgresInsert"],
        "Data Engineer": ["SQLExecutor"]
    }
    
    for agent in department.agents:
        if agent.role in critical_agents:
            # Skip validation if agent has custom processing function
            if hasattr(agent, 'custom_processing') and agent.custom_processing is not None:
                print(f"ℹ️  {agent.role} uses custom processing (tools validation skipped)")
                continue
                
            required_tools = critical_agents[agent.role]
            # Handle both Tool objects and dictionaries
            configured_tools = []
            for tool in agent.tools:
                if isinstance(tool, dict):
                    configured_tools.append(tool["name"])
                else:
                    configured_tools.append(tool.name)
            
            missing_tools = [tool for tool in required_tools if tool not in configured_tools]
            if missing_tools:
                print(f"⚠️  WARNING: {agent.role} is missing critical tools: {missing_tools}")
                print(f"   Configured tools: {configured_tools}")
                return False
    
    return True

def main():
    """Run the ETL demo workflow with robust processing"""
    print("\n🚀 Starting ETL Invoice Processing Demo...")
    print("📊 This demo includes comprehensive database monitoring")
    print("📡 Tools will execute on Memra API server")
    print("📝 Processing 15 specific invoice files with robust error handling")
    print("⏱️  Includes delays between files and retry logic for API resilience")
    print("🎯 Target files:", ", ".join(TARGET_FILES))

    # Configuration
    config = {
        "table_name": os.getenv("MEMRA_TABLE_NAME", "invoices"),
        "data_directory": os.getenv("MEMRA_DATA_DIR", "data/invoices"),
        "company_id": os.getenv("MEMRA_COMPANY_ID", "acme_corp"),
        "fiscal_year": os.getenv("MEMRA_FISCAL_YEAR", "2024"),
        "database_url": os.getenv("MEMRA_DATABASE_URL", "postgresql://memra:memra123@localhost:5432/memra_invoice_db")
    }
    
    # Generate schema query dynamically
    schema_query = f"SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = '{config['table_name']}' ORDER BY ordinal_position"

    # Validate agent configuration before proceeding
    if not validate_agent_configuration(etl_department):
        print("❌ Critical agents are missing required tools!")
        print("⚠️  Please fix agent configuration before running ETL process")
        sys.exit(1)
    
    engine = ExecutionEngine()
    
    # Use configurable data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, config["data_directory"])
    
    # Find only the target files
    invoice_files = []
    missing_files = []
    
    for target_file in TARGET_FILES:
        file_path = os.path.join(data_dir, target_file)
        if os.path.exists(file_path):
            invoice_files.append(file_path)
        else:
            missing_files.append(target_file)
    
    if missing_files:
        print(f"⚠️  Missing files: {', '.join(missing_files)}")
    
    if not invoice_files:
        print(f"❌ No target files found in {config['data_directory']}/ directory")
        print("📝 Available files:")
        available_files = glob.glob(os.path.join(data_dir, "*.PDF"))
        for file in available_files[:10]:  # Show first 10
            print(f"   - {os.path.basename(file)}")
        if len(available_files) > 10:
            print(f"   ... and {len(available_files) - 10} more")
        sys.exit(1)

    print(f"\n📁 Found {len(invoice_files)} target files to process")
    print(f"⏱️  Estimated processing time: {len(invoice_files) * PROCESSING_CONFIG['delay_between_files']:.1f} seconds (plus processing time)")
    
    # Process files with robust error handling
    successful_processing = 0
    failed_processing = 0
    skipped_processing = 0
    
    for idx, invoice_file in enumerate(invoice_files):
        filename = os.path.basename(invoice_file)
        print(f"\n{'='*60}")
        print(f"📄 Processing file {idx + 1}/{len(invoice_files)}: {filename}")
        print(f"{'='*60}")
        
        # Add delay between files (except for the first one)
        if idx > 0:
            delay = PROCESSING_CONFIG["delay_between_files"] + random.uniform(0, 1)  # Add some randomness
            print(f"⏳ Waiting {delay:.1f}s between files...")
            time.sleep(delay)
        
        try:
            # Upload file with retry logic
            remote_file_path = upload_file_to_api(invoice_file, max_retries=PROCESSING_CONFIG["max_retries"])
            
            if remote_file_path == invoice_file:
                print(f"❌ Failed to upload {filename}, skipping...")
                failed_processing += 1
                continue

            # Run the full ETL workflow with configurable parameters
            input_data = {
                "file": remote_file_path,
                "connection": config["database_url"],
                "table_name": config["table_name"],
                "sql_query": schema_query
            }
            
            result = engine.execute_department(etl_department, input_data)
            
            if result.success:
                successful_processing += 1
                print(f"\n✅ Successfully processed: {filename}")
                
                # Show summary if available
                if 'etl_summary' in result.data:
                    summary = result.data['etl_summary']
                    print(f"📋 Status: {summary.get('status', 'success')}")
                if 'write_confirmation' in result.data:
                    write_conf = result.data['write_confirmation']
                    if isinstance(write_conf, dict) and 'record_id' in write_conf:
                        print(f"💾 Database Record ID: {write_conf['record_id']}")
            else:
                failed_processing += 1
                print(f"\n❌ Failed to process: {filename}")
                print(f"   Error: {result.error}")
                if result.trace and result.trace.errors:
                    print("   Details:")
                    for error in result.trace.errors:
                        print(f"     - {error}")
                
        except Exception as e:
            failed_processing += 1
            print(f"\n💥 Unexpected error processing {filename}: {e}")
            print("   Continuing with next file...")
            continue
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"🎯 ETL DEMO COMPLETED")
    print(f"{'='*60}")
    print(f"📊 Processing Summary:")
    print(f"   ✅ Successful: {successful_processing}")
    print(f"   ❌ Failed: {failed_processing}")
    print(f"   ⏭️  Skipped: {skipped_processing}")
    print(f"   📄 Total: {len(invoice_files)}")
    
    if successful_processing > 0:
        print(f"\n🎉 Demo completed successfully!")
        print(f"   Processed {successful_processing} invoices with robust error handling")
        print(f"   This demonstrates real-world API resilience and rate limiting")
    else:
        print(f"\n⚠️  No files were processed successfully")
        print(f"   Check API connectivity and file availability")
    
    print(f"\n💡 This demo shows realistic production scenarios:")
    print(f"   - API rate limiting and retry logic")
    print(f"   - Graceful error handling and file skipping")
    print(f"   - Delays between requests to avoid overwhelming APIs")
    print(f"   - Exponential backoff for failed requests")

if __name__ == "__main__":
    main() 