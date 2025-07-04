import psycopg2
from prettytable import PrettyTable
import time

def check_database():
    # Connect to the Postgres database
    conn = psycopg2.connect(
        dbname="memra_invoice_db",
        user="memra",          # From docker-compose.yml
        password="memra123",   # From docker-compose.yml
        host="localhost",
        port=5432
    )

    # Create a cursor and run the query
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices ORDER BY created_at DESC LIMIT 10;")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    # Create and populate the pretty table
    table = PrettyTable()
    table.field_names = columns
    for row in rows:
        table.add_row(row)

    # Print the table
    print(f"\n📊 Current invoices in database (as of {time.strftime('%H:%M:%S')}):")
    print(table)
    print(f"Total rows: {len(rows)}")

    # Clean up
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_database()
