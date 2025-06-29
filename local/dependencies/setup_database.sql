-- Memra Invoice Processing Database Setup
-- Run this script to create the database schema for invoice processing workflows

-- Create database (run this as postgres superuser)
-- CREATE DATABASE memra_invoice_db;

-- Connect to the database and run the following:

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    vendor_name VARCHAR(255) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),
    tax_amount DECIMAL(10,2),
    line_items JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_vendor_name ON invoices(vendor_name);
CREATE INDEX IF NOT EXISTS idx_status ON invoices(status);

-- Create a trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_invoices_updated_at 
    BEFORE UPDATE ON invoices 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
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
    '[
        {
            "description": "Sample Product",
            "quantity": 10,
            "unit_price": 100.00,
            "amount": 1000.00,
            "main_product": true
        },
        {
            "description": "Delivery Fee",
            "quantity": 1,
            "unit_price": 111.11,
            "amount": 111.11,
            "main_product": false
        }
    ]'::jsonb,
    'processed'
),
(
    'SAMPLE-002',
    'Another Vendor LLC',
    '2024-01-20',
    567.89,
    56.78,
    '[
        {
            "description": "Service Fee",
            "quantity": 1,
            "unit_price": 500.00,
            "amount": 500.00,
            "main_product": true
        },
        {
            "description": "Tax",
            "quantity": null,
            "unit_price": null,
            "amount": 11.11,
            "main_product": false
        }
    ]'::jsonb,
    'pending'
);

-- Verify the setup
SELECT 'Database setup complete!' as status;
SELECT COUNT(*) as sample_records FROM invoices; 