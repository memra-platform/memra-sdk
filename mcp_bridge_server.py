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
    
    async def handle_tool_request(self, request: web.Request) -> web.Response:
        """Handle tool execution requests from Memra API"""
        try:
            # Verify request signature
            signature = request.headers.get('X-MCP-Signature', '')
            body = await request.text()
            
            if not self.verify_request_signature(body, signature):
                logger.warning("⚠️ Invalid request signature")
                return web.json_response({"error": "Invalid signature"}, status=401)
            
            data = json.loads(body)
            tool_name = data.get('tool')
            tool_params = data.get('params', {})
            
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
                result = self.postgres_bridge.validate_data(
                    table_name='invoices',
                    data=invoice_data,
                    schema=schema
                )
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            logger.info(f"✅ Processed {tool_name} request")
            return web.json_response(result)
            
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
        
        # If raw_data is complex invoice extraction result, map it to database fields
        if isinstance(raw_data, dict) and ('headerSection' in raw_data or 'billingDetails' in raw_data):
            result = self._map_invoice_extraction_to_db_fields(raw_data)
        else:
            result = raw_data
        
        logger.info(f"🔍 Extracted invoice data: {result}")
        return result
    
    def _map_invoice_extraction_to_db_fields(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map complex invoice extraction data to simple database fields"""
        logger.info("🔄 Mapping complex invoice data to database fields")
        
        # Extract basic fields from different sections
        db_fields = {}
        
        # Get invoice number and vendor name
        if 'billingDetails' in invoice_data:
            billing = invoice_data['billingDetails']
            if 'invoiceNumber' in billing:
                db_fields['invoice_number'] = billing['invoiceNumber']
            if 'invoiceDate' in billing:
                # Convert date format from '19-SEP-24' to '2024-09-19'
                date_str = billing['invoiceDate']
                try:
                    from datetime import datetime
                    # Parse various date formats
                    if '-' in date_str and len(date_str.split('-')) == 3:
                        parts = date_str.split('-')
                        if len(parts[2]) == 2:  # 2-digit year
                            year = '20' + parts[2]
                        else:
                            year = parts[2]
                        
                        # Convert month name to number
                        month_map = {
                            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
                        }
                        month = month_map.get(parts[1], '01')
                        day = parts[0].zfill(2)
                        db_fields['invoice_date'] = f"{year}-{month}-{day}"
                    else:
                        db_fields['invoice_date'] = date_str
                except:
                    db_fields['invoice_date'] = date_str
        
        # Get vendor name from header or payment instructions
        if 'headerSection' in invoice_data and 'vendorName' in invoice_data['headerSection']:
            db_fields['vendor_name'] = invoice_data['headerSection']['vendorName']
        elif 'paymentInstructions' in invoice_data and 'vendor_name' in invoice_data['paymentInstructions']:
            db_fields['vendor_name'] = invoice_data['paymentInstructions']['vendor_name']
        
        # Get total amount
        if 'chargesSummary' in invoice_data:
            charges = invoice_data['chargesSummary']
            if 'calculated_total' in charges:
                db_fields['total_amount'] = float(charges['calculated_total'])
            elif 'document_total' in charges:
                db_fields['total_amount'] = float(charges['document_total'])
        
        # Get tax amount
        if 'chargesSummary' in invoice_data and 'secondary_tax' in invoice_data['chargesSummary']:
            db_fields['tax_amount'] = float(invoice_data['chargesSummary']['secondary_tax'])
        
        # Store line items as JSON
        if 'chargesSummary' in invoice_data and 'lineItemsBreakdown' in invoice_data['chargesSummary']:
            import json
            db_fields['line_items'] = json.dumps(invoice_data['chargesSummary']['lineItemsBreakdown'])
        
        logger.info(f"🔄 Mapped to database fields: {db_fields}")
        return db_fields
    
    async def handle_tools_list(self, request: web.Request) -> web.Response:
        """List available tools endpoint"""
        return web.json_response({
            "tools": ["PostgresInsert", "DataValidator"],
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
    bridge_secret = os.getenv('MCP_BRIDGE_SECRET', 'your-shared-secret-with-memra')
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