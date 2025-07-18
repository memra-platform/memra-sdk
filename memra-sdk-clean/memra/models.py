from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field

class LLM(BaseModel):
    model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    stop: Optional[List[str]] = None

class Tool(BaseModel):
    name: str
    hosted_by: str = "memra"  # or "mcp" for customer's Model Context Protocol
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class Agent(BaseModel):
    role: str
    job: str
    llm: Optional[Union[LLM, Dict[str, Any]]] = None
    sops: List[str] = Field(default_factory=list)
    tools: List[Union[Tool, Dict[str, Any]]] = Field(default_factory=list)
    systems: List[str] = Field(default_factory=list)
    input_keys: List[str] = Field(default_factory=list)
    output_key: str
    allow_delegation: bool = False
    fallback_agents: Optional[Dict[str, str]] = None
    config: Optional[Dict[str, Any]] = None
    custom_processing: Optional[Any] = None  # Function to call after tool execution

class ExecutionPolicy(BaseModel):
    retry_on_fail: bool = True
    max_retries: int = 2
    halt_on_validation_error: bool = True
    timeout_seconds: int = 300

class ExecutionTrace(BaseModel):
    agents_executed: List[str] = Field(default_factory=list)
    tools_invoked: List[str] = Field(default_factory=list)
    execution_times: Dict[str, float] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    
    def show(self):
        """Display execution trace information"""
        print("=== Execution Trace ===")
        print(f"Agents executed: {', '.join(self.agents_executed)}")
        print(f"Tools invoked: {', '.join(self.tools_invoked)}")
        if self.errors:
            print(f"Errors: {', '.join(self.errors)}")

class DepartmentResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    trace: ExecutionTrace = Field(default_factory=ExecutionTrace)

class DepartmentAudit(BaseModel):
    agents_run: List[str]
    tools_invoked: List[str]
    duration_seconds: float
    total_cost: Optional[float] = None

class Department(BaseModel):
    name: str
    mission: str
    agents: List[Agent]
    manager_agent: Optional[Agent] = None
    default_llm: Optional[LLM] = None
    workflow_order: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    execution_policy: Optional[ExecutionPolicy] = None
    context: Optional[Dict[str, Any]] = None

    def run(self, input: Dict[str, Any]) -> DepartmentResult:
        """
        Execute the department workflow with the given input data.
        """
        # Import here to avoid circular imports
        from .execution import ExecutionEngine
        
        engine = ExecutionEngine()
        return engine.execute_department(self, input)
    
    def audit(self) -> DepartmentAudit:
        """
        Return audit information about the last execution.
        """
        # Import here to avoid circular imports
        from .execution import ExecutionEngine
        
        engine = ExecutionEngine()
        audit = engine.get_last_audit()
        if audit:
            return audit
        else:
            return DepartmentAudit(
                agents_run=[],
                tools_invoked=[],
                duration_seconds=0.0
            ) 