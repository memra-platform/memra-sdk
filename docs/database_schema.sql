-- Memra MCP Integration Database Schema
-- This file contains the database schema required for MCP integration
-- Run this script to create the necessary tables for invoice processing

-- Create database (run this as postgres superuser if needed)
-- CREATE DATABASE memra_invoice_db;

-- Connect to your database and run the following:

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL,
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

-- Create a trigger to automatically update the updated_at timestamp
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

-- Table description:
-- id: Primary key, auto-incrementing
-- invoice_number: Invoice identifier (can have duplicates as per requirements)
-- vendor_name: Name of the vendor/supplier
-- invoice_date: Date the invoice was issued
-- due_date: Payment due date (optional)
-- total_amount: Total invoice amount (must be positive)
-- tax_amount: Tax portion of the invoice (optional)
-- line_items: JSON array of invoice line items with structure:
--   [
--     {
--       "description": "Item description",
--       "quantity": number,
--       "unit_price": number,
--       "amount": number,
--       "main_product": boolean
--     }
--   ]
-- status: Invoice processing status (default: 'pending')
-- created_at: Record creation timestamp
-- updated_at: Last update timestamp (auto-updated)

-- Verify the setup
SELECT 'Database schema setup complete!' as status; 