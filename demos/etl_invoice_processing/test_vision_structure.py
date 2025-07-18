#!/usr/bin/env python3
"""
Test vision processor result structure
"""

import os
import sys
sys.path.append('/Users/tarpus/memra/demos/etl_invoice_processing')

from vision_pdf_processor import VisionPDFProcessor

def test_vision_structure():
    """Test the structure of vision processor result"""
    
    processor = VisionPDFProcessor()
    pdf_path = "/Users/tarpus/memra/demos/etl_invoice_processing/data/invoices/10352259401.PDF"
    
    print("Testing vision processor structure...")
    result = processor.process_pdf(pdf_path)
    
    print(f"Result keys: {list(result.keys())}")
    print(f"Success: {result.get('success')}")
    
    if result.get('success'):
        print(f"Extracted data keys: {list(result.get('extracted_data', {}).keys())}")
        print(f"Header section: {result.get('extracted_data', {}).get('headerSection', {})}")
        print(f"Billing details: {result.get('extracted_data', {}).get('billingDetails', {})}")
        print(f"Charges summary: {result.get('extracted_data', {}).get('chargesSummary', {})}")
        
        # Check if this matches what MCP bridge expects
        expected_structure = {
            "success": True,
            "data": {
                "file_path": pdf_path,
                "text_content": "PDF processed with vision model",
                "extracted_data": result["extracted_data"]
            }
        }
        
        print(f"\nExpected structure for MCP bridge:")
        print(f"  - success: {expected_structure['success']}")
        print(f"  - data.file_path: {expected_structure['data']['file_path']}")
        print(f"  - data.text_content: {expected_structure['data']['text_content']}")
        print(f"  - data.extracted_data: {list(expected_structure['data']['extracted_data'].keys())}")

if __name__ == "__main__":
    test_vision_structure() 