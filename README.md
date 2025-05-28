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

## Documentation

Documentation is coming soon. For now, see the examples below and in the `examples/` directory.

## Example: Propane Delivery Workflow

See the `examples/propane_delivery.py` file for a complete example of how to use Memra to orchestrate a propane delivery workflow.

## Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Examples

```
├── examples/
│   ├── accounts_payable_client.py  # API-based example
│   ├── accounts_payable.py         # Local example
│   ├── invoice_processing.py       # Simple workflow
│   └── propane_delivery.py         # Domain example
├── memra/                  # Core SDK
├── logic/                  # Tool implementations  
├── local/dependencies/     # Database setup & schemas
└── docker-compose.yml      # Database setup
```
