import psycopg2

def reset_database():
    """Clear all data from the invoices table and reset the sequence"""
    
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
        
        # First, let's see how many rows we have and current sequence value
        cur.execute("SELECT COUNT(*) FROM invoices;")
        count_before = cur.fetchone()[0]
        
        cur.execute("SELECT last_value FROM invoices_id_seq;")
        sequence_before = cur.fetchone()[0]
        
        print(f"📊 Current invoice count: {count_before}")
        print(f"🔢 Current sequence value: {sequence_before}")
        
        if count_before > 0:
            # Clear all data from the invoices table
            cur.execute("DELETE FROM invoices;")
            
            # Reset the sequence to start from 1
            cur.execute("ALTER SEQUENCE invoices_id_seq RESTART WITH 1;")
            
            conn.commit()
            
            # Verify the deletion and sequence reset
            cur.execute("SELECT COUNT(*) FROM invoices;")
            count_after = cur.fetchone()[0]
            
            cur.execute("SELECT last_value FROM invoices_id_seq;")
            sequence_after = cur.fetchone()[0]
            
            print(f"🗑️  Deleted {count_before} invoice records")
            print(f"🔄 Reset sequence from {sequence_before} to {sequence_after}")
            print(f"📊 New invoice count: {count_after}")
            print("✅ Database reset successfully!")
        else:
            print("📊 Database is already empty")
            # Still reset the sequence
            cur.execute("ALTER SEQUENCE invoices_id_seq RESTART WITH 1;")
            conn.commit()
            print("🔄 Reset sequence to start from 1")
        
        cur.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_database() 