# Memra Demos

This directory contains comprehensive demonstrations of Memra's capabilities.

## 🚀 ETL Invoice Processing Demo

A complete end-to-end ETL (Extract, Transform, Load) workflow that demonstrates:

- **Database Monitoring** - Pre and post-ETL state tracking
- **Schema Extraction** - Dynamic database schema discovery
- **Document Processing** - PDF invoice parsing with vision models
- **Data Validation** - Multi-stage validation and quality checks
- **Database Operations** - Secure data insertion with monitoring

### 📊 Demo Features

#### **Pre-ETL Monitoring**
- Database row count before processing
- Data quality assessment
- Null value analysis
- Schema validation

#### **ETL Pipeline**
1. **Data Engineer** - Extracts database schema
2. **Invoice Parser** - Processes PDF with vision model
3. **Data Entry Specialist** - Validates and inserts data

#### **Post-ETL Monitoring**
- Row count comparison
- Data quality metrics
- Duplicate detection
- Statistical analysis (min, max, avg amounts)
- Recent record tracking

### 🛠️ Running the Demo

#### **Prerequisites**
1. **Start Memra System:**
   ```bash
   cd /path/to/memra-ops
   ./scripts/start_memra.sh
   ```

2. **Set API Key:**
   ```bash
   export MEMRA_API_KEY='your-key-here'
   ```

3. **Ensure PostgreSQL is running:**
   ```bash
   docker ps | grep memra-postgres
   ```

#### **Run the Demo**
```bash
cd /path/to/memra/demos/etl_invoice_processing
python etl_invoice_demo.py
```

### 📈 Expected Output

```
🚀 Starting ETL Invoice Processing Demo...
📊 This demo includes comprehensive database monitoring

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

📋 ETL Summary Report:
Status: success
Summary: ETL process completed with 1 new record added

📊 Database State Comparison:
Pre-ETL Rows: 2
Post-ETL Rows: 3
New Records: 1
Data Quality: excellent
```

### 🔧 Customization

#### **Add More Monitoring Queries**
Edit `database_monitor_agent.py` to add custom SQL queries:

```python
def get_monitoring_queries(table_name: str, phase: str):
    queries = {
        "before": [
            f"SELECT COUNT(*) as row_count FROM {table_name}",
            # Add your custom queries here
        ],
        "after": [
            f"SELECT COUNT(*) as row_count FROM {table_name}",
            # Add your custom queries here
        ]
    }
    return queries.get(phase, queries["after"])
```

#### **Modify ETL Pipeline**
Edit `etl_invoice_demo.py` to:
- Add more agents
- Change workflow order
- Modify validation rules
- Add custom business logic

### 📊 Monitoring Metrics

The demo tracks these key metrics:

| Metric | Description |
|--------|-------------|
| Row Count | Total records in table |
| Null Values | Missing data analysis |
| Duplicates | Duplicate invoice detection |
| Amount Stats | Min, max, average amounts |
| Recent Records | Records added in last hour |
| Data Quality | Overall quality score |

### 🚨 Error Handling

The demo includes comprehensive error handling:
- Database connection failures
- PDF processing errors
- Data validation failures
- Network timeouts
- API rate limiting

### 🔄 Extending the Demo

#### **Add More Data Sources**
- Excel files
- CSV imports
- API integrations
- Real-time streams

#### **Add More Validation**
- Business rule validation
- Cross-reference checks
- Data type validation
- Format validation

#### **Add Reporting**
- Automated reports
- Email notifications
- Dashboard updates
- Audit trails

## 🎯 Next Steps

1. **Run the demo** to see it in action
2. **Customize** for your specific use case
3. **Extend** with additional agents and tools
4. **Deploy** to production with proper monitoring

## 📚 Related Documentation

- [Memra SDK Documentation](https://docs.memra.co)
- [Workflow Examples](../examples/)
- [Operations Guide](../memra-ops/) 