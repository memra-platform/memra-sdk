import psycopg2
import json

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='memra_invoice_db',
        user='memra',
        password='memra123'
    )
    
    cursor = conn.cursor()
    
    # Get detailed records
    cursor.execute('SELECT * FROM invoices ORDER BY created_at DESC LIMIT 5;')
    rows = cursor.fetchall()
    
    print('📄 Detailed Invoice Records:')
    for row in rows:
        print(f'\nID: {row[0]}')
        print(f'  Invoice Number: {row[1]}')
        print(f'  Vendor: {row[2]}')
        print(f'  Invoice Date: {row[3]}')
        print(f'  Due Date: {row[4]}')
        print(f'  Total Amount: ${row[5]}')
        print(f'  Tax Amount: ${row[6]}')
        print(f'  Status: {row[8]}')
        print(f'  Created: {row[9]}')
        
        if row[7]:  # line_items
            try:
                line_items = json.loads(row[7])
                print(f'  Line Items: {len(line_items)} items')
                for i, item in enumerate(line_items[:2]):  # Show first 2 items
                    print(f'    {i+1}. {item.get("description", "N/A")} - Qty: {item.get("quantity", "N/A")} @ ${item.get("unit_price", "N/A")}')
            except:
                print(f'  Line Items: {row[7]}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Database connection failed: {e}') 