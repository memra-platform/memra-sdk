# Memra Installation Guide for Newbies

This guide will walk you through installing Memra and running the ETL workflow on a completely fresh machine. We'll cover everything from basic prerequisites to running the demo.

## 🎯 What You'll Accomplish

By the end of this guide, you'll have:
- ✅ Memra SDK installed and working
- ✅ PostgreSQL database running
- ✅ MCP bridge server running
- ✅ ETL workflow processing PDF invoices
- ✅ Data stored in PostgreSQL database

## 📋 Repository Structure

The Memra SDK repository includes everything needed to run the ETL demo:

- **`memra/`** - Core SDK library
- **`demos/etl_invoice_processing/`** - Complete ETL workflow demo
- **`memra-ops/`** - Infrastructure files (Docker Compose, MCP bridge server)
- **`memra-workflows/`** - Production workflow templates
- **`docs/`** - Database schema and sample data
- **`examples/`** - Additional workflow examples

**Note**: The SDK repo uses git submodules to provide access to infrastructure and workflow templates. The sparse checkout gives you minimal access to essential files only.

### 🔧 Submodule Access

The SDK repository includes two submodules:
- **memra-ops/**: Infrastructure files (Docker Compose, MCP bridge server)
- **memra-workflows/**: Production workflow templates

**Sparse Checkout Benefits:**
- Downloads only essential files (< 1MB total)
- Maintains expected directory structure
- Provides access to ETL demo and basic workflows
- Keeps private repository content secure

**To get full access to all files:**
```bash
git -C memra-ops sparse-checkout disable
git -C memra-workflows sparse-checkout disable
```

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows (WSL recommended for Windows)
- **Python**: 3.8 or higher
- **Memory**: At least 4GB RAM
- **Storage**: At least 2GB free space
- **Internet**: Required for downloading packages and models

### Required Software
1. **Python 3.8+** - [Download here](https://www.python.org/downloads/)
2. **Git** - [Download here](https://git-scm.com/downloads)
3. **Docker** - [Download here](https://www.docker.com/products/docker-desktop/)
4. **PostgreSQL** (we'll use Docker for this)

## 🚀 Step-by-Step Installation

### Step 1: Verify Prerequisites

First, let's make sure you have the required software:

```bash
# Check Python version (should be 3.8 or higher)
python3 --version

# Check Git
git --version

# Check Docker
docker --version

# Check if Docker is running
docker ps
```

**If any of these fail:**
- Install the missing software from the links above
- For Docker, make sure Docker Desktop is running

### Step 2: Clone the Repository

```bash
# Clone the Memra repository with submodules (shallow for minimal download)
git clone --recurse-submodules --shallow-submodules --depth 1 https://github.com/memra-platform/memra-sdk.git

# Navigate to the project directory
cd memra-sdk

# Setup sparse checkout for minimal download (optional)
bash scripts/setup_submodules.sh

# Verify you're in the right place
ls -la
```

You should see files like `README.md`, `setup.py`, `memra/`, `memra-ops/`, and `memra-workflows/`.

**Note:** The submodules provide:
- **memra-ops/**: Docker Compose files and MCP bridge server
- **memra-workflows/**: Production workflow templates

### Step 3: Install Memra SDK

```bash
# Install Memra from PyPI (recommended for most users)
pip install memra

# OR install in development mode (if you want to modify the code)
pip install -e .
```

**Verify installation:**
```bash
# Check if Memra is installed
python3 -c "import memra; print('Memra installed successfully!')"
```

### Step 4: Set Up PostgreSQL Database

We'll use Docker Compose from the memra-ops submodule:

```bash
# Navigate to memra-ops directory
cd memra-ops

# Start PostgreSQL using Docker Compose
docker compose up -d postgres

# Wait a moment for PostgreSQL to start
sleep 5

# Verify PostgreSQL is running
docker ps | grep memra-postgres

# Return to main directory
cd ..
```

### Step 5: Database Schema (Auto-Configured)

The database schema is automatically created when PostgreSQL starts via Docker Compose. The schema includes:

- **`invoices`** table with all necessary columns
- **`invoice_flat_view`** view for easy querying
- **Sample data** for testing

You can verify the schema was created:

```bash
# Check if the table exists
psql -h localhost -p 5432 -U postgres -d local_workflow -c "\dt"

# View the table structure
psql -h localhost -p 5432 -U postgres -d local_workflow -c "\d invoices"
```

### Step 6: Install Additional Dependencies

```bash
# Install required Python packages
pip install psycopg2-binary aiohttp aiohttp-cors httpx prettytable

# Install build tools (for development)
pip install build twine
```

### Step 7: Set Up Environment Variables

```bash
# Set the Memra API key (development key)
export MEMRA_API_KEY="test-secret-for-development"

# Set database connection
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/local_workflow"

# Add to your shell profile (optional, for persistence)
echo 'export MEMRA_API_KEY="test-secret-for-development"' >> ~/.bashrc
echo 'export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/local_workflow"' >> ~/.bashrc
```

### Step 8: Start the MCP Bridge Server

The MCP bridge server provides tools for the ETL workflow:

```bash
# Start the MCP bridge server (from memra-ops)
cd memra-ops
python3 mcp_bridge_server.py &

# Wait for the server to start
sleep 3

# Verify the server is running
curl -s http://localhost:8081/health

# Return to main directory
cd ..
```

You should see a response indicating the server is healthy.

### Step 9: Sample Invoice Data

The SDK repo includes sample PDF invoices for testing:

```bash
# Check the sample data directory
ls -la demos/etl_invoice_processing/data/invoices/

# You should see multiple PDF files ready for testing
```

**Note**: The SDK includes sample PDF invoices for immediate testing. You can also add your own PDF files to this directory.

### Step 10: Run the ETL Workflow

```bash
# Navigate to the ETL demo directory
cd demos/etl_invoice_processing

# Run the ETL workflow
python3 etl_invoice_demo.py
```

**What happens during execution:**
1. The script will scan for PDF files in the `data/invoices/` directory
2. For each PDF, it will:
   - Extract data using vision models
   - Validate the extracted data
   - Store the data in PostgreSQL
   - Show progress and results

**Interactive prompts:**
- When prompted, type `Y` to process each invoice
- Or type `B` to process all remaining invoices in batch mode

### Step 11: Verify the Results

```bash
# Check the database for processed invoices
psql -h localhost -p 5432 -U postgres -d local_workflow -c "
SELECT 
    id,
    invoice_number,
    vendor_name,
    invoice_date,
    total_amount,
    status,
    created_at
FROM invoices
ORDER BY created_at DESC
LIMIT 10;
"

# Check the raw JSON data
psql -h localhost -p 5432 -U postgres -d local_workflow -c "
SELECT 
    id,
    raw_json->'billingDetails'->>'invoiceNumber' as invoice_number,
    raw_json->'headerSection'->>'vendorName' as vendor_name
FROM invoices
ORDER BY created_at DESC
LIMIT 5;
"
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep memra-postgres

# If not running, restart it
docker start memra-postgres

# Check logs
docker logs memra-postgres
```

#### 2. MCP Bridge Server Issues
```bash
# Check if the server is running
curl -s http://localhost:8081/health

# If not running, restart it
python3 mcp_bridge_server.py &
```

#### 3. Python Import Errors
```bash
# Reinstall Memra
pip uninstall memra
pip install memra

# Check Python path
python3 -c "import sys; print(sys.path)"
```

#### 4. Permission Issues
```bash
# On Linux/macOS, you might need to use sudo for some commands
sudo docker run ...
sudo pip install ...
```

#### 5. Port Conflicts
If port 5432 or 8081 is already in use:
```bash
# Find what's using the port
lsof -i :5432
lsof -i :8081

# Kill the process or use different ports
```

## 📊 Understanding the Results

### What the ETL Workflow Does

1. **PDF Processing**: Uses vision models to extract text and data from PDF invoices
2. **Data Extraction**: Identifies invoice numbers, vendor names, amounts, dates, etc.
3. **Validation**: Checks if the extracted data is complete and valid
4. **Database Storage**: Stores both structured data and raw JSON in PostgreSQL
5. **Monitoring**: Provides real-time feedback on the processing status

### Database Tables

- **`invoices`**: Main table with all invoice data (includes structured columns and raw JSON)

### Sample Queries

```sql
-- View all processed invoices
SELECT * FROM invoices ORDER BY created_at DESC;

-- Find invoices by vendor
SELECT * FROM invoices WHERE vendor_name LIKE '%Propane%';

-- Check processing status
SELECT status, COUNT(*) FROM invoices GROUP BY status;

-- View raw JSON data
SELECT raw_json FROM invoices WHERE id = 1;
```

## 🧹 Cleanup

When you're done testing:

```bash
# Stop the MCP bridge server
pkill -f mcp_bridge_server.py

# Stop and remove containers
cd memra-ops
docker compose down

# Return to main directory
cd ..

# Uninstall Memra (optional)
pip uninstall memra
```

## 🎉 Congratulations!

You've successfully:
- ✅ Installed Memra SDK
- ✅ Set up a PostgreSQL database
- ✅ Started the MCP bridge server
- ✅ Processed PDF invoices with AI
- ✅ Stored data in a database

You now have a working AI-powered ETL workflow that can process invoices automatically!

## 🔗 Next Steps

- **Explore the code**: Look at `etl_invoice_demo.py` to understand how it works
- **Try different PDFs**: Test with various invoice formats
- **Modify the workflow**: Customize agents and tools for your needs
- **Scale up**: Process larger batches of documents
- **Integrate**: Connect to your existing systems

## 📞 Getting Help

- **GitHub Issues**: [Report problems here](https://github.com/memra-platform/memra-sdk/issues)
- **Discussions**: [Ask questions here](https://github.com/memra-platform/memra-sdk/discussions)
- **Email**: hello@memra.com

---

**Happy building with Memra! 🚀** 
