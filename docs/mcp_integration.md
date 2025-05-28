# MCP Integration Guide

## Overview

The Memra SDK now supports Model Context Protocol (MCP) integration, allowing you to execute operations on your local infrastructure while leveraging Memra's powerful cloud-based AI processing capabilities.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Memra Cloud   │    │   MCP Bridge    │    │ Local Resources │
│   (Fly.io)      │◄──►│   (Your Server) │◄──►│ (PostgreSQL,    │
│                 │    │                 │    │  APIs, Files)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

- **Memra Cloud**: Hosts AI processing tools (PDF, OCR, LLM workflows)
- **MCP Bridge**: Your local server that bridges requests to local resources
- **Local Resources**: Your databases, APIs, file systems, etc.

## Quick Start

### 1. Set Up MCP Bridge Server

Create a local MCP bridge server to handle database operations:

```python
# mcp_bridge_server.py
import os
from mcp_bridge_server import MCPBridgeServer, PostgresBridge

# Configure your database
postgres_url = os.getenv('MCP_POSTGRES_URL', 'postgresql://user:pass@localhost:5432/mydb')
bridge_secret = os.getenv('MCP_BRIDGE_SECRET', 'your-secret-key')

# Start the bridge
postgres_bridge = PostgresBridge(postgres_url)
server = MCPBridgeServer(postgres_bridge, bridge_secret)
app = server.create_app()

# Run on port 8081
if __name__ == '__main__':
    import asyncio
    asyncio.run(server.start(port=8081))
```

### 2. Configure Agents with MCP Tools

```python
from memra import Agent, Department, ExecutionEngine

# Agent that uses MCP tools for database operations
data_agent = Agent(
    role="Data Entry Specialist",
    job="Write validated data to local database",
    tools=[
        {
            "name": "DataValidator", 
            "hosted_by": "mcp",
            "config": {
                "bridge_url": "http://localhost:8081",
                "bridge_secret": "your-secret-key"
            }
        },
        {
            "name": "PostgresInsert", 
            "hosted_by": "mcp",
            "config": {
                "bridge_url": "http://localhost:8081", 
                "bridge_secret": "your-secret-key"
            }
        }
    ],
    input_keys=["data"],
    output_key="write_result"
)
```

### 3. Execute Hybrid Workflows

```python
# Set up API key for cloud processing
os.environ['MEMRA_API_KEY'] = 'your-api-key'

# Create department with mixed cloud/local tools
department = Department(
    name="Hybrid Processing",
    agents=[cloud_processor, data_agent],
    workflow_order=["Cloud Processor", "Data Entry Specialist"]
)

# Execute
engine = ExecutionEngine()
result = engine.execute_department(department, {"file": "document.pdf"})
```

## Available MCP Tools

### PostgresInsert
Inserts data into PostgreSQL tables.

**Parameters:**
- `data`: Dictionary of field values to insert
- `table_name`: Target table (optional, defaults to 'invoices')

**Example:**
```python
{
    "name": "PostgresInsert",
    "hosted_by": "mcp", 
    "config": {
        "bridge_url": "http://localhost:8081",
        "bridge_secret": "your-secret"
    }
}
```

### DataValidator
Validates data against schema before database operations.

**Parameters:**
- `data`: Data to validate
- `schema`: Validation schema (optional)

## Security

### HMAC Authentication
All requests between Memra Cloud and your MCP bridge are authenticated using HMAC-SHA256:

```python
# Bridge verifies requests from Memra
signature = hmac.new(
    bridge_secret.encode(),
    request_body.encode(), 
    hashlib.sha256
).hexdigest()
```

### Environment Variables
```bash
export MCP_POSTGRES_URL="postgresql://user:pass@localhost:5432/db"
export MCP_BRIDGE_SECRET="your-secure-secret-key"
export MEMRA_API_KEY="your-memra-api-key"
```

## Production Deployment

### 1. Secure Your Bridge
- Use strong secrets for HMAC authentication
- Run bridge behind firewall/VPN
- Use SSL/TLS for all connections

### 2. Expose Bridge to Memra Cloud
Use a secure tunnel service like ngrok:

```bash
# Install ngrok and set auth token
ngrok config add-authtoken YOUR_NGROK_TOKEN

# Tunnel your local bridge
ngrok http 8081
```

Update your agent configs with the ngrok URL:
```python
"config": {
    "bridge_url": "https://abc123.ngrok-free.app",
    "bridge_secret": "your-secret"
}
```

### 3. Database Setup
Ensure your database schema matches expected fields:

```sql
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    invoice_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2),
    line_items JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Troubleshooting

### Common Issues

**Tool routing errors:**
- Ensure `hosted_by: "mcp"` is set correctly
- Verify bridge URL is accessible from Memra Cloud
- Check HMAC secret matches between agent config and bridge

**Database connection errors:**
- Verify PostgreSQL is running and accessible
- Check connection string format
- Ensure database user has required permissions

**Authentication failures:**
- Verify bridge secret matches in both places
- Check request signatures are being generated correctly

### Debug Mode
Enable debug logging in your bridge:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

See the `examples/` directory for complete working examples:
- `accounts_payable_mcp.py` - Full invoice processing with MCP database writes
- `test_mcp_success.py` - Simple MCP integration test

## Support

For questions about MCP integration:
- Check the troubleshooting section above
- Review example code in the repository
- Contact support at info@memra.co 