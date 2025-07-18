#!/usr/bin/env python3
"""
Test Vision PDF Processor through MCP Bridge
"""

import os
import sys
import json
import requests
sys.path.append('/Users/tarpus/memra')

def test_vision_pdf_processor(pdf_path: str):
    """Test the vision PDF processor through MCP bridge"""
    
    # Prepare the request
    payload = {
        "tool_name": "PDFProcessor",
        "input_data": {
            "file": pdf_path
        }
    }
    
    # Add bridge secret for authentication
    headers = {
        "Content-Type": "application/json",
        "X-Bridge-Secret": "test-secret-for-development"
    }
    
    # Send request to MCP bridge
    try:
        response = requests.post(
            "http://localhost:8082/execute_tool",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Vision PDF Processor Test Result:")
            print("=" * 60)
            print(json.dumps(result, indent=2))
            
            # Check if vision processing was used
            if result.get("success") and "data" in result:
                extracted_data = result["data"].get("extracted_data", {})
                vendor_name = extracted_data.get("headerSection", {}).get("vendorName", "")
                invoice_number = extracted_data.get("billingDetails", {}).get("invoiceNumber", "")
                total_amount = extracted_data.get("chargesSummary", {}).get("document_total", 0)
                
                print(f"\n📊 Extracted Data Summary:")
                print(f"   Vendor: {vendor_name}")
                print(f"   Invoice Number: {invoice_number}")
                print(f"   Total Amount: ${total_amount}")
                
                # Check if this looks like real data vs mock data
                if vendor_name and vendor_name != "Unknown Vendor" and total_amount > 0:
                    print(f"✅ This appears to be REAL data extracted by vision model!")
                else:
                    print(f"⚠️  This appears to be mock/fallback data")
                    
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing vision PDF processor: {str(e)}")

def main():
    """Main test function"""
    print("🔍 Testing Vision PDF Processor through MCP Bridge")
    print("=" * 60)
    
    # Test with the same PDF we used before
    pdf_path = os.path.abspath("data/invoices/10352259401.PDF")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"📁 Testing with: {pdf_path}")
    test_vision_pdf_processor(pdf_path)

if __name__ == "__main__":
    main() 