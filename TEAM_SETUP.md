# Memra Team Setup Guide

Welcome to the Memra platform! This guide will help you and your team get up and running with a production-like environment in minutes.

---

## 🚀 Quick Start (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd memra
   ```
2. **Create and activate the conda environment:**
   ```bash
   conda create -n memra python=3.11
   conda activate memra
   pip install -r requirements.txt
   ```
3. **Set your Memra API key:**
   ```bash
   export MEMRA_API_KEY="your-api-key-here"
   ```
4. **Start all services (PostgreSQL, MCP bridge, etc.):**
   ```bash
   docker-compose up -d
   # Or use the enhanced script:
   python scripts/start_memra.py
   ```
5. **Run the ETL demo:**
   ```bash
   python demos/etl_invoice_processing/etl_invoice_demo.py
   ```

---

## 🐳 Docker Compose Workflow
- **All engineers get the same environment**: Database, bridge, and sample data are spun up with one command.
- **No database data in Git**: Only schema (`docs/database_schema.sql`) and sample data (`docs/sample_data.sql`) are versioned.
- **Reset anytime**: `docker-compose down -v` wipes all data for a clean slate.
- **No local conflicts**: Each developer has their own isolated database.

---

## 🛠️ Manual Database Access
- Connect to the running container:
  ```bash
  docker exec -it memra_postgres psql -U memra -d memra_invoice_db
  ```
- Or use any PostgreSQL client with:
  - Host: `localhost`
  - Port: `5432`
  - User: `memra`
  - Password: `memra123`
  - Database: `memra_invoice_db`

---

## 🧑‍💻 Development Workflow
- **Start everything:**
  ```bash
  python scripts/start_memra.py
  # or
  docker-compose up -d
  ```
- **Run workflows:**
  ```bash
  python demos/etl_invoice_processing/etl_invoice_demo.py
  python examples/accounts_payable_client.py
  ```
- **Stop everything:**
  ```bash
  python scripts/stop_memra.py
  # or
  docker-compose down
  ```

---

## 🐍 Memra SDK via pip
- The core Memra SDK is published to PyPI for easy use in other projects:
  ```bash
  pip install memra-sdk
  ```
- For local development, use the version in this repo.

---

## 📝 Troubleshooting
- **Docker not running?** Start Docker Desktop.
- **Database issues?**
  ```bash
  docker-compose down -v
  docker-compose up -d
  docker logs memra_postgres
  ```
- **Bridge issues?**
  ```bash
  docker-compose restart mcp_bridge
  docker logs memra_mcp_bridge
  ```
- **API issues?**
  ```bash
  echo $MEMRA_API_KEY
  curl https://api.memra.co/health
  ```

---

## 📁 File Structure
```
memra/
├── demos/                    # Comprehensive demos
│   └── etl_invoice_processing/
├── examples/                 # Basic examples
├── docs/                     # Documentation
│   ├── database_schema.sql   # Database schema
│   └── sample_data.sql       # Sample data
├── scripts/                  # Utility scripts
│   ├── start_memra.py        # Startup script
│   └── stop_memra.py         # Shutdown script
├── docker-compose.yml        # Docker services
├── requirements.txt          # Python dependencies
└── TEAM_SETUP.md             # This file
```

---

## 🤝 Collaboration
- **Schema and sample data are versioned**—never commit actual database files.
- **Update sample data** when adding new features.
- **Test with a fresh database** before pushing changes.
- **For schema changes:**
  - Update `docs/database_schema.sql` and `docs/sample_data.sql`.
  - Test with `docker-compose up -d`.

---

## 🆘 Support
- **Docs:** See `docs/` directory
- **Issues:** Create a GitHub issue
- **API:** info@memra.co
- **Team chat:** Use your team's platform

Happy coding! 🚀 