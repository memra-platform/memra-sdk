import psycopg2

def clear_database():
    """Clear all data from the invoices table"""
    
    # Connect to the Postgres database
    conn = psycopg2.connect(
        dbname="memra_invoice_db",
        user="memra",          # From docker-compose.yml
        password="memra123",   # From docker-compose.yml
        host="localhost",
        port=5432
    )

    try:
        # Create a cursor and run the query
        cur = conn.cursor()
        
        # First, let's see how many rows we have
        cur.execute("SELECT COUNT(*) FROM invoices;")
        count_before = cur.fetchone()[0]
        print(f"📊 Current invoice count: {count_before}")
        
        if count_before > 0:
            # Clear all data from the invoices table
            cur.execute("DELETE FROM invoices;")
            conn.commit()
            
            # Verify the deletion
            cur.execute("SELECT COUNT(*) FROM invoices;")
            count_after = cur.fetchone()[0]
            
            print(f"🗑️  Deleted {count_before} invoice records")
            print(f"📊 New invoice count: {count_after}")
            print("✅ Database cleared successfully!")
        else:
            print("📊 Database is already empty")
        
        cur.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_database() 