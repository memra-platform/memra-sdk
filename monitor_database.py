import psycopg2
from prettytable import PrettyTable
import time
import os

def monitor_database():
    """Continuously monitor the database for new invoice rows"""
    
    # Connect to the Postgres database
    conn = psycopg2.connect(
        dbname="memra_invoice_db",
        user="memra",          # From docker-compose.yml
        password="memra123",   # From docker-compose.yml
        host="localhost",
        port=5432
    )

    print("🔍 Monitoring database for new invoice rows...")
    print("Press Ctrl+C to stop monitoring\n")
    
    last_count = 0
    
    try:
        while True:
            # Create a cursor and run the query
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM invoices;")
            current_count = cur.fetchone()[0]
            
            # Get the latest invoices
            cur.execute("SELECT id, invoice_number, vendor_name, total_amount, created_at FROM invoices ORDER BY created_at DESC LIMIT 5;")
            rows = cur.fetchall()
            
            # Clear screen (works on Unix-like systems)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print(f"📊 Database Monitor - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total invoices: {current_count}")
            
            if current_count > last_count:
                print(f"🆕 New invoices detected! (+{current_count - last_count})")
                last_count = current_count
            
            if rows:
                # Create and populate the pretty table
                table = PrettyTable()
                table.field_names = ["ID", "Invoice #", "Vendor", "Amount", "Created"]
                for row in rows:
                    table.add_row(row)
                print("\nLatest invoices:")
                print(table)
            else:
                print("\nNo invoices found in database.")
            
            print(f"\nMonitoring... (refresh every 2 seconds)")
            cur.close()
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    monitor_database() 