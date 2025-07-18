#!/usr/bin/env python3
"""
Simulate MCP bridge server PDF processing
"""

import os
import sys
import asyncio

# Simulate the MCP bridge server context
sys.path.append('/Users/tarpus/memra/demos/etl_invoice_processing')

async def simulate_mcp_pdf_processing(file_path: str):
    """Simulate exactly what the MCP bridge server does"""
    
    print(f"Simulating MCP bridge PDF processing for: {file_path}")
    
    try:
        # Import vision processor (like MCP bridge does)
        print("1. Importing vision processor...")
        from vision_pdf_processor import VisionPDFProcessor
        print("✅ Vision processor imported successfully!")
        
        # Initialize vision processor
        print("2. Initializing vision processor...")
        processor = VisionPDFProcessor()
        print("✅ Vision processor initialized successfully!")
        
        # Process PDF with vision (run in executor since it's synchronous)
        print("3. Processing PDF with vision...")
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, processor.process_pdf, file_path)
        print(f"✅ Vision processing completed: {result.get('success', False)}")
        
        if result.get("success"):
            print("4. Vision processing succeeded!")
            print(f"   Vendor: {result['extracted_data']['headerSection']['vendorName']}")
            print(f"   Invoice: {result['extracted_data']['billingDetails']['invoiceNumber']}")
            print(f"   Total: ${result['extracted_data']['chargesSummary']['document_total']}")
            
            # Return the result in MCP bridge format
            return {
                "success": True,
                "data": {
                    "file_path": file_path,
                    "text_content": "PDF processed with vision model",
                    "extracted_data": result["extracted_data"]
                }
            }
        else:
            print(f"❌ Vision processing failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": "Vision processing failed"}
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return {"success": False, "error": f"Import error: {e}"}
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Error: {e}"}

async def main():
    """Main test function"""
    pdf_path = "/Users/tarpus/memra/demos/etl_invoice_processing/data/invoices/10352259401.PDF"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    result = await simulate_mcp_pdf_processing(pdf_path)
    
    print(f"\nFinal result: {result}")

if __name__ == "__main__":
    asyncio.run(main()) 