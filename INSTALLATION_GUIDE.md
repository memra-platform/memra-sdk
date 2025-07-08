# Memra Installation Guide

This guide provides detailed instructions for installing Memra and running the ETL workflow. For most users, the [Quick Start Guide](QUICK_START.md) with `pip install memra` and `memra demo` is all you need!

## 🎯 Quick Start (Recommended)

For most users, this is all you need:

```bash
# Install Memra
pip install memra

# Run the ETL demo
memra demo
```

**That's it!** The demo handles everything automatically.

## 📋 Detailed Installation (If Needed)

This section is for users who:
- Need to understand what's happening under the hood
- Want to run the demo manually
- Are developing or contributing to Memra
- Run into issues with the automated demo

### What You'll Accomplish

By the end of this guide, you'll have:
- ✅ Memra SDK installed and working
- ✅ PostgreSQL database running
- ✅ MCP bridge server running
- ✅ ETL workflow processing PDF invoices
- ✅ Data stored in PostgreSQL database

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

### Step 2: Install Memra SDK

```bash
# Install Memra from PyPI (recommended for most users)
pip install memra

# OR install in development mode (if you want to modify the code)
git clone https://github.com/memra-platform/memra-sdk.git
cd memra-sdk
pip install -e .
```

**Verify installation:**
```bash
# Check if Memra is installed
python3 -c "import memra; print('Memra installed successfully!')"

# Check if CLI works
memra --help
```

### Step 3: Set Up Environment Variables

```bash
# Set the Memra API key (development key)
export MEMRA_API_KEY="test-secret-for-development"

# Set database connection
export DATABASE_URL="postgresql://memra:memra123@localhost:5432/memra_invoice_db"

# Add to your shell profile (optional, for persistence)
echo 'export MEMRA_API_KEY="test-secret-for-development"' >> ~/.bashrc
echo 'export DATABASE_URL="postgresql://memra:memra123@localhost:5432/memra_invoice_db"' >> ~/.bashrc
```

### Step 4: Manual Database Setup (Alternative to memra demo)

If you want to set up the database manually instead of using `memra demo`:

```bash
# Create a directory for the demo
mkdir -p ~/.memra/demo
cd ~/.memra/demo

# Extract demo files from the package
python -c "
import memra.cli
memra.cli.extract_demo_files()
"

# Navigate to memra-ops directory
cd memra-ops

# Start PostgreSQL using Docker Compose
docker compose up -d postgres

# Wait a moment for PostgreSQL to start
sleep 5

# Verify PostgreSQL is running
docker ps | grep memra-postgres
```

### Step 5: Manual MCP Bridge Server Setup (Alternative to memra demo)

If you want to start the MCP bridge server manually:

```bash
# Navigate to the demo directory
cd ~/.memra/demo/memra-ops

# Start the MCP bridge server
python3 mcp_bridge_server.py &

# Wait for the server to start
sleep 3

# Verify the server is running
curl -s http://localhost:8081/health
```

### Step 6: Manual Demo Execution (Alternative to memra demo)

If you want to run the demo manually:

```bash
# Navigate to the demo directory
cd ~/.memra/demo

# Run the ETL demo
python3 etl_invoice_demo.py
```

## 🔧 Troubleshooting

### Common Issues

**Docker not running:**
```bash
# Start Docker Desktop
# On macOS/Linux, you might need to start the Docker service
sudo systemctl start docker  # Linux
```

**Port conflicts:**
```bash
# Check what's using port 5432 (PostgreSQL)
lsof -i :5432

# Check what's using port 8081 (MCP bridge)
lsof -i :8081
```

**Permission issues:**
```bash
# Make sure you have write permissions to ~/.memra
mkdir -p ~/.memra
chmod 755 ~/.memra
```

**API key issues:**
```bash
# Verify the API key is set
echo $MEMRA_API_KEY

# Set it again if needed
export MEMRA_API_KEY="test-secret-for-development"
```

### Database Connection Issues

**Can't connect to PostgreSQL:**
```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# Check container logs
docker logs memra-ops_postgres_1

# Restart the container
docker compose restart postgres
```

**Database doesn't exist:**
```bash
# Connect to PostgreSQL and create the database
docker exec -it memra-ops_postgres_1 psql -U memra -c "CREATE DATABASE memra_invoice_db;"
```

### MCP Bridge Server Issues

**Server not responding:**
```bash
# Check if the server is running
ps aux | grep mcp_bridge_server

# Check server logs
tail -f ~/.memra/demo/memra-ops/mcp_bridge_server.log

# Restart the server
pkill -f mcp_bridge_server
cd ~/.memra/demo/memra-ops
python3 mcp_bridge_server.py &
```

## 📊 Verification

### Check Database Contents

```bash
# Connect to the database
docker exec -it memra-ops_postgres_1 psql -U memra -d memra_invoice_db

# List tables
\dt

# Check invoice data
SELECT COUNT(*) FROM invoices;
SELECT vendor_name, total_amount FROM invoices LIMIT 5;

# Exit
\q
```

### Check MCP Bridge Server

```bash
# Test the health endpoint
curl http://localhost:8081/health

# Test tool execution
curl -X POST http://localhost:8081/execute_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "SQLExecutor", "parameters": {"query": "SELECT 1"}}'
```

## 🧹 Cleanup

### Stop Services

```bash
# Stop Docker containers
cd ~/.memra/demo/memra-ops
docker compose down

# Stop MCP bridge server
pkill -f mcp_bridge_server
```

### Remove Demo Files

```bash
# Remove demo directory
rm -rf ~/.memra/demo
```

## 📚 Next Steps

- **Explore the code:** Check out the extracted demo files in `~/.memra/demo/`
- **Build your own workflow:** See examples in the `examples/` directory
- **Learn more:** Read the [Text-to-SQL Guide](TEXT_TO_SQL_USAGE_GUIDE.md)
- **Contribute:** Check out our [Contributing Guide](CONTRIBUTING.md)

---

**Remember:** For most users, `pip install memra` and `memra demo` is all you need! 🚀
