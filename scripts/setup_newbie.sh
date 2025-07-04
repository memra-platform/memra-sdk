#!/bin/bash

# Memra Newbie Setup Script
# This script automates the installation process for new users

set -e  # Exit on any error

echo "🚀 Welcome to Memra! Let's get you set up..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -d "memra" ]; then
    print_error "Please run this script from the memra-sdk root directory"
    exit 1
fi

print_status "Checking prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_success "Python $PYTHON_VERSION found"

# Check Git
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git."
    exit 1
fi

print_success "Git found"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop."
    exit 1
fi

if ! docker ps &> /dev/null; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

print_success "Docker is running"

print_status "Installing Memra SDK..."

# Install Memra
if pip install memra; then
    print_success "Memra SDK installed successfully"
else
    print_error "Failed to install Memra SDK"
    exit 1
fi

# Install additional dependencies
print_status "Installing additional dependencies..."
pip install psycopg2-binary aiohttp aiohttp-cors httpx prettytable

print_status "Setting up PostgreSQL database..."

# Create Docker network if it doesn't exist
if ! docker network ls | grep -q memra-network; then
    docker network create memra-network
    print_success "Created Docker network: memra-network"
fi

# Check if PostgreSQL container already exists
if docker ps -a | grep -q memra-postgres; then
    print_warning "PostgreSQL container already exists"
    read -p "Do you want to remove the existing container and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker stop memra-postgres 2>/dev/null || true
        docker rm memra-postgres 2>/dev/null || true
        print_success "Removed existing PostgreSQL container"
    else
        print_status "Using existing PostgreSQL container"
        docker start memra-postgres 2>/dev/null || true
    fi
else
    # Start PostgreSQL container
    docker run -d \
        --name memra-postgres \
        --network memra-network \
        -e POSTGRES_DB=memra_invoice_db \
        -e POSTGRES_USER=memra \
        -e POSTGRES_PASSWORD=memra123 \
        -p 5433:5432 \
        postgres:15
    
    print_success "PostgreSQL container started"
fi

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 10

# Test PostgreSQL connection
if ! docker exec memra-postgres pg_isready -U memra -d memra_invoice_db; then
    print_error "PostgreSQL is not ready. Please check Docker logs."
    docker logs memra-postgres
    exit 1
fi

print_success "PostgreSQL is ready"

print_status "Setting up database schema..."

# Create the database schema
docker exec memra-postgres psql -U memra -d memra_invoice_db -c "
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR NOT NULL,
    vendor_name VARCHAR NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    total_amount NUMERIC NOT NULL,
    tax_amount NUMERIC,
    line_items JSONB,
    status VARCHAR NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_json JSONB
);

CREATE OR REPLACE VIEW invoice_flat_view AS
SELECT
    id,
    raw_json->'billingDetails'->>'invoiceNumber' AS invoice_number,
    raw_json->'headerSection'->>'vendorName' AS vendor_name,
    CASE 
        WHEN raw_json->'billingDetails'->>'invoiceDate' = '' THEN NULL
        ELSE (raw_json->'billingDetails'->>'invoiceDate')::date 
    END AS invoice_date,
    CASE 
        WHEN raw_json->'billingDetails'->>'dueDate' = '' THEN NULL
        ELSE (raw_json->'billingDetails'->>'dueDate')::date 
    END AS due_date,
    (raw_json->'chargesSummary'->>'document_total')::numeric AS total_amount,
    (raw_json->'chargesSummary'->>'secondary_tax')::numeric AS tax_amount,
    raw_json->'chargesSummary'->'lineItemsBreakdown' AS line_items,
    raw_json->>'status' AS status,
    created_at,
    updated_at
FROM invoices;
" > /dev/null 2>&1

print_success "Database schema created"

print_status "Setting up environment variables..."

# Set environment variables
export MEMRA_API_KEY="test-secret-for-development"
export DATABASE_URL="postgresql://memra:memra123@localhost:5433/memra_invoice_db"

# Add to shell profile
SHELL_PROFILE=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
fi

if [ -n "$SHELL_PROFILE" ]; then
    # Check if variables are already set
    if ! grep -q "MEMRA_API_KEY" "$SHELL_PROFILE"; then
        echo 'export MEMRA_API_KEY="test-secret-for-development"' >> "$SHELL_PROFILE"
        echo 'export DATABASE_URL="postgresql://memra:memra123@localhost:5433/memra_invoice_db"' >> "$SHELL_PROFILE"
        print_success "Environment variables added to $SHELL_PROFILE"
    else
        print_warning "Environment variables already set in $SHELL_PROFILE"
    fi
fi

print_status "Creating data directories..."

# Create data directories
mkdir -p demos/etl_invoice_processing/data/invoices

print_success "Data directories created"

print_status "Starting MCP bridge server..."

# Start MCP bridge server in background
cd memra-ops
python3 mcp_bridge_server.py > ../mcp_server.log 2>&1 &
MCP_PID=$!

# Wait for server to start
sleep 5

# Test if server is running
if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    print_success "MCP bridge server started successfully"
else
    print_error "Failed to start MCP bridge server"
    print_error "Check the logs: cat mcp_server.log"
    exit 1
fi

cd ..

print_status "Setup complete! 🎉"
echo ""
print_success "What's been set up:"
echo "  ✅ Memra SDK installed"
echo "  ✅ PostgreSQL database running on port 5433"
echo "  ✅ MCP bridge server running on port 8081"
echo "  ✅ Environment variables configured"
echo "  ✅ Database schema created"
echo "  ✅ Data directories created"
echo ""
print_status "Next steps:"
echo "  1. Add PDF invoice files to: demos/etl_invoice_processing/data/invoices/"
echo "  2. Run the ETL workflow: cd demos/etl_invoice_processing && python3 etl_invoice_demo.py"
echo "  3. Check the results in the database"
echo ""
print_warning "Note: You'll need to provide your own PDF invoice files for testing"
echo ""
print_status "For detailed instructions, see: INSTALLATION_GUIDE.md"
echo ""
print_status "To stop services later:"
echo "  - MCP server: pkill -f mcp_bridge_server.py"
echo "  - PostgreSQL: docker stop memra-postgres"
echo ""

# Save MCP server PID for later cleanup
echo $MCP_PID > .mcp_server.pid
print_status "MCP server PID saved to .mcp_server.pid" 