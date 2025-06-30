# Memra System Architecture

## System Overview

Memra is a declarative orchestration framework for AI-powered business workflows. Think of it as "Kubernetes for business logic" where agents are the pods and departments are the deployments.

## Architecture Diagram

```mermaid
graph TB
    %% Client Application Layer
    subgraph "Client Application"
        CA[Client Application]
        CA --> |"1. Define Agents & Department"| SDK
    end
    
    %% Memra SDK Layer
    subgraph "Memra SDK"
        SDK[Memra SDK]
        SDK --> |"2. Create Execution Engine"| EE
        EE[Execution Engine]
        EE --> |"3. Execute Department"| TRC
        EE --> |"4. Execute MCP Tools"| TR
    end
    
    %% Tool Registry Components
    subgraph "Tool Registry Layer"
        TRC[Tool Registry Client]
        TR[Tool Registry]
        TRC --> |"5. API Calls"| API
        TR --> |"6. MCP Bridge Calls"| MCP
    end
    
    %% External Services
    subgraph "External Services"
        API[Memra API Server<br/>https://api.memra.co]
        MCP[MCP Bridge<br/>localhost:8081]
        DB[(PostgreSQL Database)]
    end
    
    %% Tool Execution Flow
    subgraph "Tool Execution"
        API --> |"7. Server Tools"| ST[Server Tools<br/>• PDFProcessor<br/>• OCRTool<br/>• InvoiceExtractionWorkflow<br/>• DatabaseQueryTool]
        MCP --> |"8. MCP Tools"| MT[MCP Tools<br/>• DataValidator<br/>• PostgresInsert<br/>• TextToSQL<br/>• SQLExecutor]
        MT --> |"9. Database Operations"| DB
    end
    
    %% Data Flow
    CA -.->|"Input Data"| EE
    EE -.->|"Results"| CA
    
    %% Styling
    classDef client fill:#e1f5fe
    classDef sdk fill:#f3e5f5
    classDef registry fill:#e8f5e8
    classDef external fill:#fff3e0
    classDef tools fill:#fce4ec
    
    class CA client
    class SDK,EE sdk
    class TRC,TR registry
    class API,MCP,DB external
    class ST,MT tools
```

## Detailed Workflow Diagram

```mermaid
sequenceDiagram
    participant Client as Client Application
    participant SDK as Memra SDK
    participant EE as Execution Engine
    participant TRC as Tool Registry Client
    participant API as Memra API Server
    participant TR as Tool Registry
    participant MCP as MCP Bridge
    participant DB as PostgreSQL Database
    
    %% Initialization
    Client->>SDK: Define Agents & Department
    SDK->>EE: Create Execution Engine
    EE->>TRC: Initialize API Client
    EE->>TR: Initialize Local Registry
    
    %% Health Check
    TRC->>API: Check API Health
    API-->>TRC: Health Status
    
    %% Department Execution
    Client->>EE: Execute Department(input_data)
    
    %% Agent Execution Loop
    loop For each agent in workflow_order
        EE->>EE: Find agent by role
        EE->>EE: Prepare agent input data
        
        %% Tool Execution
        loop For each tool in agent.tools
            alt Tool hosted_by == "memra"
                EE->>TRC: Execute tool via API
                TRC->>API: POST /tools/execute
                API->>API: Process with server tools
                API-->>TRC: Tool results
                TRC-->>EE: Tool results
            else Tool hosted_by == "mcp"
                EE->>TR: Execute MCP tool
                TR->>MCP: POST /execute_tool
                MCP->>DB: Database operations
                DB-->>MCP: Query results
                MCP-->>TR: Tool results
                TR-->>EE: Tool results
            end
        end
        
        EE->>EE: Store agent results
        EE->>EE: Check for real vs mock work
    end
    
    %% Manager Validation
    EE->>EE: Execute manager agent
    EE->>EE: Analyze workflow quality
    EE->>EE: Generate validation report
    
    %% Return Results
    EE-->>Client: DepartmentResult
    Client->>Client: Display results & trace
```

## Component Relationships

```mermaid
graph LR
    %% Core Models
    subgraph "Core Models"
        Agent[Agent]
        Department[Department]
        LLM[LLM]
        Tool[Tool]
    end
    
    %% Execution Components
    subgraph "Execution"
        EE[Execution Engine]
        TRC[Tool Registry Client]
        TR[Tool Registry]
    end
    
    %% Data Structures
    subgraph "Data Structures"
        DR[Department Result]
        ET[Execution Trace]
        DA[Department Audit]
    end
    
    %% Relationships
    Department --> Agent
    Department --> LLM
    Agent --> Tool
    Agent --> LLM
    
    EE --> TRC
    EE --> TR
    EE --> DR
    EE --> ET
    EE --> DA
    
    %% Styling
    classDef models fill:#e3f2fd
    classDef execution fill:#f1f8e9
    classDef data fill:#fff8e1
    
    class Agent,Department,LLM,Tool models
    class EE,TRC,TR execution
    class DR,ET,DA data
```

## Tool Routing Architecture

```mermaid
graph TB
    %% Input
    Input[Tool Execution Request]
    
    %% Decision Point
    Input --> Decision{hosted_by?}
    
    %% Server Tools Path
    Decision -->|"memra"| ServerPath[Server Tools Path]
    ServerPath --> API[Memra API Server]
    API --> ServerTools[Server Tools<br/>• PDFProcessor<br/>• OCRTool<br/>• InvoiceExtractionWorkflow<br/>• DatabaseQueryTool<br/>• FileReader<br/>• FileDiscovery]
    
    %% MCP Tools Path
    Decision -->|"mcp"| MCPPath[MCP Tools Path]
    MCPPath --> MCP[MCP Bridge]
    MCP --> MCPTools[MCP Tools<br/>• DataValidator<br/>• PostgresInsert<br/>• TextToSQL<br/>• SQLExecutor<br/>• TextToSQLGenerator]
    MCPTools --> DB[(PostgreSQL)]
    
    %% Results
    ServerTools --> Results[Tool Results]
    MCPTools --> Results
    
    %% Styling
    classDef input fill:#e8f5e8
    classDef decision fill:#fff3e0
    classDef server fill:#e3f2fd
    classDef mcp fill:#fce4ec
    classDef results fill:#f1f8e9
    
    class Input input
    class Decision decision
    class ServerPath,API,ServerTools server
    class MCPPath,MCP,MCPTools mcp
    class Results results
```

## Key Features

### 1. **Declarative Workflow Definition**
- Define agents with roles, jobs, and tools
- Create departments with workflow order
- Specify execution policies and dependencies

### 2. **Hybrid Tool Execution**
- **Server Tools**: Heavy AI processing (PDF, OCR, ML) on Memra API
- **MCP Tools**: Database operations and local processing via MCP Bridge
- Automatic routing based on `hosted_by` configuration

### 3. **Intelligent Workflow Management**
- Sequential agent execution in workflow order
- Manager agent for final validation and quality assessment
- Real vs mock work detection and reporting
- Comprehensive execution tracing and auditing

### 4. **Production-Ready Features**
- API key authentication
- Health checks and status monitoring
- Error handling and retry logic
- Execution timeouts and policies
- Detailed audit trails

### 5. **Extensible Architecture**
- Plugin-based tool system
- Support for custom MCP tools
- Configurable LLM models per agent
- Context-aware execution

## Usage Example

```python
from memra import Agent, Department, LLM, ExecutionEngine

# Define agents
etl_agent = Agent(
    role="Data Engineer",
    job="Extract invoice schema from database",
    tools=[{"name": "DatabaseQueryTool", "hosted_by": "memra"}],
    output_key="invoice_schema"
)

parser_agent = Agent(
    role="Invoice Parser", 
    job="Extract structured data from invoice PDF",
    tools=[
        {"name": "PDFProcessor", "hosted_by": "memra"},
        {"name": "InvoiceExtractionWorkflow", "hosted_by": "memra"}
    ],
    input_keys=["file", "invoice_schema"],
    output_key="invoice_data"
)

# Create department
department = Department(
    name="Accounts Payable",
    mission="Process invoices accurately",
    agents=[etl_agent, parser_agent],
    workflow_order=["Data Engineer", "Invoice Parser"]
)

# Execute workflow
engine = ExecutionEngine()
result = engine.execute_department(department, {
    "file": "invoice.pdf",
    "connection": "postgresql://user@localhost/db"
})
```

This architecture provides a scalable, maintainable framework for building complex AI-powered business workflows with clear separation of concerns and flexible tool execution strategies. 