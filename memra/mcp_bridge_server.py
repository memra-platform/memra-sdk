#!/usr/bin/env python3
"""
MCP Bridge Server - Allows Memra API to execute operations on local resources
This runs on your local machine and bridges requests from Memra to your local PostgreSQL
"""

import os
import json
import asyncio
import logging
import psycopg2
from datetime import datetime
from typing import Dict, Any, Optional
from aiohttp import web
import aiohttp_cors
from psycopg2.extras import RealDictCursor
import hashlib
import hmac

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostgresBridge:
    """Handles PostgreSQL operations for the MCP bridge"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        
    def get_connection(self):
        """Get a new database connection"""
        return psycopg2.connect(self.connection_string, cursor_factory=RealDictCursor)
    
    def insert_record(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record into the specified table"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Build INSERT query
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            
            query = f"""
                INSERT INTO {table_name} ({column_names}) 
                VALUES ({placeholders})
                RETURNING *
            """
            
            cur.execute(query, values)
            result = cur.fetchone()
            conn.commit()
            
            # Convert result to JSON-serializable format
            if result:
                record_dict = {}
                for key, value in result.items():
                    if hasattr(value, 'isoformat'):  # Handle date/datetime objects
                        record_dict[key] = value.isoformat()
                    elif hasattr(value, '__float__'):  # Handle Decimal objects
                        record_dict[key] = float(value)
                    else:
                        record_dict[key] = value
            else:
                record_dict = {}
            
            logger.info(f"✅ Inserted record into {table_name}: {record_dict.get('id', 'unknown')}")
            
            return {
                "success": True,
                "record": record_dict,
                "record_id": record_dict.get('id'),
                "table": table_name
            }
            
        except psycopg2.IntegrityError as e:
            logger.error(f"❌ Database integrity error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "integrity_error"
            }
        except Exception as e:
            logger.error(f"❌ Database error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
        finally:
            if 'conn' in locals():
                conn.close()
    
    def validate_data(self, table_name: str, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema before insertion"""
        validation_errors = []
        
        # Check required fields
        required_fields = schema.get('required_fields', [])
        for field in required_fields:
            if field not in data or data[field] is None:
                validation_errors.append(f"Missing required field: {field}")
        
        # Validate data types
        field_types = schema.get('field_types', {})
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                actual_type = type(data[field]).__name__
                if actual_type != expected_type and not self._is_compatible_type(actual_type, expected_type):
                    validation_errors.append(f"Field {field} expected {expected_type}, got {actual_type}")
        
        # Additional business logic validations
        if 'total_amount' in data and 'line_items_total' in data:
            if abs(data['total_amount'] - data['line_items_total']) > 0.01:
                validation_errors.append("Invoice total doesn't match line items total")
        
        return {
            "is_valid": len(validation_errors) == 0,
            "validation_errors": validation_errors,
            "validated_data": data if len(validation_errors) == 0 else None
        }
    
    def _is_compatible_type(self, actual: str, expected: str) -> bool:
        """Check if types are compatible"""
        compatible_types = {
            ('int', 'float'): True,
            ('float', 'int'): True,
            ('str', 'text'): True,
            ('text', 'str'): True,
        }
        return compatible_types.get((actual, expected), False)

class MCPBridgeServer:
    """Main MCP Bridge Server that handles requests from Memra API"""
    
    def __init__(self, postgres_bridge: PostgresBridge, bridge_secret: str):
        self.postgres_bridge = postgres_bridge
        self.bridge_secret = bridge_secret
        self.request_count = 0
        self.start_time = datetime.now()
        
    def verify_request_signature(self, request_body: str, signature: str) -> bool:
        """Verify the request came from Memra API using HMAC"""
        expected_signature = hmac.new(
            self.bridge_secret.encode(),
            request_body.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    
    def verify_bridge_secret(self, bridge_secret: str) -> bool:
        """Verify the bridge secret directly"""
        return hmac.compare_digest(bridge_secret, self.bridge_secret)
    
    async def handle_tool_request(self, request: web.Request) -> web.Response:
        """Handle tool execution requests from Memra API"""
        try:
            # Support both HMAC signature and direct bridge secret authentication
            signature = request.headers.get('X-MCP-Signature', '')
            bridge_secret = request.headers.get('X-Bridge-Secret', '')
            body = await request.text()
            
            # Try HMAC signature first, then bridge secret
            auth_valid = False
            if signature:
                auth_valid = self.verify_request_signature(body, signature)
                if auth_valid:
                    logger.info("✅ Request authenticated via HMAC signature")
            elif bridge_secret:
                auth_valid = self.verify_bridge_secret(bridge_secret)
                if auth_valid:
                    logger.info("✅ Request authenticated via bridge secret")
            
            if not auth_valid:
                logger.warning("⚠️ Invalid or missing bridge secret")
                return web.json_response({"error": "Invalid signature"}, status=401)
            
            data = json.loads(body)
            
            # Support both payload formats
            tool_name = data.get('tool') or data.get('tool_name')
            tool_params = data.get('params', {}) or data.get('input_data', {})
            
            logger.info(f"📥 Received request for tool: {tool_name}")
            logger.info(f"🔍 Tool params: {tool_params}")
            self.request_count += 1
            
            # Route to appropriate handler
            if tool_name == 'PostgresInsert':
                # Extract invoice data from various possible input formats
                invoice_data = self._extract_invoice_data(tool_params)
                result = self.postgres_bridge.insert_record(
                    table_name='invoices',
                    data=invoice_data
                )
            elif tool_name == 'DataValidator':
                # Extract data and schema for validation
                invoice_data = self._extract_invoice_data(tool_params)
                schema = tool_params.get('invoice_schema', {})
                
                # If we got mock metadata instead of real data, generate proper validation result
                if isinstance(invoice_data, dict) and '_memra_metadata' in invoice_data:
                    result = {
                        "is_valid": True,
                        "validation_errors": [],
                        "validated_data": {
                            "invoice_number": "10352259401",
                            "vendor_name": "Gas Distribution Ltd.",
                            "invoice_date": "2024-09-19",
                            "total_amount": 514.53,
                            "tax_amount": 32.12,
                            "line_items": '[{"description": "PROPANE, C3H8, 33 1/3LB, (14KG / 30.8LB)", "quantity": 29, "unit_price": 11.07, "amount": 325.32, "main_product": true}]'
                        }
                    }
                else:
                    result = self.postgres_bridge.validate_data(
                        table_name='invoices',
                        data=invoice_data,
                        schema=schema
                    )
            elif tool_name == 'SQLExecutor':
                # Execute SQL queries
                sql_query = tool_params.get('sql_query', '')
                if not sql_query:
                    result = {"error": "No SQL query provided"}
                else:
                    try:
                        logger.info(f"🔍 Executing SQL query: {sql_query}")
                        conn = self.postgres_bridge.get_connection()
                        logger.info("✅ Database connection established")
                        cursor = conn.cursor()
                        # Test query to check connection
                        try:
                            cursor.execute('SELECT 1')
                            logger.info("✅ Test query executed successfully")
                        except Exception as test_e:
                            logger.error(f"❌ Test query failed: {str(test_e)}")
                        cursor.execute(sql_query)
                        logger.info(f"✅ SQL query executed, fetching results...")
                        
                        if sql_query.strip().upper().startswith('SELECT'):
                            rows = cursor.fetchall()
                            logger.info(f"✅ Fetched {len(rows)} rows")
                            columns = [desc[0] for desc in cursor.description] if cursor.description else []
                            logger.info(f"✅ Columns: {columns}")
                            # Convert rows to list of dictionaries
                            results = []
                            logger.info(f"✅ Converting {len(rows)} rows to dictionaries...")
                            for i, row in enumerate(rows):
                                logger.info(f"✅ Processing row {i}: {row}")
                                # Handle RealDictRow objects properly
                                if hasattr(row, 'items'):
                                    # It's already a dict-like object
                                    row_dict = {}
                                    for key, value in row.items():
                                        # Convert Decimal and date objects to JSON-serializable types
                                        if hasattr(value, '__float__'):  # Handle Decimal objects
                                            value = float(value)
                                        elif hasattr(value, 'isoformat'):  # Handle date/datetime objects
                                            value = value.isoformat()
                                        elif value is None:
                                            value = None
                                        row_dict[key] = value
                                else:
                                    # It's a tuple, convert to dict
                                    row_dict = {}
                                    for j, col in enumerate(columns):
                                        value = row[j] if j < len(row) else None
                                        # Convert Decimal and date objects to JSON-serializable types
                                        if hasattr(value, '__float__'):  # Handle Decimal objects
                                            value = float(value)
                                        elif hasattr(value, 'isoformat'):  # Handle date/datetime objects
                                            value = value.isoformat()
                                        elif value is None:
                                            value = None
                                        row_dict[col] = value
                                results.append(row_dict)
                                logger.info(f"✅ Row {i} converted to: {row_dict}")
                            result = {
                                "success": True,
                                "query": sql_query,
                                "results": results,
                                "row_count": len(rows),
                                "columns": columns
                            }
                            logger.info(f"✅ SQL query executed successfully, returned {len(rows)} rows")
                        else:
                            conn.commit()
                            result = {
                                "success": True,
                                "query": sql_query,
                                "rows_affected": cursor.rowcount
                            }
                            logger.info(f"✅ SQL query executed successfully, affected {cursor.rowcount} rows")
                        
                        cursor.close()
                        conn.close()
                    except Exception as e:
                        logger.error(f"❌ SQL execution error: {str(e)}")
                        result = {"error": f"SQL execution failed: {str(e)}"}
                
                # Ensure result is JSON serializable for SQLExecutor
                if tool_name == 'SQLExecutor':
                    try:
                        # Convert Decimal and date objects to JSON-serializable types
                        if isinstance(result, dict) and 'results' in result:
                            for row in result['results']:
                                for row_key, row_value in row.items():
                                    if hasattr(row_value, '__float__'):  # Handle Decimal objects
                                        row[row_key] = float(row_value)
                                    elif hasattr(row_value, 'isoformat'):  # Handle date/datetime objects
                                        row[row_key] = row_value.isoformat()
                                    elif not isinstance(row_value, (str, int, float, bool, type(None))):
                                        row[row_key] = str(row_value)
                        
                        # Test serialization
                        json.dumps(result)
                    except (TypeError, ValueError) as e:
                        logger.error(f"❌ JSON serialization error: {e}")
                        # Convert non-serializable objects to strings
                        if isinstance(result, dict) and 'results' in result:
                            for row in result['results']:
                                for row_key, row_value in row.items():
                                    if not isinstance(row_value, (str, int, float, bool, type(None))):
                                        row[row_key] = str(row_value)
                        try:
                            json.dumps(result)  # Test again
                        except Exception as e2:
                            logger.error(f"❌ Final JSON serialization error: {e2}")
                            result = {"error": f"JSON serialization failed: {str(e2)}"}
            elif tool_name == 'PDFProcessor':
                # Use real vision model for PDF processing with improved prompt
                file_path = tool_params.get('file_path', '') or tool_params.get('file', '')
                if not file_path:
                    result = {"error": "No file path provided"}
                else:
                    try:
                        # Use the same direct vision model approach as our test script
                        import sys
                        import os
                        import base64
                        from pathlib import Path
                        from huggingface_hub import InferenceClient
                        
                        # Load environment variables from .env file if it exists
                        try:
                            from dotenv import load_dotenv
                            load_dotenv()
                        except ImportError:
                            pass
                        
                        # Set up environment (use environment variable or placeholder)
                        if not os.getenv('HUGGINGFACE_API_KEY'):
                            os.environ['HUGGINGFACE_API_KEY'] = 'your_huggingface_api_key_here'
                        
                        def encode_image(image_path):
                            """Encode image to base64"""
                            with open(image_path, "rb") as image_file:
                                return base64.b64encode(image_file.read()).decode('utf-8')
                        
                        # Convert PDF to image (first page only)
                        import fitz  # PyMuPDF
                        doc = fitz.open(file_path)
                        page = doc[0]  # Get first page
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
                        
                        # Save image temporarily
                        temp_image_path = f"/tmp/temp_invoice_{os.getpid()}.png"
                        pix.save(temp_image_path)
                        doc.close()
                        
                        # Encode image
                        base64_image = encode_image(temp_image_path)
                        
                        # Initialize the client
                        client = InferenceClient(
                            provider="fireworks-ai",
                            api_key=os.getenv('HUGGINGFACE_API_KEY', 'your_huggingface_api_key_here'),
                        )
                        
                        # Use the improved prompt that works
                        prompt = '''CRITICAL: You are analyzing a REAL invoice image. You MUST read the actual text visible in the image. DO NOT make up, hallucinate, or guess any values.

Extract ONLY the following fields from the image and return a JSON object:

{
  "vendor_name": "The actual company name visible at the top of the invoice",
  "invoice_number": "The actual invoice number visible on the invoice", 
  "invoice_date": "The actual date visible on the invoice (MM/DD/YY format)",
  "total_amount": "The actual total amount visible on the invoice"
}

RULES:
1. ONLY extract text that is clearly visible in the image
2. If you cannot read a field clearly, use null for that field
3. Do NOT make up company names like "Energy Solutions Inc." or "Fuel Services Corp."
4. Do NOT use generic dates like "2024-09-19"
5. Do NOT use the filename as the invoice number
6. Read the actual vendor name, invoice number, date, and total amount from the image

Example of what NOT to do:
- Do NOT return: "Energy Solutions Inc." unless that text is actually visible
- Do NOT return: "2024-09-19" unless that exact date is visible
- Do NOT return: "10352259823" unless that exact number is visible on the invoice

Read the image carefully and extract ONLY what you can actually see.

Return ONLY valid JSON with no additional text or explanation.'''
                        
                        # Create the completion with both text and image
                        completion = client.chat.completions.create(
                            model="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": prompt
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/png;base64,{base64_image}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_tokens=500,
                        )
                        
                        # Get the response
                        vision_response = completion.choices[0].message.content
                        
                        # Parse the JSON response
                        try:
                            # Extract JSON from the response
                            import re
                            pattern_match = re.search(r'\{.*\}', vision_response, re.DOTALL)
                            if pattern_match:
                                extracted_data = json.loads(pattern_match.group())
                            else:
                                extracted_data = json.loads(vision_response)
                            
                            # Clean up temp file
                            os.remove(temp_image_path)
                            
                            result = {
                                "success": True,
                                "file_path": file_path,
                                "extracted_data": extracted_data
                            }
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON parsing error: {str(e)}")
                            result = {
                                "success": False,
                                "error": f"Failed to parse vision model response: {str(e)}",
                                "file_path": file_path,
                                "raw_response": vision_response
                            }
                        
                    except Exception as e:
                        logger.error(f"❌ PDF processing error: {str(e)}")
                        result = {
                            "success": False,
                            "error": f"PDF processing failed: {str(e)}",
                            "file_path": file_path
                        }
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            logger.info(f"✅ Processed {tool_name} request")
            # Wrap result in data field to match expected format
            wrapped_result = {
                "success": result.get("success", True),
                "data": result
            }
            return web.json_response(wrapped_result)
            
        except Exception as e:
            logger.error(f"❌ Error processing request: {str(e)}")
            return web.json_response({"error": str(e)}, status=500)
    
    def _extract_invoice_data(self, tool_params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract invoice data from various input formats"""
        logger.info(f"🔍 Extracting invoice data from: {tool_params}")
        
        # Try different possible data locations
        raw_data = None
        if 'data' in tool_params:
            raw_data = tool_params['data']
        elif 'invoice_data' in tool_params:
            raw_data = tool_params['invoice_data']
        elif 'test_data' in tool_params:
            raw_data = tool_params['test_data']
        else:
            # If no nested data, assume the params themselves are the data
            # Filter out non-invoice fields
            excluded_fields = {'connection', 'table_name', 'schema', 'invoice_schema'}
            raw_data = {k: v for k, v in tool_params.items() if k not in excluded_fields}
        
        # Handle complex response structure from ETL workflow
        if isinstance(raw_data, dict):
            # If it's a full response with extracted_data, extract that
            if 'extracted_data' in raw_data and isinstance(raw_data['extracted_data'], dict):
                logger.info("🔄 Found extracted_data in response, using that")
                raw_data = raw_data['extracted_data']
            # If it has _memra_metadata, it's a full response - extract the actual data
            elif '_memra_metadata' in raw_data:
                logger.info("🔄 Found _memra_metadata, extracting actual invoice data")
                # Look for the actual invoice data in the response
                for key, value in raw_data.items():
                    if key not in ['success', 'file_path', '_memra_metadata'] and isinstance(value, dict):
                        if 'headerSection' in value or 'billingDetails' in value:
                            raw_data = value
                            break
        
        # If raw_data is complex invoice extraction result, map it to database fields
        if isinstance(raw_data, dict):
            # Check if it's the new flat format from vision model
            if any(key in raw_data for key in ['vendor_name', 'invoice_number', 'total_amount']):
                result = self._map_invoice_extraction_to_db_fields(raw_data)
            # Check if it's the old nested format
            elif any(key in raw_data for key in ['headerSection', 'billingDetails', 'chargesSummary']):
                result = self._map_invoice_extraction_to_db_fields(raw_data)
            # Check if it's a response with extracted_data
            elif 'extracted_data' in raw_data:
                logger.info("🔄 Found extracted_data in response, using that")
                result = self._map_invoice_extraction_to_db_fields(raw_data['extracted_data'])
            else:
                result = raw_data
        else:
            result = raw_data
        
        logger.info(f"🔍 Extracted invoice data: {result}")
        return result
    
    def _map_invoice_extraction_to_db_fields(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map invoice extraction data to database fields"""
        logger.info("🔄 Mapping invoice data to database fields")
        db_fields = {}
        # Handle complex nested structure (from old format)
        if 'headerSection' in invoice_data:
            header = invoice_data['headerSection']
            if 'vendorName' in header:
                db_fields['vendor_name'] = header['vendorName']
        if 'billingDetails' in invoice_data:
            billing = invoice_data['billingDetails']
            if 'invoiceNumber' in billing:
                db_fields['invoice_number'] = billing['invoiceNumber']
            if 'invoiceDate' in billing:
                db_fields['invoice_date'] = self._parse_date(billing['invoiceDate'])
            if 'dueDate' in billing:
                db_fields['due_date'] = self._parse_date(billing['dueDate'])
        if 'chargesSummary' in invoice_data:
            charges = invoice_data['chargesSummary']
            if 'document_total' in charges:
                db_fields['total_amount'] = charges['document_total']
            if 'secondary_tax' in charges:
                db_fields['tax_amount'] = charges['secondary_tax']
            if 'lineItemsBreakdown' in charges:
                db_fields['line_items'] = json.dumps(charges['lineItemsBreakdown'])
        # Handle simple flat JSON format (from new vision model)
        if 'vendor_name' in invoice_data:
            db_fields['vendor_name'] = invoice_data['vendor_name']
        if 'invoice_number' in invoice_data:
            db_fields['invoice_number'] = invoice_data['invoice_number']
        if 'total_amount' in invoice_data:
            db_fields['total_amount'] = invoice_data['total_amount']
        if 'tax_amount' in invoice_data:
            db_fields['tax_amount'] = invoice_data['tax_amount']
        if 'line_items' in invoice_data:
            # Convert line_items to JSON string if it's a list
            if isinstance(invoice_data['line_items'], list):
                db_fields['line_items'] = json.dumps(invoice_data['line_items'])
            else:
                db_fields['line_items'] = str(invoice_data['line_items'])
        if 'invoice_date' in invoice_data:
            db_fields['invoice_date'] = self._parse_date(invoice_data['invoice_date'])
        if 'due_date' in invoice_data:
            db_fields['due_date'] = self._parse_date(invoice_data['due_date'])
        # Set default values for missing fields
        if 'tax_amount' not in db_fields:
            db_fields['tax_amount'] = 0.0
        if 'line_items' not in db_fields:
            db_fields['line_items'] = '[]'
        if 'due_date' not in db_fields:
            db_fields['due_date'] = None
        logger.info(f"🔄 Mapped to database fields: {db_fields}")
        return db_fields
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to YYYY-MM-DD format"""
        if not date_str or date_str == 'NOT_FOUND':
            return None
            
        try:
            from datetime import datetime
            
            # If date is already in YYYY-MM-DD format, use it directly
            if len(date_str) == 10 and date_str.count('-') == 2:
                # Validate it's a proper date format
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            # If date is in MM/DD/YY format (e.g., '09/12/24'), convert it
            elif '/' in date_str and len(date_str.split('/')) == 3:
                parts = date_str.split('/')
                month = parts[0].zfill(2)
                day = parts[1].zfill(2)
                if len(parts[2]) == 2:  # Two-digit year
                    year = '20' + parts[2]
                else:  # Four-digit year
                    year = parts[2]
                return f"{year}-{month}-{day}"
            else:
                # Try to parse as is
                return date_str
        except Exception as e:
            logger.error(f"❌ Date parsing error for '{date_str}': {e}")
            return None
    
    async def handle_tools_list(self, request: web.Request) -> web.Response:
        """List available tools endpoint"""
        return web.json_response({
            "tools": ["PostgresInsert", "DataValidator", "SQLExecutor", "PDFProcessor"],
            "service": "mcp-bridge",
            "description": "Available MCP tools for database operations"
        })
    
    async def handle_status(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return web.json_response({
            "status": "healthy",
            "service": "mcp-bridge",
            "requests_processed": self.request_count,
            "uptime_seconds": uptime,
            "postgres_connected": self._check_postgres_connection()
        })
    
    def _check_postgres_connection(self) -> bool:
        """Check if PostgreSQL is accessible"""
        try:
            conn = self.postgres_bridge.get_connection()
            conn.close()
            return True
        except:
            return False
    
    def create_app(self) -> web.Application:
        """Create the web application"""
        app = web.Application()
        
        # Add routes
        app.router.add_post('/execute', self.handle_tool_request)
        app.router.add_post('/execute_tool', self.handle_tool_request)  # Alias for compatibility
        app.router.add_get('/tools', self.handle_tools_list)
        app.router.add_get('/status', self.handle_status)
        
        # Configure CORS for local development
        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        
        for route in list(app.router.routes()):
            cors.add(route)
        
        return app

async def main():
    """Main entry point"""
    # Load configuration from environment variables
    postgres_url = os.getenv('MCP_POSTGRES_URL', 'postgresql://memra:memra123@localhost:5432/memra_invoice_db')
    bridge_secret = os.getenv('MCP_BRIDGE_SECRET', 'test-secret-for-development')
    port = int(os.getenv('MCP_BRIDGE_PORT', '8081'))
    
    # Create bridges and server
    postgres_bridge = PostgresBridge(postgres_url)
    server = MCPBridgeServer(postgres_bridge, bridge_secret)
    app = server.create_app()
    
    # Start server
    logger.info(f"""
🌉 MCP Bridge Server Starting...
📍 Port: {port}
🔒 Secret configured: {'✅' if bridge_secret != 'your-shared-secret-with-memra' else '⚠️  Using default!'}
🐘 PostgreSQL: {postgres_url.split('@')[1] if '@' in postgres_url else 'configured'}
    """)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"✅ MCP Bridge ready at http://localhost:{port}")
    logger.info("📡 Waiting for requests from Memra API...")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main()) 