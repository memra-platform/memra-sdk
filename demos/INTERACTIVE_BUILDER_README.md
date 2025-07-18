# Interactive Agent Builder Demo

This demo allows you to interactively construct ETL workflow agents through a text-based interface, building on the existing ETL workflow but making it interactive and educational.

## 🎯 What You'll Learn

- How to create and configure AI agents
- How to assign tools to agents
- How to organize agents into departments (workflows)
- How to run and test your custom workflows
- The fundamentals of building AI-powered ETL pipelines

## 🚀 Quick Start

### Prerequisites

1. **Conda Environment**: Make sure you're in the `memra` conda environment:
   ```bash
   conda activate memra
   ```

2. **Docker Services**: Ensure PostgreSQL is running:
   ```bash
   docker compose up -d postgres
   ```

### Running the Demo

#### Option 1: Use the Launcher (Recommended)
```bash
cd demos
python run_interactive_builder.py
```

#### Option 2: Run Directly
```bash
cd demos
python interactive_agent_builder.py
```

## 📚 Available Commands

### Basic Commands
- `help` - Show help message
- `quit` / `exit` / `q` - Exit the demo
- `clear` - Clear all created agents and departments

### Resource Management
- `list [agents|tools|departments]` - List created resources
- `show <name>` - Show details of a specific resource
- `create agent <name>` - Create a new agent
- `create department <name>` - Create a new department

### Configuration
- `configure agent <name>` - Configure an agent's role and tools
- `configure department <name>` - Configure a department's agents

### Execution
- `run workflow <name>` - Run a specific workflow
- `demo` - Run the complete ETL demo workflow

## 🎯 Example Workflow

Here's a step-by-step example of building an ETL workflow:

```bash
# 1. Create agents
create agent parser
create agent validator
create agent writer

# 2. Configure each agent
configure agent parser
# Role: Invoice Parser
# Tools: PDFProcessor

configure agent validator
# Role: Data Validator
# Tools: DataValidator

configure agent writer
# Role: Database Writer
# Tools: PostgresInsert,SQLExecutor

# 3. Create and configure department
create department etl
configure department etl
# Agents: parser,validator,writer

# 4. Run the workflow
run workflow etl
```

## 🔧 Available Tools

The demo includes these pre-configured tools:

- **PDFProcessor**: Extract data from PDF files
- **DataValidator**: Validate extracted data against schema
- **PostgresInsert**: Insert data into PostgreSQL database
- **SQLExecutor**: Execute SQL queries
- **TextToSQLGenerator**: Generate SQL from natural language questions

## 🏗️ Building Your Own Workflows

### Step 1: Plan Your Workflow
Think about what agents you need and what each should do:
- **Data Extraction Agent**: Gets data from source files
- **Data Validation Agent**: Checks data quality and format
- **Data Transformation Agent**: Transforms data as needed
- **Data Loading Agent**: Saves data to destination

### Step 2: Create Agents
```bash
create agent extractor
create agent validator
create agent transformer
create agent loader
```

### Step 3: Configure Agents
For each agent, specify:
- **Role**: What the agent does (e.g., "Invoice Parser", "Data Validator")
- **Tools**: Which tools the agent can use

### Step 4: Create Department
```bash
create department my_workflow
configure department my_workflow
# Select your agents in the order they should run
```

### Step 5: Test Your Workflow
```bash
run workflow my_workflow
```

## 🎓 Learning Objectives

After completing this demo, you should understand:

1. **Agent Architecture**: How agents are structured with roles and tools
2. **Tool Integration**: How tools are assigned to agents
3. **Workflow Design**: How to organize agents into departments
4. **ETL Concepts**: Extract, Transform, Load pipeline design
5. **Interactive Development**: How to iteratively build and test workflows

## 🔍 Troubleshooting

### Common Issues

1. **"Agent not found"**: Make sure you created the agent first with `create agent <name>`
2. **"No tools available"**: The demo should automatically load tools. Try restarting if needed.
3. **"Demo data not found"**: Ensure you're running from the `demos` directory
4. **"PostgreSQL not running"**: Start it with `docker compose up -d postgres`

### Getting Help

- Use `help` command for available commands
- Use `list` to see what resources you've created
- Use `show <name>` to inspect specific resources
- Use `demo` to run the pre-built ETL workflow as a reference

## 🚀 Next Steps

After mastering the interactive builder:

1. **Explore the Code**: Look at `interactive_agent_builder.py` to understand the implementation
2. **Modify Tools**: Add your own custom tools to the available tools list
3. **Build Real Workflows**: Use the same concepts to build production workflows
4. **Extend the Demo**: Add new features like agent templates or workflow templates

## 📖 Related Resources

- [ETL Invoice Processing Demo](../etl_invoice_processing/) - The original ETL demo
- [Memra SDK Documentation](../../README.md) - Full SDK documentation
- [Tool Registry](../../memra/tool_registry.py) - How tools are registered and discovered
- [Execution Engine](../../memra/execution.py) - How workflows are executed

---

**Happy Building! 🎉**

Build your own AI-powered workflows and see how easy it is to create digital employees that do real work! 