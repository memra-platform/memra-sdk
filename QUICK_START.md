# 🚀 Quick Start Guide

Get up and running with Memra in **5 minutes**!

## 1. Install Memra SDK
```bash
pip install memra
```

## 2. Clone the Repository
```bash
git clone https://github.com/memra-platform/memra-sdk.git
cd memra-sdk
```

## 3. Set Your API Key
```bash
export MEMRA_API_KEY="your-api-key-here"
```

## 4. Start the Demo Environment
```bash
# Start PostgreSQL and MCP bridge
docker-compose up -d

# Or use the startup script
python scripts/start_memra.py
```

## 5. Run the ETL Demo
```bash
python demos/etl_invoice_processing/etl_invoice_demo.py
```

## 🎯 That's It!

You should see output like:
```
🚀 Starting ETL Invoice Processing Demo...
🏢 Starting ETL Invoice Processing Department
📋 Mission: Complete end-to-end ETL process with comprehensive monitoring
👥 Team: Pre-ETL Database Monitor, Data Engineer, Invoice Parser, Data Entry Specialist, Post-ETL Database Monitor
👔 Manager: ETL Process Manager

🔄 Step 1/5: Pre-ETL Database Monitor
✅ Database state captured: 2 rows

🔄 Step 2/5: Data Engineer
✅ Schema extracted successfully

🔄 Step 3/5: Invoice Parser
✅ Invoice data extracted: $1,234.56

🔄 Step 4/5: Data Entry Specialist
✅ Record inserted: ID 4

🔄 Step 5/5: Post-ETL Database Monitor
✅ Database state captured: 3 rows

🎉 ETL Invoice Processing Department workflow completed!
⏱️ Total time: 12.3s
```

## 🔧 What Just Happened?

1. **Pre-ETL Monitor** - Checked database state (2 rows)
2. **Data Engineer** - Extracted database schema
3. **Invoice Parser** - Processed a PDF invoice with AI vision
4. **Data Entry Specialist** - Validated and inserted the data
5. **Post-ETL Monitor** - Verified the new record was added (3 rows)

## 🛠️ Next Steps

- **Explore examples:** `python examples/accounts_payable_client.py`
- **Check database:** `docker exec -it memra_postgres psql -U memra -d memra_invoice_db`
- **Stop services:** `docker-compose down`

## 🆘 Need Help?

- **Docker not running?** Start Docker Desktop
- **API key issues?** Get your key from [memra.co](https://memra.co)
- **More details:** See `TEAM_SETUP.md` and `demos/README.md`

---

**Ready to build your own workflows?** Check out the examples in the `examples/` directory! 🚀 