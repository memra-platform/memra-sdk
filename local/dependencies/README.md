# Database Setup for Memra Invoice Processing

This directory contains the database schema and setup files needed to run the invoice processing workflow.

## Quick Setup

### Option 1: PostgreSQL (Recommended)

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # macOS
   brew install postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database**:
   ```bash
   # Start PostgreSQL service
   brew services start postgresql  # macOS
   sudo service postgresql start   # Linux
   
   # Create database
   createdb memra_invoice_db
   ```

3. **Run Setup Script**:
   ```bash
   psql memra_invoice_db < local/dependencies/setup_database.sql
   ```

4. **Update Connection String** in your code:
   ```python
   "connection": "postgresql://your_username@localhost:5432/memra_invoice_db"
   ```

### Option 2: Docker (Easiest)

1. **Create docker-compose.yml**:
   ```yaml
   version: '3.8'
   services:
     postgres:
       image: postgres:15
       environment:
         POSTGRES_DB: memra_invoice_db
         POSTGRES_USER: memra
         POSTGRES_PASSWORD: memra123
       ports:
         - "5432:5432"
       volumes:
         - ./local/dependencies/setup_database.sql:/docker-entrypoint-initdb.d/setup.sql
   ```

2. **Start Database**:
   ```bash
   docker-compose up -d
   ```

3. **Use Connection String**:
   ```python
   "connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db"
   ```

## Database Schema

The `invoices` table includes:

- **id**: Primary key (auto-increment)
- **invoice_number**: Unique invoice identifier
- **vendor_name**: Company/vendor name
- **invoice_date**: Date of the invoice
- **total_amount**: Total invoice amount
- **tax_amount**: Tax portion (if any)
- **line_items**: JSON array of invoice line items
- **status**: Processing status (pending, processed, etc.)
- **created_at/updated_at**: Timestamps

## Sample Data

The setup script includes sample invoices to test the workflow:
- SAMPLE-001: Sample Vendor Corp ($1,234.56)
- SAMPLE-002: Another Vendor LLC ($567.89)

## Files

- `data_model.json`: JSON schema definition
- `setup_database.sql`: Complete database setup script
- `README.md`: This file

## Testing the Setup

After setup, verify with:

```sql
-- Connect to database
psql memra_invoice_db

-- Check tables
\dt

-- View sample data
SELECT invoice_number, vendor_name, total_amount FROM invoices;
```

## Troubleshooting

**Connection Issues:**
- Ensure PostgreSQL is running
- Check username/password in connection string
- Verify database name exists

**Permission Issues:**
- Make sure your user has CREATE privileges
- For Docker, use the credentials from docker-compose.yml

**Port Conflicts:**
- Default PostgreSQL port is 5432
- Change port in docker-compose.yml if needed 