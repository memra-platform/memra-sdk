"""
Database Monitor Agent
Monitors database state before and after ETL processes
"""

from memra import Agent, LLM

def create_database_monitor_agent():
    """Create a database monitoring agent"""
    
    monitor_llm = LLM(
        model="llama-3.2-11b-vision-preview",
        temperature=0.1,
        max_tokens=1000
    )
    
    monitor_agent = Agent(
        role="Database Monitor",
        job="Monitor database state and validate data integrity",
        llm=monitor_llm,
        sops=[
            "Connect to database using provided credentials",
            "Execute monitoring queries to count rows and validate data",
            "Generate comprehensive monitoring report with statistics",
            "Flag any data integrity issues or anomalies",
            "Return structured monitoring results"
        ],
        systems=["Database"],
        tools=[
            {"name": "SQLExecutor", "hosted_by": "mcp"}
        ],
        input_keys=["table_name", "connection", "monitoring_phase"],
        output_key="monitoring_report"
    )
    
    return monitor_agent

def get_monitoring_queries(table_name: str, phase: str):
    """Get appropriate SQL queries for monitoring phase"""
    
    queries = {
        "before": [
            f"SELECT COUNT(*) as row_count FROM {table_name}",
            f"SELECT COUNT(*) as null_vendor_count FROM {table_name} WHERE vendor_name IS NULL",
            f"SELECT COUNT(*) as null_invoice_count FROM {table_name} WHERE invoice_number IS NULL",
            f"SELECT COUNT(*) as null_amount_count FROM {table_name} WHERE total_amount IS NULL"
        ],
        "after": [
            f"SELECT COUNT(*) as row_count FROM {table_name}",
            f"SELECT COUNT(*) as null_vendor_count FROM {table_name} WHERE vendor_name IS NULL",
            f"SELECT COUNT(*) as null_invoice_count FROM {table_name} WHERE invoice_number IS NULL", 
            f"SELECT COUNT(*) as null_amount_count FROM {table_name} WHERE total_amount IS NULL",
            f"SELECT COUNT(*) as duplicate_invoices FROM (SELECT invoice_number, COUNT(*) as cnt FROM {table_name} GROUP BY invoice_number HAVING COUNT(*) > 1) as dups",
            f"SELECT MIN(total_amount) as min_amount, MAX(total_amount) as max_amount, AVG(total_amount) as avg_amount FROM {table_name}",
            f"SELECT COUNT(*) as recent_records FROM {table_name} WHERE created_at >= NOW() - INTERVAL '1 hour'"
        ]
    }
    
    return queries.get(phase, queries["after"])

def create_simple_monitor_agent():
    """Create a simple database monitoring agent that works with the framework"""
    
    monitor_llm = LLM(
        model="llama-3.2-11b-vision-preview",
        temperature=0.1,
        max_tokens=1500
    )
    
    monitor_agent = Agent(
        role="Database Monitor",
        job="Monitor database state and validate data integrity",
        llm=monitor_llm,
        sops=[
            "Connect to database using provided credentials",
            "Execute monitoring query using sql_query input",
            "Generate monitoring report with current statistics",
            "Flag any data integrity issues",
            "Return structured monitoring results"
        ],
        systems=["Database"],
        tools=[
            {"name": "SQLExecutor", "hosted_by": "mcp", "input_keys": ["sql_query"]}
        ],
        input_keys=["table_name", "connection", "monitoring_phase", "sql_query"],
        output_key="monitoring_report"
    )
    
    return monitor_agent 