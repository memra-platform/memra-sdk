#!/usr/bin/env python3
"""
Vision-Based PDF Processor
This script processes PDFs by taking screenshots of each page and sending them to a vision model
"""

import os
import sys
import base64
import fitz  # PyMuPDF
import tempfile
from PIL import Image
import io
from huggingface_hub import InferenceClient
from typing import Dict, Any, List
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionPDFProcessor:
    """Process PDFs using vision models to extract invoice data"""
    
    def __init__(self, api_key: str = None):
        """Initialize the vision processor"""
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        self.client = InferenceClient(
            provider="fireworks-ai",
            api_key=self.api_key,
        )
        self.model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct"
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def take_page_screenshot(self, pdf_path: str, page_num: int, output_dir: str = None) -> str:
        """Take a screenshot of a specific PDF page"""
        try:
            doc = fitz.open(pdf_path)
            page = doc[page_num]
            
            # Create output directory if not provided
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix="pdf_screenshots_")
            
            # Render page to image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Save image
            image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
            pix.save(image_path)
            
            doc.close()
            logger.info(f"Screenshot saved: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error taking screenshot of page {page_num}: {str(e)}")
            return None
    
    def process_page_with_vision(self, image_path: str, page_num: int) -> Dict[str, Any]:
        """Process a single page image with vision model"""
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Create prompt for invoice data extraction
            prompt = f"""
            This is page {page_num + 1} of an invoice document. Please extract the following information in JSON format:
            
            {{
                "page_number": {page_num + 1},
                "vendor_name": "extract vendor/company name",
                "invoice_number": "extract invoice number",
                "invoice_date": "extract invoice date (YYYY-MM-DD format)",
                "due_date": "extract due date if present (YYYY-MM-DD format)",
                "subtotal": "extract subtotal amount",
                "tax_amount": "extract tax amount",
                "total_amount": "extract total amount",
                "line_items": [
                    {{
                        "description": "item description",
                        "quantity": "quantity",
                        "unit_price": "unit price",
                        "amount": "line total"
                    }}
                ],
                "notes": "any additional notes or observations"
            }}
            
            If any field cannot be found, use null. Be precise and accurate with the data extraction.
            """
            
            # Send to vision model
            completion = self.client.chat.completions.create(
                model=self.model,
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
                max_tokens=1000,
                temperature=0.1,  # Low temperature for consistent extraction
            )
            
            response_text = completion.choices[0].message.content
            logger.info(f"Vision model response for page {page_num + 1}: {response_text[:200]}...")
            
            # Try to parse JSON response
            try:
                # Extract JSON from response (might be wrapped in markdown)
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                else:
                    # Try to find JSON in the response
                    json_str = response_text.strip()
                
                page_data = json.loads(json_str)
                return page_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from vision response: {e}")
                logger.error(f"Raw response: {response_text}")
                return {
                    "page_number": page_num + 1,
                    "error": "Failed to parse vision model response",
                    "raw_response": response_text
                }
                
        except Exception as e:
            logger.error(f"Error processing page {page_num + 1} with vision: {str(e)}")
            return {
                "page_number": page_num + 1,
                "error": str(e)
            }
    
    def merge_page_data(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge data from multiple pages into a single invoice record"""
        merged_data = {
            "vendor_name": None,
            "invoice_number": None,
            "invoice_date": None,
            "due_date": None,
            "subtotal": 0.0,
            "tax_amount": 0.0,
            "total_amount": 0.0,
            "line_items": [],
            "notes": [],
            "pages_processed": len(pages_data)
        }
        
        for page_data in pages_data:
            if "error" in page_data:
                merged_data["notes"].append(f"Page {page_data['page_number']}: {page_data['error']}")
                continue
            
            # Merge vendor name (usually on first page)
            if not merged_data["vendor_name"] and page_data.get("vendor_name"):
                merged_data["vendor_name"] = page_data["vendor_name"]
            
            # Merge invoice number (usually on first page)
            if not merged_data["invoice_number"] and page_data.get("invoice_number"):
                merged_data["invoice_number"] = page_data["invoice_number"]
            
            # Merge dates
            if not merged_data["invoice_date"] and page_data.get("invoice_date"):
                merged_data["invoice_date"] = page_data["invoice_date"]
            if not merged_data["due_date"] and page_data.get("due_date"):
                merged_data["due_date"] = page_data["due_date"]
            
            # Sum amounts
            if page_data.get("subtotal"):
                try:
                    merged_data["subtotal"] += float(page_data["subtotal"])
                except (ValueError, TypeError):
                    pass
            
            if page_data.get("tax_amount"):
                try:
                    merged_data["tax_amount"] += float(page_data["tax_amount"])
                except (ValueError, TypeError):
                    pass
            
            if page_data.get("total_amount"):
                try:
                    merged_data["total_amount"] = float(page_data["total_amount"])
                except (ValueError, TypeError):
                    pass
            
            # Merge line items
            if page_data.get("line_items"):
                merged_data["line_items"].extend(page_data["line_items"])
            
            # Merge notes
            if page_data.get("notes"):
                merged_data["notes"].append(f"Page {page_data['page_number']}: {page_data['notes']}")
        
        return merged_data
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process entire PDF using vision model"""
        logger.info(f"Processing PDF with vision: {pdf_path}")
        
        try:
            # Open PDF and get page count
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            
            logger.info(f"PDF has {page_count} pages")
            
            # Create temporary directory for screenshots
            with tempfile.TemporaryDirectory() as temp_dir:
                pages_data = []
                
                # Process each page
                for page_num in range(page_count):
                    logger.info(f"Processing page {page_num + 1}/{page_count}")
                    
                    # Take screenshot
                    image_path = self.take_page_screenshot(pdf_path, page_num, temp_dir)
                    if not image_path:
                        continue
                    
                    # Process with vision model
                    page_data = self.process_page_with_vision(image_path, page_num)
                    pages_data.append(page_data)
                
                # Merge data from all pages
                merged_data = self.merge_page_data(pages_data)
                
                # Format for ETL system
                result = {
                    "success": True,
                    "file_path": pdf_path,
                    "pages_processed": page_count,
                    "extracted_data": {
                        "headerSection": {
                            "vendorName": merged_data["vendor_name"] or "Unknown Vendor",
                            "subtotal": merged_data["subtotal"]
                        },
                        "billingDetails": {
                            "invoiceNumber": merged_data["invoice_number"] or "Unknown",
                            "invoiceDate": merged_data["invoice_date"] or "2024-01-01"
                        },
                        "chargesSummary": {
                            "document_total": merged_data["total_amount"],
                            "secondary_tax": merged_data["tax_amount"],
                            "lineItemsBreakdown": merged_data["line_items"]
                        }
                    },
                    "raw_pages_data": pages_data,
                    "processing_method": "vision_model",
                    "model_used": self.model
                }
                
                logger.info(f"Vision processing completed for {pdf_path}")
                return result
                
        except Exception as e:
            logger.error(f"Error processing PDF with vision: {str(e)}")
            return {
                "success": False,
                "file_path": pdf_path,
                "error": str(e),
                "processing_method": "vision_model"
            }

def main():
    """Test the vision PDF processor"""
    processor = VisionPDFProcessor()
    
    # Test with a sample PDF
    pdf_path = os.path.abspath("data/invoices/10352259401.PDF")
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print(f"Testing vision PDF processor with: {pdf_path}")
    result = processor.process_pdf(pdf_path)
    
    print("\n" + "="*60)
    print("VISION PROCESSING RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 