# Memra SDK

A declarative orchestration framework for AI-powered business workflows. Think of it as "Kubernetes for business logic" where agents are the pods and departments are the deployments.

## 🚀 Team Setup

**New team member?** See the complete setup guide: **[TEAM_SETUP.md](TEAM_SETUP.md)**

This includes:
- Database setup (PostgreSQL + Docker)
- Local development environment
- Testing instructions
- Troubleshooting guide

## Quick Start

```python
from memra.sdk.models import Agent, Department, Tool

# Define your agents
data_extractor = Agent(
    role="Data Extraction Specialist",
    job="Extract and validate data",
    tools=[Tool(name="DataExtractor", hosted_by="memra")],
    input_keys=["input_data"],
    output_key="extracted_data"
)

# Create a department
dept = Department(
    name="Data Processing",
    mission="Process and validate data",
    agents=[data_extractor]
)

# Run the workflow
result = dept.run({"input_data": {...}})
```

## Installation

```bash
pip install memra
```

## API Access

Memra requires an API key to execute workflows on the hosted infrastructure.

### Get Your API Key
Contact [info@memra.co](mailto:info@memra.co) for API access.

### Set Your API Key
```bash
# Set environment variable
export MEMRA_API_KEY="your-api-key-here"

# Or add to your shell profile for persistence
echo 'export MEMRA_API_KEY="your-api-key-here"' >> ~/.zshrc
```

### Test Your Setup
```bash
python examples/accounts_payable_client.py
```

## Architecture

The Memra platform consists of three main components:

- **Memra SDK** (this repository): Client library for building and executing workflows
- **Memra Server**: Hosted infrastructure for heavy AI processing tools
- **MCP Bridge**: Local execution environment for database operations

Tools are automatically routed between server and local execution based on their `hosted_by` configuration.

## Documentation

Documentation is coming soon. For now, see the examples below and in the `examples/` directory.

## Example: Propane Delivery Workflow

See the `examples/propane_delivery.py` file for a complete example of how to use Memra to orchestrate a propane delivery workflow.

## Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Repository Structure

```
├── examples/                       # Example workflows and use cases
│   ├── accounts_payable_client.py  # API-based accounts payable workflow
│   ├── accounts_payable_mcp.py     # MCP-enabled accounts payable workflow
│   ├── invoice_processing.py       # Simple invoice processing example
│   └── propane_delivery.py         # Propane delivery domain example
├── memra/                          # Core SDK package
│   ├── __init__.py                 # Package initialization
│   ├── tool_registry.py            # Tool discovery and routing
│   └── sdk/                        # SDK components
│       ├── __init__.py
│       ├── client.py               # API client
│       ├── execution_engine.py     # Workflow execution
│       └── models.py               # Core data models
├── docs/                           # Documentation
├── tests/                          # Test suite
├── local/dependencies/             # Local development setup
└── scripts/                        # Utility scripts
```
