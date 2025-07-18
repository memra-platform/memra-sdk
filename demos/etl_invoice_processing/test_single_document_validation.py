#!/usr/bin/env python3
"""
Test Single Document Validation
This script tests the complete data extraction pipeline for a single document
to validate that the extracted data is accurate and not hallucinated.
"""

import os
import sys
import json
import requests
import PyPDF2
from typing import Dict, Any
sys.path.append('/Users/tarpus/memra')

def test_pdf_text_extraction(pdf_path: str) -> Dict[str, Any]:
    """Test raw PDF text extraction"""
    print(f"📄 Testing PDF text extraction for: {pdf_path}")
    print("=" * 60)
    
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        text_content = ""
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text_content += f"\n--- PAGE {i+1} ---\n{page_text}\n"
        
        print(f"✅ PDF loaded successfully")
        print(f"📊 Pages: {len(reader.pages)}")
        print(f"📝 Text length: {len(text_content)} characters")
        print(f"📄 First 500 characters:")
        print(text_content[:500])
        print(f"📄 Last 500 characters:")
        print(text_content[-500:])
        
        return {
            "success": True,
            "pages": len(reader.pages),
            "text_length": len(text_content),
            "text_content": text_content
        }
        
    except Exception as e:
        print(f"❌ PDF text extraction failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def test_pdf_processor_tool(pdf_path: str) -> Dict[str, Any]:
    """Test the PDFProcessor tool directly"""
    print(f"\n🔧 Testing PDFProcessor tool for: {pdf_path}")
    print("=" * 60)
    
    try:
        # Call the MCP bridge server directly
        url = "http://localhost:8082/execute_tool"
        headers = {
            "Content-Type": "application/json",
            "X-Bridge-Secret": "test-secret-for-development"
        }
        
        payload = {
            "tool_name": "PDFProcessor",
            "input_data": {
                "file": pdf_path
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PDFProcessor tool executed successfully")
            print(f"📊 Response keys: {list(result.keys())}")
            
            # Extract the actual data
            extracted_data = result.get('data', {}).get('extracted_data', {})
            print(f"📋 Extracted data structure:")
            print(json.dumps(extracted_data, indent=2))
            
            return {
                "success": True,
                "result": result,
                "extracted_data": extracted_data
            }
        else:
            print(f"❌ PDFProcessor tool failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        print(f"❌ PDFProcessor tool test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def validate_extracted_data(extracted_data: Dict[str, Any], pdf_path: str) -> Dict[str, Any]:
    """Validate the extracted data for accuracy"""
    print(f"\n🔍 Validating extracted data for: {pdf_path}")
    print("=" * 60)
    
    validation_results = {
        "overall_valid": True,
        "issues": [],
        "warnings": [],
        "field_analysis": {}
    }
    
    # Extract key sections
    header = extracted_data.get('headerSection', {})
    billing = extracted_data.get('billingDetails', {})
    charges = extracted_data.get('chargesSummary', {})
    
    # Validate vendor name
    vendor_name = header.get('vendorName', '')
    validation_results["field_analysis"]["vendor_name"] = {
        "value": vendor_name,
        "valid": vendor_name != '' and vendor_name != 'Unknown Vendor',
        "issues": []
    }
    
    if not vendor_name or vendor_name == 'Unknown Vendor':
        validation_results["field_analysis"]["vendor_name"]["issues"].append("Empty or default vendor name")
        validation_results["issues"].append("Invalid vendor name")
    
    # Validate invoice number
    invoice_number = billing.get('invoiceNumber', '')
    expected_invoice_number = os.path.basename(pdf_path).replace('.PDF', '')
    validation_results["field_analysis"]["invoice_number"] = {
        "value": invoice_number,
        "expected": expected_invoice_number,
        "valid": invoice_number == expected_invoice_number,
        "issues": []
    }
    
    if invoice_number != expected_invoice_number:
        validation_results["field_analysis"]["invoice_number"]["issues"].append(f"Expected {expected_invoice_number}, got {invoice_number}")
        validation_results["issues"].append("Invoice number mismatch")
    
    # Validate invoice date
    invoice_date = billing.get('invoiceDate', '')
    validation_results["field_analysis"]["invoice_date"] = {
        "value": invoice_date,
        "valid": bool(invoice_date) and invoice_date != '2024-01-01',
        "issues": []
    }
    
    if not invoice_date or invoice_date == '2024-01-01':
        validation_results["field_analysis"]["invoice_date"]["issues"].append("Empty or default date")
        validation_results["issues"].append("Invalid invoice date")
    
    # Validate total amount
    total_amount = charges.get('document_total', 0)
    validation_results["field_analysis"]["total_amount"] = {
        "value": total_amount,
        "valid": total_amount > 0 and total_amount < 10000,  # Reasonable range
        "issues": []
    }
    
    if total_amount <= 0 or total_amount >= 10000:
        validation_results["field_analysis"]["total_amount"]["issues"].append(f"Amount {total_amount} seems unreasonable")
        validation_results["issues"].append("Invalid total amount")
    
    # Validate line items
    line_items = charges.get('lineItemsBreakdown', [])
    validation_results["field_analysis"]["line_items"] = {
        "count": len(line_items),
        "valid": len(line_items) > 0,
        "issues": []
    }
    
    if len(line_items) == 0:
        validation_results["field_analysis"]["line_items"]["issues"].append("No line items found")
        validation_results["issues"].append("Missing line items")
    
    # Overall validation
    validation_results["overall_valid"] = len(validation_results["issues"]) == 0
    
    # Print validation results
    print(f"📊 Validation Results:")
    print(f"   Overall Valid: {'✅' if validation_results['overall_valid'] else '❌'}")
    print(f"   Issues Found: {len(validation_results['issues'])}")
    print(f"   Warnings: {len(validation_results['warnings'])}")
    
    print(f"\n📋 Field Analysis:")
    for field, analysis in validation_results["field_analysis"].items():
        status = "✅" if analysis.get("valid", False) else "❌"
        print(f"   {field}: {status} {analysis.get('value', 'N/A')}")
        if analysis.get("issues"):
            for issue in analysis["issues"]:
                print(f"      ⚠️  {issue}")
    
    if validation_results["issues"]:
        print(f"\n❌ Issues Found:")
        for issue in validation_results["issues"]:
            print(f"   • {issue}")
    
    return validation_results

def test_full_pipeline_single_document(pdf_path: str) -> Dict[str, Any]:
    """Test the full pipeline for a single document"""
    print(f"\n🚀 Testing Full Pipeline for: {pdf_path}")
    print("=" * 80)
    
    results = {
        "pdf_path": pdf_path,
        "pdf_text_test": None,
        "pdf_processor_test": None,
        "validation_results": None,
        "overall_success": False
    }
    
    # Step 1: Test PDF text extraction
    results["pdf_text_test"] = test_pdf_text_extraction(pdf_path)
    
    # Step 2: Test PDFProcessor tool
    results["pdf_processor_test"] = test_pdf_processor_tool(pdf_path)
    
    # Step 3: Validate extracted data
    if results["pdf_processor_test"]["success"]:
        extracted_data = results["pdf_processor_test"]["extracted_data"]
        results["validation_results"] = validate_extracted_data(extracted_data, pdf_path)
        results["overall_success"] = results["validation_results"]["overall_valid"]
    
    # Summary
    print(f"\n📊 SUMMARY FOR {pdf_path}")
    print("=" * 60)
    print(f"PDF Text Extraction: {'✅' if results['pdf_text_test']['success'] else '❌'}")
    print(f"PDFProcessor Tool: {'✅' if results['pdf_processor_test']['success'] else '❌'}")
    print(f"Data Validation: {'✅' if results['validation_results'] and results['validation_results']['overall_valid'] else '❌'}")
    print(f"Overall Success: {'✅' if results['overall_success'] else '❌'}")
    
    return results

def main():
    """Main test function"""
    print("🧪 SINGLE DOCUMENT VALIDATION TEST")
    print("=" * 80)
    
    # Test with a specific invoice file (use absolute path)
    pdf_path = os.path.abspath("data/invoices/10352259401.PDF")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Run the full test
    results = test_full_pipeline_single_document(pdf_path)
    
    # Save results to file
    output_file = "single_document_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    if results["overall_success"]:
        print(f"\n🎉 Document validation PASSED!")
    else:
        print(f"\n💥 Document validation FAILED!")
        print(f"Check the detailed results above and in {output_file}")

if __name__ == "__main__":
    main() 