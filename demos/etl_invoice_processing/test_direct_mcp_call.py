#!/usr/bin/env python3
"""
Test direct call to MCP bridge server PDF processor
"""

import os
import sys
import asyncio
import json

# Add the MCP bridge server path
sys.path.append('/Users/tarpus/memra/memra-ops')

async def test_direct_mcp_pdf_processor():
    """Test the MCP bridge server PDF processor directly"""
    
    try:
        # Import the MCP bridge server
        from mcp_bridge_server import MCPBridgeServer
        
        # Create a server instance
        postgres_url = 'postgresql://memra:memra123@localhost:5432/memra_invoice_db'
        bridge_secret = 'test-secret-for-development'
        server = MCPBridgeServer(postgres_url, bridge_secret)
        
        # Test PDF processing
        pdf_path = "/Users/tarpus/memra/demos/etl_invoice_processing/data/invoices/10352259401.PDF"
        input_data = {"file": pdf_path}
        
        print(f"Testing direct MCP bridge PDF processor with: {pdf_path}")
        result = await server.pdf_processor(input_data)
        
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get("success"):
            extracted_data = result.get("data", {}).get("extracted_data", {})
            vendor = extracted_data.get("headerSection", {}).get("vendorName", "Unknown")
            invoice = extracted_data.get("billingDetails", {}).get("invoiceNumber", "Unknown")
            total = extracted_data.get("chargesSummary", {}).get("document_total", 0)
            
            print(f"\nExtracted Data:")
            print(f"  Vendor: {vendor}")
            print(f"  Invoice: {invoice}")
            print(f"  Total: ${total}")
            
            if "Superior Propane" in vendor or "50450014" in invoice:
                print("✅ Real data extracted by vision model!")
            else:
                print("⚠️  Mock data used")
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_mcp_pdf_processor()) 