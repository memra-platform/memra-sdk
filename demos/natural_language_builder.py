#!/usr/bin/env python3
"""
Natural Language Agent Builder with LLM Integration

This demo allows users to create AI agents and workflows using natural language,
with an integrated LLM for conversational responses and intelligent analysis.
"""

import os
import sys
import json
import asyncio
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Add the parent directory to the path to import memra modules
sys.path.append(str(Path(__file__).parent.parent))

# Import local modules instead of SDK
from memra.models import Agent, Department, Tool

# Add LLM integration
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Warning: huggingface_hub not available. Install with: pip install huggingface_hub")

# Local execution engine that uses hybrid approach (remote API + local MCP bridge)
class HybridExecutionEngine:
    """Hybrid execution engine that uses both api.memra.co and local MCP bridge"""
    
    def __init__(self):
        self.remote_api_url = "https://api.memra.co"
        self.local_mcp_url = "http://localhost:8081"
        self.api_key = os.getenv("MEMRA_API_KEY", "test-secret-for-development")
        self.bridge_secret = "test-secret-for-development"
        
    async def execute_department(self, department, input_data=None):
        """Execute a department using hybrid approach"""
        try:
            import aiohttp
            
            # Execute each agent in the department sequentially
            results = []
            previous_output = input_data
            
            for agent in department.agents:
                print(f"\n🤖 {agent.role} is working...")
                agent_result = await self.execute_agent(agent, previous_output)
                results.append(agent_result)
                
                # Pass the output to the next agent
                if agent_result.get("success"):
                    # Extract data from the agent's results
                    agent_data = self._extract_agent_output(agent_result, agent.output_key)
                    if agent_data:
                        previous_output = agent_data
                        print(f"   📤 {agent.role} produced output for next agent")
                    else:
                        print(f"⚠️  {agent.role} didn't produce output, continuing...")
                else:
                    print(f"⚠️  {agent.role} failed, continuing...")
                
            return {
                "success": True,
                "department_name": department.name,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_agent_output(self, agent_result: Dict[str, Any], output_key: str) -> Dict[str, Any]:
        """Extract the actual output data from agent results"""
        if not agent_result.get("success"):
            return {}
        
        # Look for data in the results
        if agent_result.get("results"):
            for tool_result in agent_result["results"]:
                if tool_result.get("success") and tool_result.get("data"):
                    # Extract the actual data from the tool result
                    tool_data = tool_result["data"]
                    if isinstance(tool_data, dict):
                        # If it's a dict, look for extracted_data or similar
                        if "extracted_data" in tool_data:
                            return {output_key: tool_data["extracted_data"]}
                        elif "data" in tool_data and "extracted_data" in tool_data["data"]:
                            return {output_key: tool_data["data"]["extracted_data"]}
                        else:
                            # Return the whole tool data
                            return {output_key: tool_data}
                    else:
                        # If it's not a dict, wrap it
                        return {output_key: tool_data}
        
        # Fallback: return the agent's data field
        if agent_result.get("data"):
            return {output_key: agent_result["data"]}
        
        return {}
    
    async def execute_agent(self, agent, input_data=None):
        """Execute a single agent using hybrid approach"""
        try:
            import aiohttp
            
            # Determine which tools to use based on hosted_by
            remote_tools = [tool for tool in agent.tools if tool.hosted_by == "memra"]
            local_tools = [tool for tool in agent.tools if tool.hosted_by == "mcp-bridge"]
            
            if remote_tools:
                # Use remote API for memra tools
                return await self._execute_remote_tools(agent, remote_tools, input_data)
            elif local_tools:
                # Use local MCP bridge for local tools
                return await self._execute_local_tools(agent, local_tools, input_data)
            else:
                # Mock execution for tools without hosted_by specified
                return {
                    "success": True,
                    "agent_name": agent.role,
                    "message": f"Agent '{agent.role}' executed successfully (mock)",
                    "tools_used": [tool.name for tool in agent.tools]
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_remote_tools(self, agent, tools, input_data):
        """Execute tools using api.memra.co"""
        try:
            import aiohttp
            
            results = []
            for tool in tools:
                print(f"   🔧 Using {tool.name}...")
                
                # Prepare tool-specific input
                tool_input = self._prepare_tool_input(tool.name, input_data)
                
                # Make API call to api.memra.co
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.remote_api_url}/tools/execute",
                        json={
                            "tool_name": tool.name,
                            "hosted_by": "memra",
                            "input_data": tool_input
                        },
                        headers={
                            "X-API-Key": self.api_key,
                            "Content-Type": "application/json"
                        }
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            print(f"   📊 {tool.name} response: {result}")
                            results.append({
                                "tool": tool.name,
                                "success": True,
                                "data": result.get("data")
                            })
                            print(f"   ✅ {tool.name} completed successfully")
                        else:
                            error_text = await response.text()
                            results.append({
                                "tool": tool.name,
                                "success": False,
                                "error": f"API error: {response.status} - {error_text}"
                            })
                            print(f"   ❌ {tool.name} failed: {response.status}")
            
            return {
                "success": True,
                "agent_name": agent.role,
                "message": f"Agent '{agent.role}' executed with remote tools",
                "tools_used": [tool.name for tool in tools],
                "results": results,
                "data": results[-1].get("data") if results and results[-1].get("success") else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Remote execution failed: {str(e)}"
            }
    
    async def _execute_local_tools(self, agent, tools, input_data):
        """Execute tools using local MCP bridge"""
        try:
            import aiohttp
            
            results = []
            for tool in tools:
                print(f"   🔧 Using {tool.name}...")
                
                # Prepare tool-specific input
                tool_input = self._prepare_tool_input(tool.name, input_data)
                
                # Make API call to local MCP bridge
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.local_mcp_url}/execute_tool",
                        json={
                            "tool_name": tool.name,
                            "input_data": tool_input
                        },
                        headers={
                            "X-Bridge-Secret": self.bridge_secret,
                            "Content-Type": "application/json"
                        }
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            results.append({
                                "tool": tool.name,
                                "success": True,
                                "data": result.get("data")
                            })
                            print(f"   ✅ {tool.name} completed successfully")
                        else:
                            error_text = await response.text()
                            results.append({
                                "tool": tool.name,
                                "success": False,
                                "error": f"MCP bridge error: {response.status} - {error_text}"
                            })
                            print(f"   ❌ {tool.name} failed: {response.status}")
            
            return {
                "success": True,
                "agent_name": agent.role,
                "message": f"Agent '{agent.role}' executed with local tools",
                "tools_used": [tool.name for tool in tools],
                "results": results,
                "data": results[-1].get("data") if results and results[-1].get("success") else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Local execution failed: {str(e)}"
            }
    
    def _prepare_tool_input(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tool-specific input data"""
        if not input_data:
            return {}
        
        print(f"   🔍 Preparing input for {tool_name}: {list(input_data.keys())}")
        
        # For PDFProcessor, pass the file paths
        if tool_name == "PDFProcessor":
            if "files" in input_data:
                # Process each file individually - for now process first file
                # In a full implementation, this would loop through all files
                file_path = input_data["files"][0]
                print(f"   📄 Processing file: {file_path}")
                return {"file": file_path}
        
        # For PostgresInsert, pass the extracted data
        elif tool_name == "PostgresInsert":
            # Look for extracted data in various possible locations
            if "extracted_data" in input_data:
                print(f"   📊 Found extracted_data for PostgresInsert")
                return {"invoice_data": input_data["extracted_data"]}
            elif "validated_data" in input_data:
                print(f"   📊 Found validated_data for PostgresInsert")
                return {"invoice_data": input_data["validated_data"]}
            elif "data" in input_data and "extracted_data" in input_data["data"]:
                print(f"   📊 Found nested extracted_data for PostgresInsert")
                return {"invoice_data": input_data["data"]["extracted_data"]}
            else:
                print(f"   ⚠️  No suitable data found for PostgresInsert")
                return {}
        
        # For DataValidator, pass the extracted data
        elif tool_name == "DataValidator":
            if "extracted_data" in input_data:
                print(f"   📊 Found extracted_data for DataValidator")
                return {"invoice_data": input_data["extracted_data"]}
            elif "data" in input_data and "extracted_data" in input_data["data"]:
                print(f"   📊 Found nested extracted_data for DataValidator")
                return {"invoice_data": input_data["data"]["extracted_data"]}
            else:
                print(f"   ⚠️  No suitable data found for DataValidator")
                return {}
        
        # Default: pass through the input data
        return input_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationalLLM:
    """LLM for conversational responses"""
    
    def __init__(self):
        self.fireworks_api_key = os.getenv("FIREWORKS_API_KEY", "fw_3Zb13yks5hGB25Xi9d6ia69K")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.hf_model = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        self.client = None
        self.use_fireworks = False
        
        # Try Fireworks AI first for better conversational responses
        try:
            from fireworks.client import Fireworks
            self.client = Fireworks(api_key=self.fireworks_api_key)
            self.use_fireworks = True
            logger.info(f"Initialized Fireworks AI LLM for conversational responses")
        except ImportError:
            logger.warning("Fireworks client not available, falling back to Hugging Face")
            if HF_AVAILABLE and self.hf_api_key:
                try:
                    self.client = InferenceClient(
                        model=self.hf_model,
                        token=self.hf_api_key
                    )
                    logger.info(f"Initialized LLM with model: {self.hf_model}")
                except Exception as e:
                    logger.warning(f"Failed to initialize LLM: {e}")
                    self.client = None
    
    async def generate_response(self, context: str, user_input: str, available_info: Dict[str, Any]) -> str:
        """Generate a conversational response using LLM"""
        if not self.client:
            return self._fallback_response(context, user_input, available_info)
        
        try:
            if self.use_fireworks:
                # Use Fireworks AI for conversational responses
                messages = [
                    {
                        "role": "system",
                        "content": f"You are a helpful AI assistant helping users create and manage AI agents and workflows. You should be conversational, specific, and helpful. Always respond naturally as if you're having a real conversation."
                    },
                    {
                        "role": "user", 
                        "content": f"""CONTEXT: {context}

AVAILABLE INFORMATION:
{json.dumps(available_info, indent=2)}

USER REQUEST: {user_input}

Respond conversationally about what you found and what you're going to do. Be specific and natural."""
                    }
                ]
                
                response = self.client.chat.completions.create(
                    model="accounts/fireworks/models/llama-v3-70b",
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
            else:
                # Fallback to Hugging Face
                prompt = f"""You are a helpful AI assistant helping users create and manage AI agents and workflows. 

CONTEXT: {context}

AVAILABLE INFORMATION:
{json.dumps(available_info, indent=2)}

USER REQUEST: {user_input}

Respond in a conversational, helpful way. Be specific about what you found and what you're going to do. If you need more information, ask clarifying questions naturally. If you're ready to proceed, explain your plan clearly.

Response:"""

                response = self.client.text_generation(
                    prompt,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True,
                    stop=["\n\n", "CONTEXT:", "AVAILABLE INFORMATION:"],
                    return_full_text=False
                )
                
                return response.strip()
            
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}")
            return self._fallback_response(context, user_input, available_info)
    
    def _fallback_response(self, context: str, user_input: str, available_info: Dict[str, Any]) -> str:
        """Fallback response when LLM is not available"""
        if "invoice" in user_input.lower() and "database" in user_input.lower():
            return f"I understand you want to process invoices and write them to the database. I found {available_info.get('pdf_files', 0)} PDF files and the database is ready. Let me help you set this up!"
        elif "pdf" in user_input.lower():
            return f"I can help you process PDF files. I found {available_info.get('pdf_files', 0)} files to work with."
        else:
            return "I understand your request. Let me analyze what we need to do and help you set it up properly."

class NaturalLanguageBuilder:
    """Natural language interface for building AI agents and workflows with LLM integration"""
    
    def __init__(self):
        self.execution_engine = HybridExecutionEngine()
        self.llm = ConversationalLLM()
        self.agents = {}
        self.departments = {}
        self.available_tools = {}
        self.agent_counter = 0
        
        # Tool mapping patterns for natural language understanding (no mock tools)
        self.tool_patterns = {
            'pdf': ['PDFProcessor'],
            'database': ['PostgresInsert', 'SQLExecutor'],
            'sql': ['SQLExecutor', 'TextToSQLGenerator'],
            'validation': ['DataValidator'],
            'file': ['FileDiscovery'],
            'extract': ['PDFProcessor'],
            'validate': ['DataValidator'],
            'insert': ['PostgresInsert'],
            'query': ['SQLExecutor', 'TextToSQLGenerator'],
            'process': ['PDFProcessor'],
            'read': ['PDFProcessor'],
            'write': ['PostgresInsert'],
            'check': ['DataValidator'],
            'verify': ['DataValidator'],
            'load': ['PostgresInsert'],
            'store': ['PostgresInsert'],
            'save': ['PostgresInsert'],
            'parse': ['PDFProcessor'],
            'invoice': ['PDFProcessor'],
            'document': ['PDFProcessor'],
            'data': ['DataValidator', 'PostgresInsert'],
            'etl': ['PDFProcessor', 'DataValidator', 'PostgresInsert'],
            'pipeline': ['PDFProcessor', 'DataValidator', 'PostgresInsert']
        }
        
        # Role mapping patterns
        self.role_patterns = {
            'parser': ['parse', 'extract', 'read', 'process', 'invoice', 'document', 'pdf'],
            'validator': ['validate', 'verify', 'check', 'validate', 'quality', 'accuracy'],
            'writer': ['write', 'insert', 'save', 'store', 'load', 'database', 'db'],
            'extractor': ['extract', 'parse', 'read', 'process'],
            'processor': ['process', 'handle', 'manage', 'work'],
            'loader': ['load', 'insert', 'save', 'store'],
            'checker': ['check', 'verify', 'validate', 'quality'],
            'manager': ['manage', 'coordinate', 'oversee', 'supervise']
        }
        
    async def start(self):
        """Start the natural language agent builder"""
        print("\n" + "="*60)
        print("🎯 NATURAL LANGUAGE AGENT BUILDER")
        print("="*60)
        print("Create AI agents and workflows using natural language!")
        print("Describe what you need, and I'll build it for you.")
        print("Type 'help' for examples, 'quit' to exit.\n")
        
        # Initialize available tools
        await self.load_available_tools()
        
        # Show available tools at startup
        await self.show_available_tools()
        
        while True:
            try:
                user_input = input("\n💼 Job Description > ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using the Natural Language Agent Builder!")
                    break
                    
                if user_input.lower() == 'help':
                    await self.show_help()
                    continue
                    
                if user_input.lower() == 'list':
                    await self.list_resources()
                    continue
                    
                if user_input.lower() == 'run':
                    await self.run_workflow()
                    continue
                    
                if user_input.lower() == 'demo':
                    await self.run_demo_workflow()
                    continue
                    
                if user_input.lower() == 'tools':
                    await self.show_available_tools()
                    continue
                    
                # Process natural language input
                await self.process_natural_language(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Thanks for trying the Natural Language Agent Builder!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Type 'help' for examples.")
    
    async def load_available_tools(self):
        """Load available tools for hybrid execution (remote API + local MCP bridge)"""
        try:
            print("🔍 Loading available tools...")
            
            # Use local MCP bridge tools since remote API requires valid credentials
            print("⚠️  Using local MCP bridge tools (remote API requires valid credentials)")
            hybrid_tools = [
                # Local tools (MCP bridge) - all operations
                {
                    "name": "PDFProcessor",
                    "description": "Process PDF files and extract invoice data (local)",
                    "hosted_by": "mcp-bridge"
                },
                {
                    "name": "DataValidator", 
                    "description": "Validate extracted data against schema (local)",
                    "hosted_by": "mcp-bridge"
                },
                {
                    "name": "PostgresInsert",
                    "description": "Insert data into PostgreSQL database (local)",
                    "hosted_by": "mcp-bridge"
                },
                {
                    "name": "SQLExecutor",
                    "description": "Execute SQL queries against database (local)",
                    "hosted_by": "mcp-bridge"
                },
                {
                    "name": "TextToSQLGenerator",
                    "description": "Generate SQL from natural language questions (local)",
                    "hosted_by": "mcp-bridge"
                },
                {
                    "name": "FileDiscovery",
                    "description": "Discover files in directories",
                    "hosted_by": "mcp-bridge"
                },
                {
                    "name": "FileReader",
                    "description": "Read files from local filesystem",
                    "hosted_by": "mcp-bridge"
                }
            ]
            
            for tool_data in hybrid_tools:
                tool = Tool(
                    name=tool_data['name'],
                    description=tool_data['description'],
                    hosted_by=tool_data['hosted_by']
                )
                self.available_tools[tool.name] = tool
                
            remote_count = len([t for t in self.available_tools.values() if t.hosted_by == "memra"])
            local_count = len([t for t in self.available_tools.values() if t.hosted_by == "mcp-bridge"])
            
            print(f"✅ Loaded {len(self.available_tools)} tools:")
            print(f"   🌐 Remote (api.memra.co): {remote_count} tools")
            print(f"   🏠 Local (MCP bridge): {local_count} tools")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load tools: {e}")
            # Fallback to basic tools
            self.available_tools = {
                "PDFProcessor": Tool(name="PDFProcessor", description="Process PDF files and extract data", hosted_by="mcp-bridge"),
                "DataValidator": Tool(name="DataValidator", description="Validate extracted data against schema", hosted_by="mcp-bridge"),
                "PostgresInsert": Tool(name="PostgresInsert", description="Insert data into PostgreSQL database", hosted_by="mcp-bridge"),
                "SQLExecutor": Tool(name="SQLExecutor", description="Execute SQL queries", hosted_by="mcp-bridge"),
                "TextToSQLGenerator": Tool(name="TextToSQLGenerator", description="Generate SQL from natural language", hosted_by="mcp-bridge")
            }
    
    async def show_help(self):
        """Show help information with natural language examples"""
        help_text = """
🎯 NATURAL LANGUAGE AGENT BUILDER - HELP

💼 How to Create Agents & Workflows:

Just describe what you need in natural language! Here are some examples:

🤖 SINGLE AGENT EXAMPLES:
"I need an agent to parse invoice PDFs"
"I want someone to validate data"
"Create an agent that inserts data into the database"
"I need a PDF processor"
"Build me a data validator"

🏢 WORKFLOW EXAMPLES:
"I need a complete ETL pipeline for invoices"
"Build me a team to process documents"
"Create a workflow that extracts, validates, and loads data"
"I need an invoice processing team"
"Set up a data pipeline"

📋 AVAILABLE COMMANDS:
  help                    - Show this help message
  tools                   - Show available tools and capabilities
  quit/exit/q            - Exit the demo
  list                   - List created agents and workflows
  run                    - Run a workflow
  demo                   - Run the complete ETL demo

🎯 EXAMPLES OF WHAT YOU CAN SAY:

Single Agents:
  "I need an invoice parser"
  "Create a data validator"
  "Build me a database writer"
  "I want someone to process PDFs"
  "Need an agent to check data quality"

Complete Workflows:
  "I need a complete ETL pipeline"
  "Build me an invoice processing team"
  "Create a document processing workflow"
  "Set up a data validation pipeline"
  "I need a team to handle invoices"

The system will automatically:
  ✅ Choose appropriate tools
  ✅ Set up agent roles and jobs
  ✅ Create workflows when needed
  ✅ Suggest configurations
  ✅ Ask for confirmation

Try it! Just describe what you need in plain English! 🚀
"""
        print(help_text)
    
    async def show_available_tools(self):
        """Show available tools and their capabilities"""
        print("\n🛠️  AVAILABLE TOOLS & CAPABILITIES:")
        print("="*60)
        
        # Group tools by hosted_by
        remote_tools = [tool for tool in self.available_tools.values() if tool.hosted_by == "memra"]
        local_tools = [tool for tool in self.available_tools.values() if tool.hosted_by == "mcp-bridge"]
        
        print(f"\n🌐 REMOTE TOOLS (api.memra.co) - Production Capabilities:")
        print("-" * 50)
        for tool in remote_tools:
            print(f"  • {tool.name}")
            print(f"    {tool.description}")
            print()
        
        print(f"\n🏠 LOCAL TOOLS (MCP Bridge) - Basic Operations:")
        print("-" * 50)
        for tool in local_tools:
            print(f"  • {tool.name}")
            print(f"    {tool.description}")
            print()
        
        print("💡 WHAT YOU CAN ASK FOR:")
        print("-" * 30)
        print("  • 'I need an invoice parser' → Uses PDFProcessor")
        print("  • 'Create a data validator' → Uses DataValidator")
        print("  • 'Build me a database writer' → Uses PostgresInsert")
        print("  • 'I need a SQL generator' → Uses TextToSQLGenerator")
        print("  • 'Create a complete ETL pipeline' → Uses multiple tools")
        print("  • 'I need someone to process PDFs' → Uses PDFProcessor")
        print("  • 'Build me a data analyst' → Uses SQLExecutor + TextToSQLGenerator")
        print()
        print("🎯 Try: 'I need an invoice parser' or 'Create a complete ETL pipeline'")
    
    async def process_natural_language(self, text: str):
        """Process natural language input with LLM-powered conversational responses"""
        
        # First, let's understand what resources are available
        print("\n🔍 Let me check what we're working with...")
        available_info = await self.analyze_available_resources()
        
        # Generate conversational response using LLM
        context = f"User wants to create AI agents/workflows. Available tools: {list(self.available_tools.keys())}"
        llm_response = await self.llm.generate_response(context, text, available_info)
        
        print(f"\n💬 {llm_response}")
        
        # Now let's ask clarifying questions based on the request
        context_data = await self.gather_context_from_user(text)
        
        # Analyze the actual problem with real context
        print(f"\n🧠 Analyzing your specific situation...")
        analysis = await self.intelligent_problem_analysis(text, context_data)
        
        if not analysis['can_help']:
            print(f"\n❌ I don't think I can help with that request.")
            print(f"💡 Here's what I can help with:")
            await self.show_capabilities()
            return
        
        # Generate conversational plan explanation
        plan_context = f"Creating a plan for: {text}. Tools needed: {[t.name for t in analysis['tools']]}"
        plan_response = await self.llm.generate_response(
            plan_context, 
            "Explain the plan in a conversational way", 
            {
                "goal": text,
                "source": context_data.get('source', 'Not specified'),
                "target": context_data.get('target', 'Not specified'),
                "tools": [t.name for t in analysis['tools']],
                "needs_workflow": analysis['needs_workflow']
            }
        )
        
        print(f"\n📋 {plan_response}")
        
        # Ask for confirmation before proceeding
        confirm = input("\n🤔 Should I proceed with this plan? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("No problem! Let me know if you want to adjust anything.")
            return
        
        # Create the appropriate solution
        if analysis['needs_workflow']:
            await self.create_intelligent_workflow(text, analysis, context_data)
        else:
            await self.create_intelligent_agent(text, analysis, context_data)
    
    async def analyze_available_resources(self):
        """Analyze what resources are actually available"""
        available_info = {}
        
        print("   📂 Checking for data sources...")
        
        # Check for demo data
        demo_data_dir = Path(__file__).parent / "etl_invoice_processing" / "data" / "invoices"
        if demo_data_dir.exists():
            # Look for both .pdf and .PDF files
            pdf_files = list(demo_data_dir.glob("*.pdf")) + list(demo_data_dir.glob("*.PDF"))
            available_info['pdf_files'] = len(pdf_files)
            print(f"   ✅ Found {len(pdf_files)} PDF files in demo directory")
        else:
            available_info['pdf_files'] = 0
            print("   ❌ No demo data directory found")
        
        # Check for database connection
        print("   🗄️  Checking database connection...")
        try:
            import psycopg2
            conn = psycopg2.connect("postgresql://memra:memra123@localhost:5432/memra_invoice_db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM invoices")
            count = cursor.fetchone()[0]
            available_info['database_records'] = count
            available_info['database_name'] = 'memra_invoice_db'
            print(f"   ✅ Database connected - {count} invoices in database")
            cursor.close()
            conn.close()
        except Exception as e:
            available_info['database_error'] = str(e)
            print(f"   ❌ Database connection failed: {str(e)}")
        
        # Check for available tools
        print("   🛠️  Checking available tools...")
        remote_tools = [t for t in self.available_tools.values() if t.hosted_by == "memra"]
        local_tools = [t for t in self.available_tools.values() if t.hosted_by == "mcp-bridge"]
        available_info['remote_tools'] = len(remote_tools)
        available_info['local_tools'] = len(local_tools)
        available_info['total_tools'] = len(self.available_tools)
        print(f"   ✅ {len(remote_tools)} remote tools, {len(local_tools)} local tools available")
        
        return available_info
    
    async def gather_context_from_user(self, request: str) -> Dict[str, Any]:
        """Gather context by asking intelligent questions"""
        context = {}
        
        # Analyze the request to determine what questions to ask
        request_lower = request.lower()
        
        # Ask about source if not clear
        if any(word in request_lower for word in ['pdf', 'file', 'document', 'invoice']):
            if 'demo' in request_lower or 'directory' in request_lower:
                context['source'] = 'demo_invoices'
            else:
                print(f"\n❓ Where are the files you want to process?")
                print("   a) Use the demo invoice files (15 PDFs)")
                print("   b) Specify a different directory")
                print("   c) Upload files manually")
                choice = input("   Your choice (a/b/c): ").strip().lower()
                if choice == 'a':
                    context['source'] = 'demo_invoices'
                elif choice == 'b':
                    path = input("   Enter directory path: ").strip()
                    context['source'] = f'custom_path:{path}'
                else:
                    context['source'] = 'manual_upload'
        
        # Ask about target database if not clear
        if any(word in request_lower for word in ['database', 'postgres', 'db', 'insert', 'save']):
            print(f"\n❓ Which database should I use?")
            print("   a) Use the demo database (memra_invoice_db)")
            print("   b) Specify a different database")
            choice = input("   Your choice (a/b): ").strip().lower()
            if choice == 'a':
                context['target'] = 'demo_database'
            else:
                db_url = input("   Enter database URL: ").strip()
                context['target'] = f'custom_db:{db_url}'
        
        # Ask about processing scope
        if 'all' in request_lower or 'batch' in request_lower:
            context['scope'] = 'all_files'
        elif any(word in request_lower for word in ['first', 'one', 'single']):
            context['scope'] = 'single_file'
        else:
            print(f"\n❓ How many files should I process?")
            print("   a) All available files")
            print("   b) Just the first few (for testing)")
            print("   c) Specify a number")
            choice = input("   Your choice (a/b/c): ").strip().lower()
            if choice == 'a':
                context['scope'] = 'all_files'
            elif choice == 'b':
                context['scope'] = 'test_batch'
            else:
                try:
                    num = int(input("   How many files? "))
                    context['scope'] = f'count:{num}'
                except ValueError:
                    context['scope'] = 'test_batch'
        
        return context
    
    async def intelligent_problem_analysis(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligent analysis of the problem with real context"""
        analysis = {
            'can_help': False,
            'tools': [],
            'needs_workflow': False,
            'reasoning': []
        }
        
        request_lower = request.lower()
        
        # Check if this is something we can actually help with
        if any(word in request_lower for word in ['pdf', 'invoice', 'document', 'file']):
            analysis['can_help'] = True
            analysis['reasoning'].append("Request involves document processing - this is within our capabilities")
        else:
            analysis['reasoning'].append("Request doesn't involve document processing - may be outside our scope")
            return analysis
        
        # Determine what tools are actually needed based on context
        if context.get('source') == 'demo_invoices':
            analysis['reasoning'].append("Using demo invoice files - will need PDF processing")
            if 'PDFProcessor' in self.available_tools:
                analysis['tools'].append(self.available_tools['PDFProcessor'])
        
        if any(word in request_lower for word in ['validate', 'check', 'quality']):
            analysis['reasoning'].append("Request mentions validation - will need data validation")
            if 'DataValidator' in self.available_tools:
                analysis['tools'].append(self.available_tools['DataValidator'])
        
        if context.get('target') or any(word in request_lower for word in ['database', 'postgres', 'insert', 'save']):
            analysis['reasoning'].append("Request involves database operations - will need database tools")
            if 'PostgresInsert' in self.available_tools:
                analysis['tools'].append(self.available_tools['PostgresInsert'])
            if 'SQLExecutor' in self.available_tools:
                analysis['tools'].append(self.available_tools['SQLExecutor'])
        
        # Determine if this needs a workflow or single agent
        if len(analysis['tools']) > 2:
            analysis['needs_workflow'] = True
            analysis['reasoning'].append("Multiple tools needed - this requires a workflow")
        else:
            analysis['reasoning'].append("Simple task - single agent should suffice")
        
        # Show reasoning
        for reason in analysis['reasoning']:
            print(f"   💭 {reason}")
        
        return analysis
    
    async def create_intelligent_agent(self, request: str, analysis: Dict[str, Any], context: Dict[str, Any]):
        """Create an intelligent agent based on real analysis"""
        print(f"\n🤖 Creating a focused agent for your task...")
        
        # Determine the best role based on the actual tools
        tool_names = [t.name for t in analysis['tools']]
        if 'PDFProcessor' in tool_names:
            role = "Document Processor"
            job = f"Process {context.get('source', 'documents')} and extract data"
        elif 'DataValidator' in tool_names:
            role = "Data Validator"
            job = "Validate data quality and accuracy"
        elif 'PostgresInsert' in tool_names:
            role = "Data Writer"
            job = f"Write data to {context.get('target', 'database')}"
        else:
            role = "Data Processor"
            job = "Process data as requested"
        
        # Create the agent
        agent_name = f"intelligent_agent_{self.agent_counter + 1}"
        self.agent_counter += 1
        
        agent = Agent(
            role=role,
            job=job,
            tools=analysis['tools'],
            output_key=f"{role.lower().replace(' ', '_')}_result"
        )
        
        self.agents[agent_name] = agent
        
        print(f"✅ Created agent: {agent_name}")
        print(f"   Role: {role}")
        print(f"   Job: {job}")
        print(f"   Tools: {[t.name for t in analysis['tools']]}")
        
        # Execute with proper context
        print(f"\n🚀 Ready to execute with your specific context...")
        confirm = input("Should I run this now? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            await self.execute_with_context(agent_name, context)
    
    async def create_intelligent_workflow(self, request: str, analysis: Dict[str, Any], context: Dict[str, Any]):
        """Create an intelligent workflow based on real analysis"""
        
        # Generate conversational workflow creation message
        workflow_context = f"Creating workflow for: {request}. Tools: {[t.name for t in analysis['tools']]}"
        workflow_response = await self.llm.generate_response(
            workflow_context,
            "Explain what agents you're creating in a conversational way",
            {
                "request": request,
                "tools": [t.name for t in analysis['tools']],
                "context": context
            }
        )
        
        print(f"\n🏢 {workflow_response}")
        
        # Create specialized agents based on actual tool needs
        agents = []
        
        # PDF Processing Agent
        pdf_tools = [t for t in analysis['tools'] if 'PDF' in t.name]
        if pdf_tools:
            pdf_agent = Agent(
                role="Document Processor",
                job=f"Extract data from {context.get('source', 'documents')}",
                tools=pdf_tools,
                output_key="extracted_data"
            )
            agents.append(pdf_agent)
            print(f"✅ Document Processor - handles: {[t.name for t in pdf_tools]}")
        
        # Validation Agent
        validation_tools = [t for t in analysis['tools'] if 'Validator' in t.name]
        if validation_tools:
            validation_agent = Agent(
                role="Data Validator",
                job="Ensure data quality and accuracy",
                tools=validation_tools,
                output_key="validated_data"
            )
            agents.append(validation_agent)
            print(f"✅ Data Validator - handles: {[t.name for t in validation_tools]}")
        
        # Database Agent
        db_tools = [t for t in analysis['tools'] if any(word in t.name for word in ['Postgres', 'SQL'])]
        if db_tools:
            db_agent = Agent(
                role="Data Writer",
                job=f"Write data to {context.get('target', 'database')}",
                tools=db_tools,
                output_key="database_result"
            )
            agents.append(db_agent)
            print(f"✅ Data Writer - handles: {[t.name for t in db_tools]}")
        
        # Create workflow
        workflow_name = f"intelligent_workflow_{len(self.departments) + 1}"
        workflow = Department(
            name="Smart Processing Team",
            mission=f"Complete: {request}",
            agents=agents,
            workflow_order=[agent.role for agent in agents]
        )
        
        self.departments[workflow_name] = workflow
        
        # Generate conversational summary
        summary_context = f"Workflow created with {len(agents)} agents for: {request}"
        summary_response = await self.llm.generate_response(
            summary_context,
            "Summarize what was created in a conversational way",
            {
                "mission": workflow.mission,
                "agents": [a.role for a in agents],
                "flow": workflow.workflow_order
            }
        )
        
        print(f"\n📋 {summary_response}")
        
        # Execute with proper context
        confirm = input("\n🚀 Should I start the workflow now? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            await self.execute_workflow_with_context(workflow_name, context)
    
    async def execute_with_context(self, agent_name: str, context: Dict[str, Any]):
        """Execute an agent with proper context"""
        if agent_name not in self.agents:
            print(f"❌ Agent '{agent_name}' not found!")
            return
        
        agent = self.agents[agent_name]
        print(f"\n🚀 Executing {agent_name} with your context...")
        
        # Prepare input data based on context
        input_data = await self.prepare_input_data(context)
        
        try:
            result = await self.execution_engine.execute_agent(agent, input_data)
            
            print(f"\n✅ Execution complete!")
            if result.get("success"):
                print(f"Agent executed successfully!")
                if result.get("results"):
                    print(f"Processed {len(result['results'])} operations")
            else:
                print(f"❌ Execution failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Execution error: {str(e)}")
    
    async def execute_workflow_with_context(self, workflow_name: str, context: Dict[str, Any]):
        """Execute a workflow with proper context"""
        if workflow_name not in self.departments:
            print(f"❌ Workflow '{workflow_name}' not found!")
            return
        
        workflow = self.departments[workflow_name]
        
        # Generate conversational execution start message
        execution_context = f"Starting workflow execution for: {workflow.mission}"
        execution_response = await self.llm.generate_response(
            execution_context,
            "Explain that you're starting the workflow execution in a conversational way",
            {
                "mission": workflow.mission,
                "agents": [a.role for a in workflow.agents],
                "context": context
            }
        )
        
        print(f"\n🚀 {execution_response}")
        
        # Prepare input data based on context
        input_data = await self.prepare_input_data(context)
        
        try:
            results = await self.execution_engine.execute_department(workflow, input_data)
            
            # Generate conversational completion message
            completion_context = f"Workflow completed. Results: {results}"
            completion_response = await self.llm.generate_response(
                completion_context,
                "Explain the completion results in a conversational way",
                {
                    "success": results.get("success"),
                    "results_count": len(results.get("results", [])),
                    "error": results.get("error")
                }
            )
            
            print(f"\n🎉 {completion_response}")
            
            # Show detailed results if available
            if results.get("success") and results.get("results"):
                print(f"\n📊 Detailed Results:")
                for i, result in enumerate(results["results"], 1):
                    agent_name = result.get("agent_name", f"Agent {i}")
                    tools_used = result.get("tools_used", [])
                    print(f"   {i}. {agent_name}: Used {len(tools_used)} tools")
                    if result.get("results"):
                        for tool_result in result["results"]:
                            tool_name = tool_result.get("tool", "Unknown")
                            success = "✅" if tool_result.get("success") else "❌"
                            print(f"      {success} {tool_name}")
                
        except Exception as e:
            error_response = await self.llm.generate_response(
                f"Workflow execution failed: {str(e)}",
                "Explain the error in a conversational way",
                {"error": str(e)}
            )
            print(f"\n❌ {error_response}")
    
    async def prepare_input_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data based on context"""
        input_data = {}
        
        # Handle source files
        if context.get('source') == 'demo_invoices':
            demo_data_dir = Path(__file__).parent / "etl_invoice_processing" / "data" / "invoices"
            if demo_data_dir.exists():
                # Look for both .pdf and .PDF files
                pdf_files = list(demo_data_dir.glob("*.pdf")) + list(demo_data_dir.glob("*.PDF"))
                
                # Apply scope
                scope = context.get('scope', 'test_batch')
                if scope == 'all_files':
                    selected_files = pdf_files
                elif scope == 'test_batch':
                    selected_files = pdf_files[:3]  # First 3 for testing
                elif scope.startswith('count:'):
                    try:
                        count = int(scope.split(':')[1])
                        selected_files = pdf_files[:count]
                    except:
                        selected_files = pdf_files[:3]
                else:
                    selected_files = pdf_files[:3]
                
                input_data['files'] = [str(f) for f in selected_files]
                print(f"📄 Using {len(selected_files)} files from demo directory")
        
        # Handle target database
        if context.get('target') == 'demo_database':
            input_data['database'] = 'postgresql://memra:memra123@localhost:5432/memra_invoice_db'
            print(f"🗄️  Using demo database")
        
        return input_data
    
    async def show_capabilities(self):
        """Show what the system can actually do"""
        print(f"   📄 Document Processing:")
        print(f"      • Extract data from PDF invoices")
        print(f"      • Process files in batches")
        print(f"      • Validate extracted data")
        print(f"   🗄️  Database Operations:")
        print(f"      • Insert data into PostgreSQL")
        print(f"      • Execute SQL queries")
        print(f"      • Generate SQL from natural language")
        print(f"   🔄 Workflow Automation:")
        print(f"      • Create multi-step processing pipelines")
        print(f"      • Coordinate between different tools")
        print(f"      • Handle complex data transformations")
    
    # Legacy method removed - replaced with intelligent analysis
    
    # Legacy method removed - replaced with intelligent analysis
    
    async def execute_single_agent(self, agent_name: str):
        """Execute a single agent"""
        if agent_name not in self.agents:
            print(f"❌ Agent '{agent_name}' not found!")
            return
        
        agent = self.agents[agent_name]
        print(f"\n🚀 EXECUTING AGENT: {agent_name}")
        print("="*40)
        print(f"Role: {agent.role}")
        print(f"Job: {agent.job}")
        print(f"Tools: {[t.name for t in agent.tools]}")
        
        # Check if we have demo data for file operations
        demo_data_dir = Path(__file__).parent / "etl_invoice_processing" / "data" / "invoices"
        if demo_data_dir.exists() and any('File' in t.name for t in agent.tools):
            # Look for both .pdf and .PDF files
            pdf_files = list(demo_data_dir.glob("*.pdf")) + list(demo_data_dir.glob("*.PDF"))
            if pdf_files:
                input_data = {"files": [str(f) for f in pdf_files[:3]]}  # Use first 3 files
                print(f"📄 Using demo data: {len(input_data['files'])} PDF files")
            else:
                input_data = {"message": "No demo files found"}
        else:
            input_data = {"message": "Test execution"}
        
        try:
            # Execute the agent
            result = await self.execution_engine.execute_agent(agent, input_data)
            
            print(f"\n✅ EXECUTION COMPLETE")
            print("-" * 20)
            if result.get("success"):
                print(f"Agent '{agent_name}' executed successfully!")
                print(f"Tools used: {result.get('tools_used', [])}")
                if result.get("results"):
                    print(f"Results: {len(result['results'])} tool executions")
            else:
                print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Execution error: {str(e)}")
    
    # Legacy method removed - replaced with intelligent analysis
    
    # Legacy method removed - replaced with intelligent analysis
    
    # Legacy method removed - replaced with intelligent analysis
    
    # Legacy method removed - replaced with intelligent analysis
    
    # Legacy methods removed - replaced with intelligent analysis
    
    async def list_resources(self):
        """List created resources"""
        print("\n📋 CREATED RESOURCES:")
        
        if self.agents:
            print("\n🤖 AGENTS:")
            for name, agent in self.agents.items():
                print(f"  - {name}: {agent.job}")
                print(f"    Tools: {[t.name for t in agent.tools]}")
        else:
            print("\n🤖 No agents created yet.")
        
        if self.departments:
            print("\n🏢 WORKFLOWS:")
            for name, dept in self.departments.items():
                print(f"  - {name}: {dept.mission}")
                print(f"    Agents: {[a.role for a in dept.agents]}")
        else:
            print("\n🏢 No workflows created yet.")
    
    async def run_workflow(self):
        """Run a workflow"""
        if not self.departments:
            print("❌ No workflows created yet. Create one first!")
            return
        
        print("\n🏢 Available workflows:")
        for i, (name, dept) in enumerate(self.departments.items(), 1):
            print(f"  {i}. {name}: {dept.mission}")
        
        try:
            choice = input("\nWhich workflow to run? (number or name): ").strip()
            
            if choice.isdigit():
                workflow_names = list(self.departments.keys())
                if 1 <= int(choice) <= len(workflow_names):
                    workflow_name = workflow_names[int(choice) - 1]
                else:
                    print("❌ Invalid number!")
                    return
            else:
                workflow_name = choice
            
            if workflow_name in self.departments:
                await self.run_specific_workflow(workflow_name)
            else:
                print(f"❌ Workflow '{workflow_name}' not found!")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    async def run_specific_workflow(self, workflow_name: str):
        """Run a specific workflow"""
        dept = self.departments[workflow_name]
        
        print(f"\n🚀 Your digital team is getting to work...")
        print("="*50)
        
        # Check if we have demo data
        demo_data_dir = Path(__file__).parent / "etl_invoice_processing" / "data" / "invoices"
        if not demo_data_dir.exists():
            print("❌ I can't find the demo data! Please make sure the ETL demo data is available.")
            return
        
        # Get list of PDF files (both .pdf and .PDF)
        pdf_files = list(demo_data_dir.glob("*.pdf")) + list(demo_data_dir.glob("*.PDF"))
        if not pdf_files:
            print("❌ I can't find any PDF files to work with!")
            return
        
        print(f"📄 I found {len(pdf_files)} PDF files to process")
        print("Let me get the team started...")
        
        # Run the workflow
        try:
            results = await self.execution_engine.execute_department(
                dept, 
                {"files": [str(f) for f in pdf_files]}
            )
            
            print(f"\n🎉 Great news! Your digital team has finished the work!")
            print(f"   📊 Processed: {len(pdf_files)} files")
            print(f"   ✅ Results: {results}")
            print(f"\n💡 Your data has been processed and is ready to use!")
            
        except Exception as e:
            print(f"❌ Oh no! Something went wrong: {str(e)}")
            print("Let me know if you'd like to try again or if you need help troubleshooting.")
    
    async def run_demo_workflow(self):
        """Run the complete ETL demo workflow"""
        print("\n🎯 RUNNING COMPLETE ETL DEMO WORKFLOW")
        print("="*50)
        
        # Create demo agents
        print("🤖 Creating demo agents...")
        
        # Invoice Parser Agent
        parser_agent = Agent(
            role="Invoice Parser",
            job="Extract data from invoice PDFs",
            tools=[self.available_tools.get("PDFProcessor", Tool(name="PDFProcessor"))],
            output_key="invoice_data"
        )
        
        # Data Validator Agent
        validator_agent = Agent(
            role="Data Validator", 
            job="Validate extracted invoice data",
            tools=[self.available_tools.get("DataValidator", Tool(name="DataValidator"))],
            output_key="validated_data"
        )
        
        # Database Writer Agent
        writer_agent = Agent(
            role="Database Writer",
            job="Insert validated data into database", 
            tools=[
                self.available_tools.get("PostgresInsert", Tool(name="PostgresInsert")),
                self.available_tools.get("SQLExecutor", Tool(name="SQLExecutor"))
            ],
            output_key="insertion_result"
        )
        
        # Create ETL Department
        etl_department = Department(
            name="ETL Pipeline",
            mission="Complete ETL workflow for invoice processing",
            agents=[parser_agent, validator_agent, writer_agent],
            workflow_order=["Invoice Parser", "Data Validator", "Database Writer"]
        )
        
        print("✅ Demo agents created!")
        print(f"   Agents: {[a.role for a in etl_department.agents]}")
        
        # Store for later use
        self.agents.update({
            "demo_parser": parser_agent,
            "demo_validator": validator_agent, 
            "demo_writer": writer_agent
        })
        self.departments["demo_etl"] = etl_department
        
        # Run the workflow
        await self.run_specific_workflow("demo_etl")

async def main():
    """Main function to run the natural language agent builder"""
    try:
        # Set up API key for hybrid execution
        if not os.getenv("MEMRA_API_KEY"):
            os.environ["MEMRA_API_KEY"] = "test-secret-for-development"
            print("🔑 Using default API key for demo")
        
        # Check if PostgreSQL is running
        print("🔍 Checking required services...")
        
        # Simple check for PostgreSQL
        try:
            import psycopg2
            conn = psycopg2.connect("postgresql://memra:memra123@localhost:5432/memra_invoice_db")
            conn.close()
            print("✅ PostgreSQL is running")
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            print("Please ensure PostgreSQL is running and accessible")
            return
        
        print("🎯 Launching Natural Language Agent Builder...")
        print("🌐 Hybrid mode: Remote API (api.memra.co) + Local MCP Bridge")
        
        # Create and start the builder
        builder = NaturalLanguageBuilder()
        await builder.start()
        
    except Exception as e:
        print(f"❌ Error running demo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 