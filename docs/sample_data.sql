-- Sample data for memra_invoice_db
-- This file contains sample invoice data for development/testing

INSERT INTO invoices (
    invoice_number, 
    vendor_name, 
    invoice_date, 
    total_amount, 
    tax_amount, 
    line_items, 
    status
) VALUES 
(
    'SAMPLE-001',
    'Sample Vendor Corp',
    '2024-01-15',
    1234.56,
    123.45,
    '[{"amount": 1000.0, "quantity": 10, "unit_price": 100.0, "description": "Sample Product", "main_product": true}, {"amount": 111.11, "quantity": 1, "unit_price": 111.11, "description": "Delivery Fee", "main_product": false}]',
    'processed'
),
(
    'SAMPLE-002',
    'Another Vendor LLC',
    '2024-01-20',
    567.89,
    56.78,
    '[{"amount": 500.0, "quantity": 1, "unit_price": 500.0, "description": "Service Fee", "main_product": true}, {"amount": 11.11, "quantity": null, "unit_price": null, "description": "Tax", "main_product": false}]',
    'pending'
),
(
    '77861009',
    'Air Liquide Canada Inc.',
    '2024-09-19',
    660.03,
    75.93,
    '[{"amount": 472.8, "quantity": 30.0, "unit_price": 15.76, "description": "PROPANE, C3H8, 33 1/3LB, (14KG / 30.8LB)", "main_product": true}, {"amount": 0.0, "quantity": 30.0, "unit_price": 0, "description": "EMPTY CYLINDER PROPANE, 30.8LB (14KG)", "main_product": false}, {"amount": 0.0, "quantity": 1.0, "unit_price": 0, "description": "CHARGE, FUEL SURCHARGE", "main_product": false}, {"amount": 111.3, "quantity": 30.0, "unit_price": 3.71, "description": "CHARGE, CARBON TAX PROPANE, ON, NB, SASK, MANITOBA, 33 1/3LB CYLINDER", "main_product": false}]',
    'processed'
); 