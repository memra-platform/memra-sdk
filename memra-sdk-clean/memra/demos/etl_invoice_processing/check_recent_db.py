import psycopg2
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="local_workflow",
    user="postgres",
    password="postgres",
    port=5433
)

try:
    with conn.cursor() as cur:
        # Get the 10 most recent records
        cur.execute("""
            SELECT id, vendor_name, invoice_number, invoice_date, due_date, 
                   total_amount, tax_amount, created_at
            FROM invoices
            ORDER BY id DESC
            LIMIT 10
        """)
        
        records = cur.fetchall()
        
        if records:
            print("🔍 Most Recent Invoice Records:\n")
            for record in records:
                id, vendor, invoice_num, inv_date, due_date, total, tax, created = record
                print(f"ID: {id} (Created: {created})")
                print(f"  Vendor: {vendor}")
                print(f"  Invoice #: {invoice_num}")
                print(f"  Invoice Date: {inv_date}")
                print(f"  Due Date: {due_date}")
                print(f"  Total: ${total:.2f}")
                print(f"  Tax: ${tax:.2f}")
                print("-" * 40)
        else:
            print("No records found in database")
            
finally:
    conn.close()