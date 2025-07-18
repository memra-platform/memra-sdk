# Server Setup Guide

This guide explains how to set up the MCP Bridge Server with proper security practices.

## Security Notice

The files with hardcoded API keys have been removed from the public repository for security reasons. These files should only exist on your production servers with proper environment variable configuration.

## Files Excluded from Public Repository

The following files contain sensitive information and are excluded from the public repository:

- `memra-ops/mcp_bridge_server.py` - MCP Bridge Server with API keys
- `memra-ops/config.py` - Configuration with hardcoded secrets
- `memra-ops/etl_tools.py` - ETL tools with API keys
- `memra-etl-service/app.py` - ETL service with API keys

## Server Setup Instructions

### 1. Environment Variables

Set up the following environment variables on your server:

```bash
# Required API Keys
export HUGGINGFACE_API_KEY="your_huggingface_api_key_here"
export FIREWORKS_API_KEY="your_fireworks_api_key_here"

# Database Configuration
export POSTGRES_URL="postgresql://username:password@host:port/database"

# Server Configuration
export PORT="8082"
export BRIDGE_SECRET="your_bridge_secret_here"

# Optional Configuration
export HUGGINGFACE_MODEL="meta-llama/Llama-3.1-8B-Instruct"
```

### 2. File Setup

Copy the template files to create the actual server files:

```bash
# Copy templates to actual files
cp memra-ops/mcp_bridge_server.py.template memra-ops/mcp_bridge_server.py
cp memra-ops/config.py.template memra-ops/config.py
```

### 3. Fly.io Deployment

For Fly.io deployment, create a `fly.toml` file:

```toml
app = "memra-mcp-bridge"
primary_region = "sjc"

[build]

[env]
  PORT = "8080"
  POSTGRES_URL = "postgresql://memra:memra123@localhost:5432/memra_invoice_db"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

Set secrets on Fly.io:

```bash
fly secrets set HUGGINGFACE_API_KEY="your_key_here"
fly secrets set FIREWORKS_API_KEY="your_key_here"
fly secrets set BRIDGE_SECRET="your_secret_here"
```

### 4. Docker Deployment

For Docker deployment, create a `.env` file (never commit this):

```env
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
FIREWORKS_API_KEY=your_fireworks_api_key_here
POSTGRES_URL=postgresql://username:password@host:port/database
PORT=8082
BRIDGE_SECRET=your_bridge_secret_here
```

### 5. Local Development

For local development, create a `.env` file in the project root:

```env
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
FIREWORKS_API_KEY=your_fireworks_api_key_here
POSTGRES_URL=postgresql://memra:memra123@localhost:5432/memra_invoice_db
PORT=8082
BRIDGE_SECRET=your_local_secret_here
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive configuration
3. **Rotate API keys** regularly
4. **Use secrets management** in production (Fly.io secrets, Docker secrets, etc.)
5. **Monitor API usage** to detect unauthorized access
6. **Use HTTPS** in production
7. **Implement proper authentication** for the bridge server

## Troubleshooting

### Missing API Keys
If you see warnings about missing API keys, ensure the environment variables are set correctly:

```bash
echo $HUGGINGFACE_API_KEY
echo $FIREWORKS_API_KEY
```

### Database Connection Issues
Check your PostgreSQL connection string and ensure the database is accessible:

```bash
psql $POSTGRES_URL -c "SELECT 1;"
```

### Port Conflicts
If you get "address already in use" errors, change the PORT environment variable or stop conflicting services.

## Support

For issues with server setup, check:
1. Environment variables are set correctly
2. Database is accessible
3. API keys are valid
4. Network connectivity to external services 