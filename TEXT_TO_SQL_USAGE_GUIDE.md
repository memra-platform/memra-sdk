# Text-to-SQL System Usage Guide

## 🎯 **System Overview**

The Text-to-SQL system provides **dual functionality**:

1. **Standalone Query Agent** - Independent business intelligence tool
2. **Integrated Workflow Component** - Automatic querying after invoice processing

## 🚀 **How to Use the System**

### **Option 1: Standalone Text-to-SQL Queries**

For ad-hoc business intelligence queries on your existing invoice database:

```bash
# Interactive system with full UI
source /Users/tarpus/miniconda3/bin/activate memra
python3 examples/complete_text_to_sql_system.py

# Automated demo (no interaction required)
python3 examples/test_text_to_sql_demo.py
```

**Features:**
- Ask natural language questions about invoice data
- Real-time SQL generation and execution
- Interactive query interface
- Works with existing database records

### **Option 2: Complete Invoice Processing + Queries**

For end-to-end workflow from PDF to database to queries:

```bash
source /Users/tarpus/miniconda3/bin/activate memra
python3 examples/complete_invoice_workflow_with_queries.py
```

**Workflow:**
1. **File Discovery** - Automatically finds PDFs in `invoices/` directory
2. **Invoice Processing** - Extracts data and inserts into database
3. **Business Intelligence** - Offers natural language querying of results

## 🧠 **Natural Language Query Examples**

The system understands questions like:

- "Show me all invoices from Air Liquide"
- "What is the total amount of all invoices?"
- "How many invoices do we have in the database?"
- "Show me the most recent 5 invoices"
- "What is the average invoice amount?"

## ⚙️ **Technical Architecture**

### **Components:**
- **TextToSQLGenerator** - Converts English to SQL using pattern matching
- **SQLExecutor** - Executes SQL queries against PostgreSQL database
- **MCP Bridge Server** - Handles tool execution and database connections

### **Data Flow:**
```
English Question → SQL Generation → SQL Execution → Real Results
```

### **Real vs Mock Results:**
- ✅ **Real Results**: When MCP bridge server is running on port 8081
- ⚠️ **Mock Results**: When MCP bridge is unavailable (fallback mode)

## 🔧 **Setup Requirements**

### **Prerequisites:**
1. **MCP Bridge Server** running on `localhost:8081`
2. **PostgreSQL Database** with invoice data
3. **Python Environment** with required dependencies

### **Start MCP Bridge Server:**
```bash
source /Users/tarpus/miniconda3/bin/activate memra
export MCP_POSTGRES_URL="postgresql://tarpus@localhost:5432/memra_invoice_db"
export MCP_BRIDGE_SECRET="test-secret-for-development"
python3 mcp_bridge_server.py
```

### **Verify System Health:**
```bash
curl -s http://localhost:8081/health
# Should return: {"status": "healthy", "service": "mcp-bridge"}
```

## 📊 **Current Database State**

As of the last test, your database contains:
- **16 total invoices**
- **9 Air Liquide invoices** with complete line item details
- **Real invoice data** including amounts, dates, and vendor information

## 🎯 **Use Cases**

### **For Business Users:**
- Quick insights into invoice data
- Ad-hoc financial reporting
- Vendor analysis and spending patterns

### **For Developers:**
- Integration into existing workflows
- Automated data validation after processing
- Business intelligence layer for applications

### **For Data Teams:**
- Natural language interface to SQL database
- Rapid prototyping of queries
- Self-service analytics capabilities

## 🔄 **Integration Patterns**

### **Pattern 1: Post-Processing Queries**
```python
# After invoice processing
record_id = process_invoice(file_path)
run_text_to_sql_queries(registry, record_id)
```

### **Pattern 2: Standalone BI Tool**
```python
# Independent query session
registry = ToolRegistry()
run_text_to_sql_queries(registry)
```

### **Pattern 3: Automated Validation**
```python
# Automatic validation queries after data insertion
validate_recent_data_with_queries()
```

## 🚀 **Next Steps**

### **Immediate Usage:**
1. Run the complete workflow to see end-to-end functionality
2. Try different natural language questions
3. Explore the interactive query interface

### **Future Enhancements:**
1. **LLM Integration** - Replace pattern matching with actual LLM for better SQL generation
2. **Advanced Queries** - Support for complex joins, aggregations, and analytics
3. **Query History** - Save and replay previous queries
4. **Export Capabilities** - Export results to CSV, Excel, or reports

## 💡 **Tips for Best Results**

1. **Be Specific** - "Show me Air Liquide invoices" works better than "show invoices"
2. **Use Keywords** - Include words like "total", "count", "recent", "from [vendor]"
3. **Check Results** - Look for "Real database results!" vs "mocked" indicators
4. **Iterate** - Try different phrasings if the first query doesn't work as expected

The system is now ready for production use and can be extended based on your specific business needs! 