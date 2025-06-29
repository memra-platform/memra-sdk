# Memra SDK

The core Memra framework for building AI-powered business workflows.

## Installation

```bash
pip install memra
```

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

## License

MIT License - see LICENSE file for details. 