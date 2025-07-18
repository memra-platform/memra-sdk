# Natural Language Agent Builder

**Create AI agents and workflows using natural language - as easy as writing a job posting!**

This demo allows you to create AI agents and workflows by simply describing what you need in plain English. No complex configuration, no technical knowledge required. Just describe the job and the system builds it for you.

## 🎯 What Makes This Special

### Before (Traditional Approach)
```bash
create agent parser
configure agent parser
# Role: Invoice Parser
# Tools: PDFProcessor
create agent validator
configure agent validator
# Role: Data Validator
# Tools: DataValidator
create department etl
configure department etl
# Agents: parser,validator,writer
```

### After (Natural Language Approach)
```
"I need a complete ETL pipeline for invoices"
```
→ System automatically creates all agents and workflow!

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
python run_natural_language_builder.py
```

#### Option 2: Run Directly
```bash
cd demos
python natural_language_builder.py
```

#### Option 3: See the Demo
```bash
cd demos
python natural_language_demo.py
```

## 💼 How to Use

### Single Agent Creation

Just describe what you need:

```
💼 Job Description > I need an agent to parse invoice PDFs
```

**System Response:**
```
🤖 Creating agent from: 'I need an agent to parse invoice PDFs'
✅ Created agent: agent_1
   Role: Data Extractor
   Job: I need an agent to parse invoice PDFs.
   Tools: ['PDFProcessor']

🤔 Does this look right? (y/n): y
✅ Agent 'agent_1' created successfully!
```

### Complete Workflow Creation

Describe a complete process:

```
💼 Job Description > I need a complete ETL pipeline for invoices
```

**System Response:**
```
🏢 Creating workflow from: 'I need a complete ETL pipeline for invoices'
✅ Created parser: Data Extractor
✅ Created validator: Data Validator
✅ Created writer: Data Writer

🏢 Created workflow: workflow_1
   Mission: Complete workflow: I need a complete ETL pipeline for invoices
   Agents: ['Data Extractor', 'Data Validator', 'Data Writer']
   Workflow: Data Extractor → Data Validator → Data Writer

🤔 Does this workflow look right? (y/n): y
✅ Workflow 'workflow_1' created successfully!

🚀 Would you like to run this workflow now? (y/n): y
```

## 🎯 Example Job Descriptions

### Single Agents
- `"I need an invoice parser"`
- `"Create a data validator"`
- `"Build me a database writer"`
- `"I want someone to process PDFs"`
- `"Need an agent to check data quality"`
- `"I need a SQL query generator"`

### Complete Workflows
- `"I need a complete ETL pipeline"`
- `"Build me an invoice processing team"`
- `"Create a document processing workflow"`
- `"Set up a data validation pipeline"`
- `"I need a team to handle invoices"`
- `"Create a workflow that extracts, validates, and loads data"`

## 🔧 Available Commands

### Basic Commands
- `help` - Show help message with examples
- `quit` / `exit` / `q` - Exit the demo
- `list` - List created agents and workflows
- `run` - Run a workflow
- `demo` - Run the complete ETL demo

### Natural Language Input
Just describe what you need in plain English!

## 🧠 How It Works

### 1. Natural Language Processing
The system analyzes your job description using keyword patterns:

- **PDF/Invoice/Document** → PDFProcessor tool
- **Validate/Check/Verify** → DataValidator tool  
- **Database/Insert/Save** → PostgresInsert tool
- **Pipeline/ETL/Complete** → Creates full workflow

### 2. Smart Tool Selection
Based on your description, the system automatically chooses appropriate tools:

```python
tool_patterns = {
    'pdf': ['PDFProcessor', 'InvoiceExtractionWorkflow'],
    'validation': ['DataValidator'],
    'database': ['PostgresInsert', 'SQLExecutor'],
    'etl': ['PDFProcessor', 'DataValidator', 'PostgresInsert']
}
```

### 3. Role Assignment
The system determines appropriate agent roles:

```python
role_patterns = {
    'parser': ['parse', 'extract', 'read', 'process'],
    'validator': ['validate', 'verify', 'check'],
    'writer': ['write', 'insert', 'save', 'store']
}
```

### 4. Workflow Creation
For complex requests, the system creates complete workflows with proper sequencing.

## 🎓 Learning Examples

### Example 1: Single Agent
**User Input:** `"I need an invoice parser"`

**System Creates:**
- **Agent:** Data Extractor
- **Role:** Extract data from source files
- **Tools:** PDFProcessor
- **Output:** invoice_data

### Example 2: Complete Workflow
**User Input:** `"I need a complete ETL pipeline for invoices"`

**System Creates:**
- **Agent 1:** Data Extractor (PDFProcessor)
- **Agent 2:** Data Validator (DataValidator)  
- **Agent 3:** Data Writer (PostgresInsert)
- **Workflow:** Data Extractor → Data Validator → Data Writer

### Example 3: Custom Request
**User Input:** `"I want someone to check data quality and fix errors"`

**System Creates:**
- **Agent:** Data Validator
- **Role:** Validate extracted data for quality and accuracy
- **Tools:** DataValidator
- **Output:** validated_data

## 🔍 Advanced Features

### 1. Confirmation System
The system always asks for confirmation before creating agents:
```
🤔 Does this look right? (y/n): 
```

### 2. Smart Suggestions
After creating agents, the system suggests next steps:
```
💡 You now have 3 agents. Say 'create a workflow' to combine them!
```

### 3. Interactive Execution
You can run workflows immediately after creation:
```
🚀 Would you like to run this workflow now? (y/n): 
```

### 4. Resource Management
Use `list` to see all created resources:
```
📋 CREATED RESOURCES:

🤖 AGENTS:
  - agent_1: I need an agent to parse invoice PDFs.
    Tools: ['PDFProcessor']

🏢 WORKFLOWS:
  - workflow_1: Complete workflow: I need a complete ETL pipeline for invoices
    Agents: ['Data Extractor', 'Data Validator', 'Data Writer']
```

## 🚀 The Vision

This natural language interface transforms AI agent creation from a technical task into a conversational experience. Instead of learning complex configuration syntax, users can simply describe their needs in plain English.

### The Future
Imagine being able to say:
- `"I need a team to process customer invoices and put them in our database"`
- `"Create a workflow that validates data quality and generates reports"`
- `"Build me an agent that answers customer questions using our knowledge base"`

And having the system automatically create sophisticated AI workflows!

## 🎯 Benefits

### For Users
- **No Technical Knowledge Required** - Just describe what you need
- **Fast Creation** - No complex configuration steps
- **Intuitive Interface** - Natural conversation style
- **Immediate Results** - Create and run workflows instantly

### For Developers
- **Extensible** - Easy to add new patterns and tools
- **Maintainable** - Clean, modular code structure
- **Educational** - Shows how natural language can drive complex systems

## 🔮 Future Enhancements

Potential improvements could include:
- **LLM Integration** - Use AI to better understand complex requests
- **Template System** - Pre-built job templates for common tasks
- **Visual Workflow Builder** - Convert to web-based interface
- **Advanced Validation** - More sophisticated input understanding
- **Workflow Templates** - Save and reuse common workflows

## 📊 Success Metrics

The natural language builder successfully:
- ✅ Understands 12+ different tool types
- ✅ Creates agents with appropriate roles and tools
- ✅ Builds complete workflows automatically
- ✅ Provides confirmation and feedback
- ✅ Enables immediate workflow execution
- ✅ Supports conversational interaction

## 🎉 Conclusion

The Natural Language Agent Builder represents a significant step forward in making AI workflow creation accessible to everyone. By translating natural language into sophisticated AI agents and workflows, it bridges the gap between human intent and technical implementation.

**The future of AI workflow creation is here - and it speaks your language!** 🚀

---

**Try it now:** `python run_natural_language_builder.py`

**Example:** `"I need a complete ETL pipeline for invoices"` 