#!/usr/bin/env python3
"""
Test script to verify vision response conversion
"""

import json

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
            ""
        )
        
        tax_amount = (
            data.get("tax_amount") or 
            data.get("TaxAmount") or 
            data.get("taxAmount") or 
            0
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
                "dueDate": ""
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

def test_conversion():
    """Test the conversion function with actual vision model response"""
    
    # This is the actual response from our test
    vision_response = '''```json
{
  "InvoiceDate": "09/16/24",
  "InvoiceNumber": "50482291",
  "AccountNumber": "203258",
  "InvoiceTotal": "197.79",
  "Order": [
    {
      "Date": "09/16/24",
      "OrderNumber": "923785",
      "QuantityDelivered": "6.0",
      "Description": "331L CYL AL/BOUT 331L",
      "UnitPrice": "22.174",
      "ExtendedTotal": "133.04"
    },
    {
      "Description": "CARBURN TAX",
      "ExtendedTotal": "11.94"
    },
    {
      "Description": "FUEL CHARGE",
      "ExtendedTotal": "22.06"
    },
    {
      "Description": "DANG - HST / F/P/ PRAIS MAT.",
      "ExtendedTotal": "4.95"
    },
    {
      "Description": "GST - HST / TPS - TVH",
      "ExtendedTotal": "25.80"
    }
  ]
}
```'''
    
    print("🧪 Testing Vision Response Conversion")
    print("=" * 50)
    
    print(f"\n📄 Original Vision Response:")
    print(vision_response)
    
    print(f"\n🔄 Converting to extracted_data format...")
    extracted_data = convert_vision_response_to_extracted_data(vision_response)
    
    print(f"\n✅ Converted Data:")
    print(json.dumps(extracted_data, indent=2))
    
    # Verify the conversion worked
    vendor = extracted_data["headerSection"]["vendorName"]
    invoice_num = extracted_data["billingDetails"]["invoiceNumber"]
    amount = extracted_data["chargesSummary"]["document_total"]
    
    print(f"\n🎯 Key Fields:")
    print(f"   Vendor: '{vendor}'")
    print(f"   Invoice #: '{invoice_num}'")
    print(f"   Amount: ${amount}")
    
    if invoice_num == "50482291" and amount == 197.79:
        print("✅ Conversion successful!")
    else:
        print("❌ Conversion failed!")

if __name__ == "__main__":
    test_conversion() 