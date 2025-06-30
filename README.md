# Memra SDK

The core Memra framework for building AI-powered business workflows.

## Installation

```bash
pip install memra
```

## 🚀 Quick Start (5 minutes!)

**Want to see Memra in action immediately?** Check out our [Quick Start Guide](QUICK_START.md) to run the ETL demo in minutes!

## Quick Start

```python
from memra import Agent, Department, LLM, ExecutionEngine

# Define an agent
agent = Agent(
    role="Data Analyst",
    job="Analyze customer data",
    llm=LLM(model="llama-3.2-11b-vision-preview"),
    sops=["Load data", "Perform analysis", "Generate report"],
    output_key="analysis_result"
)

# Create a department
department = Department(
    name="Analytics",
    mission="Provide data insights",
    agents=[agent],
    workflow_order=["Data Analyst"]
)

# Execute the workflow
engine = ExecutionEngine()
result = engine.execute_department(department, {"data": "customer_data.csv"})
```

## Core Components

### Agent
An AI worker that performs specific tasks using LLMs and tools.

### Department
A team of agents working together to accomplish a mission.

### ExecutionEngine
Orchestrates the execution of departments and their workflows.

### LLM
Configuration for language models used by agents.

## Examples

See the `examples/` directory for basic usage examples:
- `simple_text_to_sql.py` - Basic text-to-SQL conversion
- `ask_questions.py` - Simple question answering

## Documentation

For detailed documentation, visit [docs.memra.co](https://docs.memra.co)

Documentation is also available locally in the `examples/` directory.

## Example: Propane Delivery Workflow

See the `examples/propane_delivery.py` file for a complete example of how to use Memra to orchestrate a propane delivery workflow.

## 🔍 Smart File Discovery

Memra includes intelligent file discovery and management capabilities:

### File Discovery Tools
- **FileDiscovery**: Automatically scan directories for files matching patterns
- **FileCopy**: Copy files from external locations to standard processing directories
- **Smart Routing**: Automatically handle file paths and directory management

### Example: Smart Invoice Processing
```python
from memra import Agent

# Smart agent that discovers and processes files automatically
smart_parser = Agent(
    role="Smart Invoice Parser",
    job="Discover and process invoice files intelligently",
    tools=[
        {"name": "FileDiscovery", "hosted_by": "memra"},
        {"name": "FileCopy", "hosted_by": "memra"},
        {"name": "InvoiceExtractionWorkflow", "hosted_by": "memra"}
    ]
)

# Three modes of operation:
# 1. Auto-discovery: Scan invoices/ directory
# 2. External file: Copy from Downloads to invoices/
# 3. Specific file: Process exact file path
```

See `examples/accounts_payable_smart.py` for a complete implementation.

## Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details.

## License

MIT License - see LICENSE file for details. 