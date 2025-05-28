# Memra Team Setup Guide

This guide will help you set up the database for the Memra invoice processing system.

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/memra-platform/memra-sdk.git
cd memra-sdk
```

### 2. Set Up Python Environment

```bash
# Create conda environment
conda create -n memra python=3.10
conda activate memra

# Install dependencies
pip install -e .
```

### 3. Set Up Database

**Option A: Docker (Recommended)**
```bash
# Start database with Docker Compose
docker-compose up -d

# Verify it's running
docker ps | grep postgres
```

**Option B: Local PostgreSQL**
```bash
# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb memra_invoice_db

# Run setup script
psql memra_invoice_db < local/dependencies/setup_database.sql
```

### 4. Update Connection String

Edit `examples/accounts_payable.py` line 147:

```python
# Update with your database credentials
"connection": "postgresql://memra:memra123@localhost:5432/memra_invoice_db"  # Docker
# OR
"connection": "postgresql://your_username@localhost:5432/memra_invoice_db"  # Local PostgreSQL
```

### 5. Get API Key from Team Lead

Contact your team lead for a Memra API key, then set it:

```bash
# Set environment variable (required for API access)
export MEMRA_API_KEY="your-api-key-from-team-lead"

# Optional: Add to shell profile for persistence
echo 'export MEMRA_API_KEY="your-api-key-from-team-lead"' >> ~/.zshrc
```

## 🧪 Test the Setup

### 1. Test Database Connection

```bash
# Docker
psql postgresql://memra:memra123@localhost:5432/memra_invoice_db -c "SELECT COUNT(*) FROM invoices;"

# Local PostgreSQL  
psql memra_invoice_db -c "SELECT COUNT(*) FROM invoices;"
```

Should return: `count: 2` (sample records)

### 2. Test API Access

```bash
# Test that your API key works
python examples/accounts_payable_client.py
```

Expected output:
- ✅ API Health check passes
- 🚀 Workflow starts successfully
- 📡 Tools execute remotely on Memra API

### 3. View Sample Data

```bash
# Connect to database
psql postgresql://memra:memra123@localhost:5432/memra_invoice_db

# View sample invoices
SELECT invoice_number, vendor_name, total_amount FROM invoices;
```

## 📋 System Dependencies

- **Python 3.10+**
- **PostgreSQL** (or Docker)
- **poppler-utils** (for PDF processing):
  ```bash
  # macOS
  brew install poppler
  
  # Ubuntu/Debian
  sudo apt-get install poppler-utils
  ```

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
pg_isready

# Check Docker container
docker ps | grep postgres

# Restart Docker container
docker-compose restart
```

### Import Errors
```bash
# Reinstall in development mode
pip install -e .
```

## 📁 Database Schema

The `invoices` table includes:
- **invoice_number**: Unique invoice identifier
- **vendor_name**: Company/vendor name  
- **invoice_date**: Date of the invoice
- **total_amount**: Total invoice amount
- **tax_amount**: Tax portion (if any)
- **line_items**: JSON array of invoice line items
- **status**: Processing status (pending, processed, etc.)

See `local/dependencies/setup_database.sql` for complete schema.

## 🆘 Need Help?

- **Database Setup**: See `local/dependencies/README.md`
- **Schema Questions**: Check `local/dependencies/setup_database.sql`
- **General Issues**: Contact team lead

Happy coding! 🚀 