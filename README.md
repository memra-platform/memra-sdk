# Memra SDK

**The declarative framework for building enterprise-grade AI workflows with MCP integration.**

[![PyPI version](https://badge.fury.io/py/memra.svg)](https://badge.fury.io/py/memra)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Why Memra?

Building AI-powered business workflows is hard. You need to:
- **Orchestrate multiple AI agents** with different roles and responsibilities
- **Integrate with external tools** (databases, APIs, file systems)
- **Handle complex business logic** with validation and error recovery
- **Scale from prototypes to production** without rewriting everything
- **Maintain consistency** across different workflows and teams

**Memra solves these challenges** by providing a declarative framework that lets you focus on *what* you want to accomplish, not *how* to wire everything together.

## 🚀 Quick Start (5 minutes!)

**Want to see Memra in action immediately?** Check out our [Quick Start Guide](QUICK_START.md) to run the ETL demo in minutes!

### Installation

```bash
pip install memra
```

**📖 New to Memra?** For a complete beginner-friendly setup with step-by-step instructions, see our [Detailed Installation Guide](INSTALLATION_GUIDE.md) or run our automated setup script:

```bash
# Automated setup for new users
bash scripts/setup_newbie.sh
```

**🔧 Repository Structure:** This repo uses git submodules with sparse checkout to provide minimal access to infrastructure and workflow templates while keeping private content secure.

### Basic Example

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

## 🏗️ Core Architecture

### Agent
An AI worker that performs specific tasks using LLMs and tools. Agents have:
- **Role**: What they do (e.g., "Data Analyst", "Invoice Processor")
- **Job**: Specific task description
- **LLM**: Language model configuration
- **Tools**: External tools they can use
- **SOPs**: Standard operating procedures

### Department
A team of agents working together to accomplish a mission. Departments:
- **Coordinate multiple agents** in a workflow
- **Handle dependencies** between agents
- **Provide execution policies** (retries, timeouts, error handling)
- **Manage context** and data flow

### ExecutionEngine
Orchestrates the execution of departments and their workflows with:
- **Automatic agent coordination**
- **Tool integration** via MCP (Model Context Protocol)
- **Error handling and retries**
- **Execution tracing and monitoring**

### LLM
Configuration for language models used by agents, supporting:
- **Multiple model providers** (OpenAI, Anthropic, local models)
- **Custom parameters** (temperature, max tokens, etc.)
- **Model-specific configurations**

## 🔥 Real-World Examples

### ETL Invoice Processing Demo
**Complete end-to-end workflow** that processes PDF invoices using vision models and stores data in PostgreSQL:

```bash
# Run the ETL demo
python demos/etl_invoice_processing/etl_invoice_demo.py
```

This demo showcases:
- **Vision model integration** for PDF processing
- **Multi-agent workflow** (Extractor, Validator, Database Engineer)
- **MCP tool integration** (PostgreSQL, SQL execution)
- **Data validation and error handling**
- **Production-ready patterns**

### Smart File Discovery
Automatically discover and process files with intelligent routing:

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

### Accounts Payable Workflow
Complete accounts payable processing with validation and database integration:

```python
# See examples/accounts_payable_smart.py for full implementation
from memra import Department, Agent

ap_department = Department(
    name="Accounts Payable",
    mission="Process and validate vendor invoices",
    agents=[
        Agent(role="Invoice Extractor", ...),
        Agent(role="Data Validator", ...),
        Agent(role="Database Engineer", ...)
    ],
    workflow_order=["Invoice Extractor", "Data Validator", "Database Engineer"]
)
```

## 🛠️ Key Features

### 🔌 MCP Integration
Built-in support for Model Context Protocol (MCP) tools:
- **Database operations** (PostgreSQL, MySQL, etc.)
- **File system operations** (discovery, copying, processing)
- **API integrations** (REST, GraphQL, custom APIs)
- **Custom tool development** with simple Python functions

### 🎯 Declarative Workflows
Define workflows in terms of **what** you want to accomplish:

```python
# Instead of writing procedural code, declare your workflow
department = Department(
    name="Invoice Processing",
    mission="Extract, validate, and store invoice data",
    agents=[
        Agent(role="Extractor", job="Extract data from PDFs"),
        Agent(role="Validator", job="Validate extracted data"),
        Agent(role="Database Engineer", job="Store data in database")
    ],
    workflow_order=["Extractor", "Validator", "Database Engineer"]
)
```

### 🔄 Error Handling & Recovery
Built-in resilience with:
- **Automatic retries** with configurable policies
- **Fallback agents** for critical workflows
- **Validation at each step**
- **Comprehensive error reporting**

### 📊 Monitoring & Observability
Track workflow execution with:
- **Execution traces** showing agent and tool usage
- **Performance metrics** (timing, costs)
- **Error logs** with context
- **Audit trails** for compliance

### 🚀 Production Ready
Scale from prototype to production:
- **Async execution** for high throughput
- **Resource management** and connection pooling
- **Configuration management** for different environments
- **Security best practices** for API keys and credentials

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Detailed Installation Guide](INSTALLATION_GUIDE.md)** - Complete beginner-friendly setup instructions
- **[System Architecture](memra_system_architecture.md)** - Deep dive into Memra's design
- **[Text-to-SQL Guide](TEXT_TO_SQL_USAGE_GUIDE.md)** - Building database query workflows
- **[Examples Directory](examples/)** - Complete working examples
- **[Demos Directory](demos/)** - Advanced workflow demonstrations

## 🏢 Use Cases

### Financial Services
- **Invoice processing** and accounts payable automation
- **Document classification** and routing
- **Compliance monitoring** and reporting
- **Risk assessment** and fraud detection

### Healthcare
- **Medical record processing** and data extraction
- **Claims processing** and validation
- **Patient data analysis** and insights
- **Regulatory compliance** workflows

### Manufacturing
- **Quality control** and inspection workflows
- **Supply chain** optimization and monitoring
- **Equipment maintenance** scheduling
- **Production planning** and optimization

### Retail & E-commerce
- **Order processing** and fulfillment
- **Customer service** automation
- **Inventory management** and forecasting
- **Market analysis** and trend detection

## 🤝 Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/memra-platform/memra-sdk.git
cd memra-sdk

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ **Commercial use** - Use in proprietary software
- ✅ **Modification** - Modify and distribute
- ✅ **Distribution** - Distribute copies
- ✅ **Private use** - Use privately
- ❌ **Liability** - No warranty provided
- ❌ **Warranty** - No warranty provided

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/memra-platform/memra-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/memra-platform/memra-sdk/discussions)
- **Email**: hello@memra.com

## 🔗 Related Projects

- **[memra-workflows](https://github.com/memra-platform/memra-workflows)** - Production workflow templates
- **[memra-ops](https://github.com/memra-platform/memra-ops)** - Operations and deployment tools

---

**Built with ❤️ by the memra team** 
