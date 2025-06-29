import time
import logging
from typing import Dict, Any, List, Optional
from .models import Department, Agent, DepartmentResult, ExecutionTrace, DepartmentAudit
from .tool_registry import ToolRegistry
from .tool_registry_client import ToolRegistryClient

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """Engine that executes department workflows by coordinating agents and tools"""
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.api_client = ToolRegistryClient()
        self.last_execution_audit: Optional[DepartmentAudit] = None
    
    def execute_department(self, department: Department, input_data: Dict[str, Any]) -> DepartmentResult:
        """Execute a department workflow"""
        start_time = time.time()
        trace = ExecutionTrace()
        
        try:
            print(f"\n🏢 Starting {department.name} Department")
            print(f"📋 Mission: {department.mission}")
            print(f"👥 Team: {', '.join([agent.role for agent in department.agents])}")
            if department.manager_agent:
                print(f"👔 Manager: {department.manager_agent.role}")
            print(f"🔄 Workflow: {' → '.join(department.workflow_order)}")
            print("=" * 60)
            
            logger.info(f"Starting execution of department: {department.name}")
            
            # Initialize execution context
            context = {
                "input": input_data,
                "department_context": department.context or {},
                "results": {}
            }
            
            # Execute agents in workflow order
            for i, agent_role in enumerate(department.workflow_order, 1):
                print(f"\n🔄 Step {i}/{len(department.workflow_order)}: {agent_role}")
                
                agent = self._find_agent_by_role(department, agent_role)
                if not agent:
                    error_msg = f"Agent with role '{agent_role}' not found in department"
                    print(f"❌ Error: {error_msg}")
                    trace.errors.append(error_msg)
                    return DepartmentResult(
                        success=False,
                        error=error_msg,
                        trace=trace
                    )
                
                # Execute agent
                agent_start = time.time()
                result = self._execute_agent(agent, context, trace)
                agent_duration = time.time() - agent_start
                
                trace.agents_executed.append(agent.role)
                trace.execution_times[agent.role] = agent_duration
                
                if not result.get("success", False):
                    # Try fallback if available
                    if department.manager_agent and agent.role in (department.manager_agent.fallback_agents or {}):
                        fallback_role = department.manager_agent.fallback_agents[agent.role]
                        print(f"🔄 {department.manager_agent.role}: Let me try {fallback_role} as backup for {agent.role}")
                        fallback_agent = self._find_agent_by_role(department, fallback_role)
                        if fallback_agent:
                            logger.info(f"Trying fallback agent: {fallback_role}")
                            result = self._execute_agent(fallback_agent, context, trace)
                            trace.agents_executed.append(fallback_agent.role)
                    
                    if not result.get("success", False):
                        error_msg = f"Agent {agent.role} failed: {result.get('error', 'Unknown error')}"
                        print(f"❌ Workflow stopped: {error_msg}")
                        trace.errors.append(error_msg)
                        return DepartmentResult(
                            success=False,
                            error=error_msg,
                            trace=trace
                        )
                
                # Store result for next agent
                context["results"][agent.output_key] = result.get("data")
                print(f"✅ Step {i} completed in {agent_duration:.1f}s")
            
            # Execute manager agent for final validation if present
            if department.manager_agent:
                print(f"\n🔍 Final Review Phase")
                manager_start = time.time()
                
                # Prepare manager input with all workflow results
                manager_input = {
                    "workflow_results": context["results"],
                    "department_context": context["department_context"]
                }
                
                # Add connection if available
                if "connection" in context["input"]:
                    manager_input["connection"] = context["input"]["connection"]
                
                # Execute manager validation
                manager_result = self._execute_manager_validation(department.manager_agent, manager_input, trace)
                manager_duration = time.time() - manager_start
                
                trace.agents_executed.append(department.manager_agent.role)
                trace.execution_times[department.manager_agent.role] = manager_duration
                
                # Store manager validation results
                context["results"][department.manager_agent.output_key] = manager_result.get("data")
                
                # Check if manager validation failed
                if not manager_result.get("success", False):
                    error_msg = f"Manager validation failed: {manager_result.get('error', 'Unknown error')}"
                    print(f"❌ {error_msg}")
                    trace.errors.append(error_msg)
                    return DepartmentResult(
                        success=False,
                        error=error_msg,
                        trace=trace
                    )
                
                print(f"✅ Manager review completed in {manager_duration:.1f}s")
            
            # Create audit record
            total_duration = time.time() - start_time
            self.last_execution_audit = DepartmentAudit(
                agents_run=trace.agents_executed,
                tools_invoked=trace.tools_invoked,
                duration_seconds=total_duration
            )
            
            print(f"\n🎉 {department.name} Department workflow completed!")
            print(f"⏱️ Total time: {total_duration:.1f}s")
            print("=" * 60)
            
            return DepartmentResult(
                success=True,
                data=context["results"],
                trace=trace
            )
            
        except Exception as e:
            print(f"💥 Unexpected error in {department.name} Department: {str(e)}")
            logger.error(f"Execution failed: {str(e)}")
            trace.errors.append(str(e))
            return DepartmentResult(
                success=False,
                error=str(e),
                trace=trace
            )
    
    def _find_agent_by_role(self, department: Department, role: str) -> Optional[Agent]:
        """Find an agent by role in the department"""
        for agent in department.agents:
            if agent.role == role:
                return agent
        return None
    
    def _execute_agent(self, agent: Agent, context: Dict[str, Any], trace: ExecutionTrace) -> Dict[str, Any]:
        """Execute a single agent"""
        print(f"\n👤 {agent.role}: Hi! I'm starting my work now...")
        logger.info(f"Executing agent: {agent.role}")
        
        try:
            # Show what the agent is thinking about
            print(f"💭 {agent.role}: My job is to {agent.job.lower()}")
            
            # Prepare input data for agent
            agent_input = {}
            for key in agent.input_keys:
                if key in context["input"]:
                    agent_input[key] = context["input"][key]
                    print(f"📥 {agent.role}: I received '{key}' as input")
                elif key in context["results"]:
                    agent_input[key] = context["results"][key]
                    print(f"📥 {agent.role}: I got '{key}' from a previous agent")
                else:
                    print(f"🤔 {agent.role}: Hmm, I'm missing input '{key}' but I'll try to work without it")
                    logger.warning(f"Missing input key '{key}' for agent {agent.role}")
            
            # Always include connection string if available (for database tools)
            if "connection" in context["input"]:
                agent_input["connection"] = context["input"]["connection"]
            
            # Execute agent's tools
            result_data = {}
            tools_with_real_work = []
            tools_with_mock_work = []
            
            print(f"🔧 {agent.role}: I need to use {len(agent.tools)} tool(s) to complete my work...")
            
            for i, tool_spec in enumerate(agent.tools, 1):
                tool_name = tool_spec["name"] if isinstance(tool_spec, dict) else tool_spec.name
                hosted_by = tool_spec.get("hosted_by", "memra") if isinstance(tool_spec, dict) else tool_spec.hosted_by
                
                print(f"⚡ {agent.role}: Using tool {i}/{len(agent.tools)}: {tool_name}")
                
                trace.tools_invoked.append(tool_name)
                
                # Get tool from registry and execute
                print(f"🔍 {agent.role}: Tool {tool_name} is hosted by: {hosted_by}")
                if hosted_by == "memra":
                    # Use API client for server-hosted tools
                    print(f"🌐 {agent.role}: Using API client for {tool_name}")
                    config_to_pass = tool_spec.get("config") if isinstance(tool_spec, dict) else tool_spec.config
                    tool_result = self.api_client.execute_tool(
                        tool_name, 
                        hosted_by, 
                        agent_input,
                        config_to_pass
                    )
                else:
                    # Use local registry for MCP and other local tools
                    print(f"🏠 {agent.role}: Using local registry for {tool_name}")
                    config_to_pass = tool_spec.get("config") if isinstance(tool_spec, dict) else tool_spec.config
                    
                    # For MCP tools, merge department context MCP configuration
                    if hosted_by == "mcp":
                        mcp_config = {}
                        dept_context = context.get("department_context", {})
                        if "mcp_bridge_url" in dept_context:
                            mcp_config["bridge_url"] = dept_context["mcp_bridge_url"]
                        if "mcp_bridge_secret" in dept_context:
                            mcp_config["bridge_secret"] = dept_context["mcp_bridge_secret"]
                        
                        # Merge with tool-specific config if it exists
                        if config_to_pass:
                            mcp_config.update(config_to_pass)
                        config_to_pass = mcp_config
                    
                    print(f"🔧 {agent.role}: Config for {tool_name}: {config_to_pass}")
                    tool_result = self.tool_registry.execute_tool(
                        tool_name, 
                        hosted_by, 
                        agent_input,
                        config_to_pass
                    )
                
                if not tool_result.get("success", False):
                    print(f"😟 {agent.role}: Oh no! Tool {tool_name} failed: {tool_result.get('error', 'Unknown error')}")
                    return {
                        "success": False,
                        "error": f"Tool {tool_name} failed: {tool_result.get('error', 'Unknown error')}"
                    }
                
                # Check if this tool did real work or mock work
                tool_data = tool_result.get("data", {})
                if self._is_real_work(tool_name, tool_data):
                    tools_with_real_work.append(tool_name)
                    print(f"✅ {agent.role}: Great! {tool_name} did real work and gave me useful results")
                else:
                    tools_with_mock_work.append(tool_name)
                    print(f"🔄 {agent.role}: {tool_name} gave me simulated results (that's okay for testing)")
                
                result_data.update(tool_data)
            
            # Add metadata about real vs mock work
            result_data["_memra_metadata"] = {
                "agent_role": agent.role,
                "tools_real_work": tools_with_real_work,
                "tools_mock_work": tools_with_mock_work,
                "work_quality": "real" if tools_with_real_work else "mock"
            }
            
            # Agent reports completion
            if tools_with_real_work:
                print(f"🎉 {agent.role}: Perfect! I completed my work with real data processing")
            else:
                print(f"📝 {agent.role}: I finished my work, but used simulated data (still learning!)")
            
            print(f"📤 {agent.role}: Passing my results to the next agent via '{agent.output_key}'")
            
            return {
                "success": True,
                "data": result_data
            }
            
        except Exception as e:
            print(f"😰 {agent.role}: I encountered an error and couldn't complete my work: {str(e)}")
            logger.error(f"Agent {agent.role} execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _is_real_work(self, tool_name: str, tool_data: Dict[str, Any]) -> bool:
        """Determine if a tool did real work or returned mock data"""
        
        # Check for specific indicators of real work
        if tool_name == "PDFProcessor":
            # Real work if it has actual image paths and file size
            return (
                "metadata" in tool_data and 
                "file_size" in tool_data["metadata"] and
                tool_data["metadata"]["file_size"] > 1000 and  # Real file size
                "pages" in tool_data and
                len(tool_data["pages"]) > 0 and
                "image_path" in tool_data["pages"][0]
            )
        
        elif tool_name == "InvoiceExtractionWorkflow":
            # Real work if it has actual extracted data with specific vendor info
            return (
                "headerSection" in tool_data and
                "vendorName" in tool_data["headerSection"] and
                tool_data["headerSection"]["vendorName"] not in ["", "UNKNOWN", "Sample Vendor"] and
                "chargesSummary" in tool_data and
                "memra_checksum" in tool_data["chargesSummary"]
            )
        
        elif tool_name == "DatabaseQueryTool":
            # Real work if it loaded the actual schema file (more than 3 columns)
            return (
                "columns" in tool_data and
                len(tool_data["columns"]) > 3
            )
        
        elif tool_name == "DataValidator":
            # Real work if it actually validated real data with meaningful validation
            return (
                "validation_errors" in tool_data and
                isinstance(tool_data["validation_errors"], list) and
                "is_valid" in tool_data and
                # Check if it's validating real extracted data (not just mock data)
                len(str(tool_data)) > 100 and  # Real validation results are more substantial
                not tool_data.get("_mock", False)  # Not mock data
            )
        
        elif tool_name == "PostgresInsert":
            # Real work if it successfully inserted into a real database
            return (
                "success" in tool_data and
                tool_data["success"] == True and
                "record_id" in tool_data and
                isinstance(tool_data["record_id"], int) and  # Real DB returns integer IDs
                "database_table" in tool_data and  # Real implementation includes table name
                not tool_data.get("_mock", False)  # Not mock data
            )
        
        elif tool_name == "FileDiscovery":
            # Real work if it actually discovered files in a real directory
            return (
                "files" in tool_data and
                isinstance(tool_data["files"], list) and
                "directory" in tool_data and
                tool_data.get("success", False) == True
            )
            
        elif tool_name == "FileCopy":
            # Real work if it actually copied a file
            return (
                "destination_path" in tool_data and
                "source_path" in tool_data and
                tool_data.get("success", False) == True and
                tool_data.get("operation") == "copy_completed"
            )
        
        elif tool_name == "TextToSQL":
            # Real work if it actually executed SQL and returned real results
            return (
                "generated_sql" in tool_data and
                "results" in tool_data and
                isinstance(tool_data["results"], list) and
                tool_data.get("success", False) == True and
                not tool_data.get("_mock", False)  # Not mock data
            )
        
        # Default to mock work
        return False
    
    def get_last_audit(self) -> Optional[DepartmentAudit]:
        """Get audit information from the last execution"""
        return self.last_execution_audit 
    
    def _execute_manager_validation(self, manager_agent: Agent, manager_input: Dict[str, Any], trace: ExecutionTrace) -> Dict[str, Any]:
        """Execute manager agent to validate workflow results"""
        print(f"\n👔 {manager_agent.role}: Time for me to review everyone's work...")
        logger.info(f"Manager {manager_agent.role} validating workflow results")
        
        try:
            # Analyze workflow results for real vs mock work
            workflow_analysis = self._analyze_workflow_quality(manager_input["workflow_results"])
            
            print(f"🔍 {manager_agent.role}: Let me analyze what each agent accomplished...")
            
            # Prepare validation report
            validation_report = {
                "workflow_analysis": workflow_analysis,
                "validation_status": "pass" if workflow_analysis["overall_quality"] == "real" else "fail",
                "recommendations": [],
                "agent_performance": {}
            }
            
            # Analyze each agent's performance
            for result_key, result_data in manager_input["workflow_results"].items():
                if isinstance(result_data, dict) and "_memra_metadata" in result_data:
                    metadata = result_data["_memra_metadata"]
                    agent_role = metadata["agent_role"]
                    
                    if metadata["work_quality"] == "real":
                        print(f"👍 {manager_agent.role}: {agent_role} did excellent real work!")
                    else:
                        print(f"📋 {manager_agent.role}: {agent_role} completed their tasks but with simulated data")
                    
                    validation_report["agent_performance"][agent_role] = {
                        "work_quality": metadata["work_quality"],
                        "tools_real_work": metadata["tools_real_work"],
                        "tools_mock_work": metadata["tools_mock_work"],
                        "status": "completed_real_work" if metadata["work_quality"] == "real" else "completed_mock_work"
                    }
                    
                    # Add recommendations for mock work
                    if metadata["work_quality"] == "mock":
                        recommendation = f"Agent {agent_role} performed mock work - implement real {', '.join(metadata['tools_mock_work'])} functionality"
                        validation_report["recommendations"].append(recommendation)
                        print(f"💡 {manager_agent.role}: I recommend upgrading {agent_role}'s tools for production")
            
            # Overall workflow validation
            if workflow_analysis["overall_quality"] == "real":
                validation_report["summary"] = "Workflow completed successfully with real data processing"
                print(f"🎯 {manager_agent.role}: Excellent! This workflow is production-ready")
            elif workflow_analysis["overall_quality"].startswith("mixed"):
                validation_report["summary"] = "Workflow completed with mixed real and simulated data"
                print(f"⚖️ {manager_agent.role}: Good progress! Some agents are production-ready, others need work")
            else:
                validation_report["summary"] = "Workflow completed but with mock/simulated data - production readiness requires real implementations"
                print(f"🚧 {manager_agent.role}: This workflow needs more development before production use")
            
            real_percentage = workflow_analysis["real_work_percentage"]
            print(f"📊 {manager_agent.role}: Overall assessment: {real_percentage:.0f}% of agents did real work")
            
            return {
                "success": True,
                "data": validation_report
            }
            
        except Exception as e:
            print(f"😰 {manager_agent.role}: I had trouble analyzing the workflow: {str(e)}")
            logger.error(f"Manager validation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_workflow_quality(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the overall quality of workflow execution"""
        
        total_agents = 0
        real_work_agents = 0
        mock_work_agents = 0
        
        for result_key, result_data in workflow_results.items():
            if isinstance(result_data, dict) and "_memra_metadata" in result_data:
                metadata = result_data["_memra_metadata"]
                total_agents += 1
                
                if metadata["work_quality"] == "real":
                    real_work_agents += 1
                else:
                    mock_work_agents += 1
        
        # Determine overall quality
        if real_work_agents > 0 and mock_work_agents == 0:
            overall_quality = "real"
        elif real_work_agents > mock_work_agents:
            overall_quality = "mixed_mostly_real"
        elif real_work_agents > 0:
            overall_quality = "mixed_mostly_mock"
        else:
            overall_quality = "mock"
        
        return {
            "total_agents": total_agents,
            "real_work_agents": real_work_agents,
            "mock_work_agents": mock_work_agents,
            "overall_quality": overall_quality,
            "real_work_percentage": (real_work_agents / total_agents * 100) if total_agents > 0 else 0
        } 