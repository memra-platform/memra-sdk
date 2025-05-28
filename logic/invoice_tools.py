import os
import sys
import subprocess
import base64
import json
import re
import logging
from typing import Dict, Any
from pathlib import Path
from huggingface_hub import InferenceClient
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date

# Add project root to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import local config, fallback to environment variables
try:
    from config import API_CONFIG
except ImportError:
    # Server deployment - use environment variables
    API_CONFIG = {
        "huggingface": {
            "api_key": os.getenv("HUGGINGFACE_API_KEY", ""),
            "model": os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-4-Maverick-17B-128E-Instruct"),
            "max_tokens": int(os.getenv("HUGGINGFACE_MAX_TOKENS", "2000"))
        }
    }

logger = logging.getLogger(__name__)

# Propane invoice data model
PROPANE_DATA_MODEL = {
    "headerSection": {
        "vendorName": "string",
        "customerName": "string", 
        "serviceAddress": "string",
        "subtotal": "number or null"
    },
    "billingDetails": {
        "invoiceDate": "string",
        "invoiceNumber": "string",
        "accountNumber": "string",
        "referenceNumber": "string or null",
        "Service Address": "string or null",
        "Subtotal": "number or null"
    },
    "chargesSummary": {
        "lineItemsBreakdown": [
            {
                "description": "string",
                "quantity": "number or null",
                "unit_price": "number or null", 
                "amount": "number",
                "main_product": "boolean"
            }
        ],
        "extended_total": "number",
        "calculated_subtotal": "number",
        "secondary_tax": "number",
        "calculated_total": "number",
        "document_total": "number",
        "invoiceNumber": "string",
        "accountNumber": "string",
        "memra_checksum": "string"
    },
    "paymentInstructions": {
        "dueOnInvoiceAmount": "number or null",
        "payInFullByDate": "string or null",
        "remitToAddress": "string or null",
        "barcodeFooter": "string or null",
        "vendor_name": "string or null"
    }
}

class DatabaseQueryTool:
    """Tool for querying database schemas and data"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        # TODO: Initialize database connection
        
    def get_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table"""
        logger.info(f"Getting schema for table: {table_name}")
        # TODO: Implement actual database query
        # For now, return the schema from our local file
        try:
            schema_path = Path(__file__).parent.parent / "local" / "dependencies" / "data_model.json"
            with open(schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            return {
                "columns": [
                    {"name": "id", "type": "integer", "nullable": False},
                    {"name": "invoice_number", "type": "varchar", "nullable": False},
                    {"name": "total_amount", "type": "decimal", "nullable": False},
                ],
                "constraints": [
                    {"type": "primary_key", "columns": ["id"]},
                    {"type": "unique", "columns": ["invoice_number"]}
                ]
            }

class PDFProcessor:
    """Tool for processing PDF files"""
    
    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process a PDF file and convert to high-resolution images"""
        logger.info(f"Processing PDF: {file_path}")
        
        try:
            # Create output directory for this PDF
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            pdf_name = pdf_path.stem
            output_dir = Path("temp_processing") / pdf_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert PDF to images using pdftoppm
            cmd = [
                "pdftoppm",
                "-png", 
                "-r", "300",  # 300 DPI for high resolution
                str(pdf_path),
                str(output_dir / "page")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Error converting PDF {file_path}: {result.stderr}")
                raise Exception(f"PDF conversion failed: {result.stderr}")
            
            # Get list of generated images
            image_files = list(output_dir.glob("*.png"))
            
            return {
                "pages": [
                    {
                        "page_number": i+1,
                        "image_path": str(img_path),
                        "content": f"Page {i+1} converted to image"
                    }
                    for i, img_path in enumerate(sorted(image_files))
                ],
                "metadata": {
                    "page_count": len(image_files),
                    "file_size": pdf_path.stat().st_size,
                    "output_directory": str(output_dir)
                }
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            raise

class OCRTool:
    """Tool for performing OCR on images"""
    
    def extract_text(self, image_data: Dict[str, Any]) -> str:
        """Extract text from an image using OCR"""
        logger.info("Performing OCR on image")
        
        # For now, we'll skip OCR since the LLM can process images directly
        # In a full implementation, you could use pytesseract here
        return "OCR text extraction - delegated to LLM vision processing"

class InvoiceExtractionWorkflow:
    """Workflow for extracting structured data from invoices using LLM"""
    
    def __init__(self):
        self.client = InferenceClient(
            provider="fireworks-ai",
            api_key=API_CONFIG["huggingface"]["api_key"],
        )
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_json_from_markdown(self, text: str) -> str:
        """Extract JSON from markdown response"""
        # Remove markdown code block markers
        text = re.sub(r'```json\n?', '', text)
        text = re.sub(r'\n?```', '', text)
        # Remove any newlines and extra spaces
        text = re.sub(r'\s+', ' ', text)
        # Convert Python dict syntax to JSON
        text = text.replace("'", '"')
        # Try to find JSON content
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_text = match.group(0)
            # Ensure the JSON is properly closed
            if not json_text.strip().endswith('}'):
                last_brace = json_text.rfind('}')
                if last_brace != -1:
                    json_text = json_text[:last_brace+1]
                else:
                    json_text = json_text.rstrip() + '}}'
            return json_text
        return text.strip()
    
    def validate_calculations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and calculate invoice totals"""
        try:
            charges = data.get("chargesSummary", {})
            line_items = charges.get("lineItemsBreakdown", [])
            
            # Find main product line item
            main_product = None
            additional_items_total = 0
            
            for item in line_items:
                if item.get("main_product"):
                    main_product = item
                elif item.get("amount") is not None:
                    additional_items_total += float(item["amount"])
            
            if main_product and main_product.get("unit_price") and main_product.get("quantity"):
                # Calculate extended total (price * quantity for main product)
                extended_total = float(main_product["unit_price"]) * float(main_product["quantity"])
                # Calculate subtotal (extended total + sum of additional items)
                calculated_subtotal = extended_total + additional_items_total
                # Get the document total
                document_total = float(charges.get("document_total", 0))
                
                # Calculate secondary tax
                secondary_tax = document_total - calculated_subtotal
                if abs(secondary_tax) < 0.01:
                    secondary_tax = 0.0
                
                # Update the data with calculated values
                charges["extended_total"] = round(extended_total, 2)
                charges["calculated_subtotal"] = round(calculated_subtotal, 2)
                charges["secondary_tax"] = round(secondary_tax, 2)
                charges["calculated_total"] = round(document_total, 2)
                
                # Set checksum
                if abs((calculated_subtotal + secondary_tax) - document_total) <= 0.01:
                    charges["memra_checksum"] = "pass"
                else:
                    charges["memra_checksum"] = "fail"
            else:
                charges["memra_checksum"] = "fail"
                
        except Exception as e:
            logger.error(f"Error in calculations: {e}")
            data.get("chargesSummary", {})["memra_checksum"] = "fail"
        
        return data
    
    def extract_data(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from invoice using LLM vision"""
        logger.info("Extracting structured data from invoice using LLM")
        
        # Get the first image from the PDF processing results
        # This is a simplified approach - in practice you'd handle multiple pages
        temp_dir = Path("temp_processing")
        image_files = list(temp_dir.rglob("*.png"))
        
        if not image_files:
            raise Exception("No processed images found for extraction")
        
        # Use the first image
        image_path = image_files[0]
        base64_image = self.encode_image(str(image_path))
        
        # Create the completion with both text and image
        completion = self.client.chat.completions.create(
            model=API_CONFIG["huggingface"]["model"],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Please analyze this propane invoice image and fill out the following data model with the information you find. 
                            Pay special attention to:

                            1. For each line item in chargesSummary, include:
                               - description (keep full description on one line)
                               - quantity (if available, otherwise null)
                               - unit_price (if available, otherwise null)
                               - amount (total for the line, must be a number)
                               - main_product: true for the main product (usually bulk propane), false for additional charges
                            
                            2. The main product will typically be the bulk propane line item
                               - This should have main_product = true
                               - All other items (taxes, fees, etc.) should have main_product = false
                               - Make sure to include quantity and unit_price for the main product
                            
                            3. Look for a barcode in the footer of the invoice
                               - Include it in paymentInstructions.barcodeFooter if found
                               - Set to null if not found
                            
                            Return the data in proper JSON format with double quotes around property names and string values.
                            Do not include any additional text or explanation.
                            Here is the data model structure:
                            {json.dumps(PROPANE_DATA_MODEL)}
                            """
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
            max_tokens=API_CONFIG["huggingface"]["max_tokens"],
        )
        
        # Extract and parse the JSON response
        try:
            json_text = self.extract_json_from_markdown(completion.choices[0].message.content)
            response_data = json.loads(json_text)
            # Validate calculations
            response_data = self.validate_calculations(response_data)
            return response_data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Raw response: {completion.choices[0].message.content}")
            raise Exception(f"Failed to parse LLM response: {e}")

class DataValidator:
    """Tool for validating extracted data"""
    
    def validate(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema"""
        logger.info("Validating extracted data")
        
        validation_errors = []
        
        try:
            # Check required fields
            required_fields = [
                "headerSection.vendorName",
                "billingDetails.invoiceNumber", 
                "chargesSummary.document_total"
            ]
            
            for field_path in required_fields:
                keys = field_path.split('.')
                current = data
                try:
                    for key in keys:
                        current = current[key]
                    if current is None or current == "":
                        validation_errors.append(f"Required field {field_path} is missing or empty")
                except KeyError:
                    validation_errors.append(f"Required field {field_path} not found")
            
            # Validate calculations checksum
            checksum = data.get("chargesSummary", {}).get("memra_checksum")
            if checksum != "pass":
                validation_errors.append("Invoice calculations do not match (checksum failed)")
            
            return {
                "is_valid": len(validation_errors) == 0,
                "validation_errors": validation_errors
            }
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "is_valid": False,
                "validation_errors": [f"Validation process failed: {str(e)}"]
            }

class PostgresInsert:
    """Tool for inserting data into Postgres"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.connection = None
        
    def _connect(self):
        """Establish database connection"""
        if self.connection is None:
            try:
                # Build connection string from credentials
                host = self.credentials.get("host", "localhost")
                port = self.credentials.get("port", 5432)
                database = self.credentials.get("database", "memra_invoice_db")
                user = self.credentials.get("user", "tarpus")
                password = self.credentials.get("password", "")
                
                if password:
                    conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
                else:
                    conn_string = f"postgresql://{user}@{host}:{port}/{database}"
                
                self.connection = psycopg2.connect(conn_string)
                logger.info(f"Connected to database: {database}")
                
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
                raise
    
    def _parse_invoice_date(self, date_str: str) -> date:
        """Parse invoice date from various formats"""
        if not date_str:
            return datetime.now().date()
        
        # Try common date formats
        formats = ["%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d/%m/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # If all formats fail, return today's date
        logger.warning(f"Could not parse date '{date_str}', using today's date")
        return datetime.now().date()
        
    def insert_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a record into the database"""
        logger.info(f"Inserting record into {table}")
        
        try:
            self._connect()
            
            # Extract key fields from the invoice data
            header = data.get("headerSection", {})
            billing = data.get("billingDetails", {})
            charges = data.get("chargesSummary", {})
            
            invoice_number = charges.get("invoiceNumber") or billing.get("invoiceNumber", "UNKNOWN")
            vendor_name = header.get("vendorName", "UNKNOWN")
            total_amount = charges.get("document_total", 0)
            tax_amount = charges.get("secondary_tax", 0)
            invoice_date = self._parse_invoice_date(billing.get("invoiceDate", ""))
            
            # Prepare line items as JSONB
            line_items = charges.get("lineItemsBreakdown", [])
            
            # Insert query
            insert_query = """
                INSERT INTO invoices (
                    invoice_number, vendor_name, invoice_date, total_amount, 
                    tax_amount, line_items, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id;
            """
            
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, (
                    invoice_number,
                    vendor_name,
                    invoice_date,
                    float(total_amount),
                    float(tax_amount) if tax_amount else None,
                    json.dumps(line_items),
                    'pending'
                ))
                
                record_id = cursor.fetchone()[0]
                self.connection.commit()
                
                logger.info(f"Successfully inserted invoice {invoice_number} with ID {record_id}")
                
                return {
                    "success": True,
                    "record_id": record_id,
                    "invoice_number": invoice_number,
                    "total_amount": total_amount,
                    "vendor_name": vendor_name,
                    "database_table": table
                }
                
        except psycopg2.IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            if self.connection:
                self.connection.rollback()
            return {
                "success": False,
                "error": f"Database integrity error (possibly duplicate invoice): {str(e)}"
            }
            
        except Exception as e:
            logger.error(f"Database insert failed: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def __del__(self):
        """Close database connection when object is destroyed"""
        if self.connection:
            self.connection.close() 