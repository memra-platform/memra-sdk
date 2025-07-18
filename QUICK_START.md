# 🚀 Quick Start Guide

Get up and running with Memra in **5 minutes**!

> **💡 New to Memra?** If you need more detailed setup instructions or run into issues, check out our [Detailed Installation Guide](INSTALLATION_GUIDE.md) or use our automated setup script: `bash scripts/setup_newbie.sh`
>
> **🔧 Submodules:** This repo uses git submodules for infrastructure and workflow templates. The sparse checkout gives you minimal access to essential files only.

## 1. Install Memra SDK
```bash
# Upgrade pip first (recommended, especially for Windows)
python -m pip install --upgrade pip

# Install Memra SDK
pip install memra
```

## 2. Run the ETL Demo
```bash
# That's it! Just run the demo command
memra demo
```

**What happens automatically:**
- ✅ Extracts bundled demo files
- ✅ Sets environment variables (API key, database URL)
- ✅ Starts Docker containers (PostgreSQL, MCP bridge)
- ✅ Runs the ETL workflow
- ✅ Shows results and next steps

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

- **Explore examples:** Check out the extracted demo files in `~/.memra/demo/`
- **Check database:** `docker exec -it memra_postgres psql -U postgres -d local_workflow`
- **Stop services:** `cd ~/.memra/demo/memra-ops && docker compose down`

## 🆘 Need Help?

- **Docker not running?** Start Docker Desktop
- **API key issues?** Use `test-secret-for-development` for local demos
- **Setup problems?** See our [Detailed Installation Guide](INSTALLATION_GUIDE.md)
- **More details:** See `TEAM_SETUP.md` and `demos/README.md`

---

**Ready to build your own workflows?** Check out the examples in the `examples/` directory! 🚀 