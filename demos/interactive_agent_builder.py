#!/usr/bin/env python3
"""
Interactive Agent Builder Demo

This demo allows users to interactively construct ETL workflow agents
through a text-based interface, building on the existing ETL workflow
but making it interactive and educational.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the parent directory to the path to import memra modules
sys.path.append(str(Path(__file__).parent.parent))

from memra.discovery import discover_tools
from memra.execution import ExecutionEngine
from memra.models import Agent, Department, Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveAgentBuilder:
    """Interactive interface for building ETL workflow agents"""
    
    def __init__(self):
        self.execution_engine = ExecutionEngine()
        self.agents = {}
        self.departments = {}
        self.available_tools = {}
        self.current_workflow = None
        
    async def start(self):
        """Start the interactive agent builder"""
        print("\n" + "="*60)
        print("🤖 INTERACTIVE AGENT BUILDER DEMO")
        print("="*60)
        print("Build your own ETL workflow agents through conversation!")
        print("Type 'help' for available commands, 'quit' to exit.\n")
        
        # Initialize available tools
        await self.load_available_tools()
        
        while True:
            try:
                user_input = input("\n🔧 Agent Builder > ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using the Interactive Agent Builder!")
                    break
                    
                await self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Thanks for trying the Interactive Agent Builder!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Type 'help' for available commands.")
    
    async def load_available_tools(self):
        """Load available tools from the discovery client"""
        try:
            print("🔍 Loading available tools...")
            tools = discover_tools()
            
            for tool_data in tools:
                tool = Tool(
                    name=tool_data.get('name', 'Unknown'),
                    description=tool_data.get('description', 'No description'),
                    hosted_by=tool_data.get('hosted_by', 'memra')
                )
                self.available_tools[tool.name] = tool
                
            print(f"✅ Loaded {len(self.available_tools)} available tools")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load tools from discovery client: {e}")
            # Fallback to basic tools
            self.available_tools = {
                "PDFProcessor": Tool(name="PDFProcessor", description="Process PDF files and extract data"),
                "DataValidator": Tool(name="DataValidator", description="Validate extracted data against schema"),
                "PostgresInsert": Tool(name="PostgresInsert", description="Insert data into PostgreSQL database"),
                "SQLExecutor": Tool(name="SQLExecutor", description="Execute SQL queries"),
                "TextToSQLGenerator": Tool(name="TextToSQLGenerator", description="Generate SQL from natural language")
            }
    
    async def process_command(self, command: str):
        """Process user commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == 'help':
            await self.show_help()
        elif cmd == 'list':
            await self.list_resources(parts[1:] if len(parts) > 1 else [])
        elif cmd == 'create':
            await self.create_resource(parts[1:])
        elif cmd == 'configure':
            await self.configure_resource(parts[1:])
        elif cmd == 'run':
            await self.run_workflow(parts[1:])
        elif cmd == 'show':
            await self.show_resource(parts[1:])
        elif cmd == 'demo':
            await self.run_demo_workflow()
        elif cmd == 'clear':
            await self.clear_resources()
        else:
            print(f"❓ Unknown command: {cmd}")
            print("Type 'help' for available commands.")
    
    async def show_help(self):
        """Show help information"""
        help_text = """
📚 INTERACTIVE AGENT BUILDER COMMANDS:

🔧 Basic Commands:
  help                    - Show this help message
  quit/exit/q            - Exit the demo
  clear                  - Clear all created agents and departments

📋 Resource Management:
  list [agents|tools|departments]  - List created resources
  show <name>                      - Show details of a specific resource
  create agent <name>              - Create a new agent
  create department <name>         - Create a new department

⚙️ Configuration:
  configure agent <name>           - Configure an agent's role and tools
  configure department <name>      - Configure a department's agents

🚀 Execution:
  run workflow <name>              - Run a specific workflow
  demo                             - Run the complete ETL demo workflow

💡 Example Workflow:
  1. create agent parser
  2. configure agent parser
  3. create agent validator  
  4. configure agent validator
  5. create department etl
  6. configure department etl
  7. run workflow etl

🎯 Available Tools:
  - PDFProcessor: Extract data from PDF files
  - DataValidator: Validate extracted data
  - PostgresInsert: Insert data into database
  - SQLExecutor: Execute SQL queries
  - TextToSQLGenerator: Generate SQL from questions
"""
        print(help_text)
    
    async def list_resources(self, resource_type: List[str]):
        """List created resources"""
        if not resource_type:
            print("\n📋 ALL RESOURCES:")
            print(f"  Agents: {list(self.agents.keys())}")
            print(f"  Departments: {list(self.departments.keys())}")
            print(f"  Available Tools: {list(self.available_tools.keys())}")
        elif resource_type[0] == 'agents':
            if self.agents:
                print("\n🤖 CREATED AGENTS:")
                for name, agent in self.agents.items():
                    print(f"  {name}: {agent.job} (Tools: {[t.name for t in agent.tools]})")
            else:
                print("\n🤖 No agents created yet. Use 'create agent <name>' to create one.")
        elif resource_type[0] == 'tools':
            print("\n🔧 AVAILABLE TOOLS:")
            for name, tool in self.available_tools.items():
                print(f"  {name}: {tool.description}")
        elif resource_type[0] == 'departments':
            if self.departments:
                print("\n🏢 CREATED DEPARTMENTS:")
                for name, dept in self.departments.items():
                    print(f"  {name}: {len(dept.agents)} agents")
            else:
                print("\n🏢 No departments created yet. Use 'create department <name>' to create one.")
        else:
            print(f"❓ Unknown resource type: {resource_type[0]}")
    
    async def create_resource(self, args: List[str]):
        """Create a new resource (agent or department)"""
        if len(args) < 2:
            print("❌ Usage: create <agent|department> <name>")
            return
        
        resource_type = args[0].lower()
        name = args[1]
        
        if resource_type == 'agent':
            if name in self.agents:
                print(f"❌ Agent '{name}' already exists!")
                return
            
            self.agents[name] = Agent(
                role=name,
                job="Unconfigured Agent",
                tools=[],
                output_key="result"
            )
            print(f"✅ Created agent '{name}'. Use 'configure agent {name}' to set it up.")
            
        elif resource_type == 'department':
            if name in self.departments:
                print(f"❌ Department '{name}' already exists!")
                return
            
            self.departments[name] = Department(
                name=name,
                mission="Department created through interactive builder",
                agents=[]
            )
            print(f"✅ Created department '{name}'. Use 'configure department {name}' to set it up.")
            
        else:
            print(f"❌ Unknown resource type: {resource_type}")
    
    async def configure_resource(self, args: List[str]):
        """Configure a resource (agent or department)"""
        if len(args) < 2:
            print("❌ Usage: configure <agent|department> <name>")
            return
        
        resource_type = args[0].lower()
        name = args[1]
        
        if resource_type == 'agent':
            await self.configure_agent(name)
        elif resource_type == 'department':
            await self.configure_department(name)
        else:
            print(f"❌ Unknown resource type: {resource_type}")
    
    async def configure_agent(self, name: str):
        """Configure an agent interactively"""
        if name not in self.agents:
            print(f"❌ Agent '{name}' not found! Create it first with 'create agent {name}'")
            return
        
        agent = self.agents[name]
        print(f"\n⚙️  CONFIGURING AGENT: {name}")
        print("="*40)
        
        # Configure job
        print("\n🎭 What should this agent do? (e.g., 'Invoice Parser', 'Data Validator')")
        job = input("Job: ").strip()
        if job:
            agent.job = job
        
        # Configure tools
        print(f"\n🔧 Available tools: {list(self.available_tools.keys())}")
        print("Which tools should this agent have? (comma-separated, or 'all' for all tools)")
        tools_input = input("Tools: ").strip()
        
        if tools_input.lower() == 'all':
            agent.tools = list(self.available_tools.values())
        elif tools_input:
            tool_names = [t.strip() for t in tools_input.split(',')]
            selected_tools = []
            for tool_name in tool_names:
                if tool_name in self.available_tools:
                    selected_tools.append(self.available_tools[tool_name])
                else:
                    print(f"⚠️  Warning: Tool '{tool_name}' not found, skipping...")
            agent.tools = selected_tools
        
        print(f"✅ Agent '{name}' configured!")
        print(f"   Job: {agent.job}")
        print(f"   Tools: {[t.name for t in agent.tools]}")
    
    async def configure_department(self, name: str):
        """Configure a department interactively"""
        if name not in self.departments:
            print(f"❌ Department '{name}' not found! Create it first with 'create department {name}'")
            return
        
        if not self.agents:
            print("❌ No agents available! Create some agents first.")
            return
        
        dept = self.departments[name]
        print(f"\n🏢 CONFIGURING DEPARTMENT: {name}")
        print("="*40)
        
        print(f"\n🤖 Available agents: {list(self.agents.keys())}")
        print("Which agents should be in this department? (comma-separated)")
        agents_input = input("Agents: ").strip()
        
        if agents_input:
            agent_names = [a.strip() for a in agents_input.split(',')]
            selected_agents = []
            for agent_name in agent_names:
                if agent_name in self.agents:
                    selected_agents.append(self.agents[agent_name])
                else:
                    print(f"⚠️  Warning: Agent '{agent_name}' not found, skipping...")
            dept.agents = selected_agents
            dept.workflow_order = [agent.role for agent in selected_agents]
        
        print(f"✅ Department '{name}' configured!")
        print(f"   Agents: {[a.role for a in dept.agents]}")
    
    async def show_resource(self, args: List[str]):
        """Show details of a specific resource"""
        if len(args) < 1:
            print("❌ Usage: show <name>")
            return
        
        name = args[0]
        
        if name in self.agents:
            agent = self.agents[name]
            print(f"\n🤖 AGENT: {name}")
            print("="*30)
            print(f"Job: {agent.job}")
            print(f"Tools: {[t.name for t in agent.tools]}")
            print(f"Output Key: {agent.output_key}")
            
        elif name in self.departments:
            dept = self.departments[name]
            print(f"\n🏢 DEPARTMENT: {name}")
            print("="*30)
            print(f"Agents: {[a.role for a in dept.agents]}")
            print(f"Mission: {dept.mission}")
            
        else:
            print(f"❌ Resource '{name}' not found!")
    
    async def run_workflow(self, args: List[str]):
        """Run a specific workflow"""
        if len(args) < 2 or args[0] != 'workflow':
            print("❌ Usage: run workflow <name>")
            return
        
        workflow_name = args[1]
        
        if workflow_name not in self.departments:
            print(f"❌ Workflow '{workflow_name}' not found! Create it first.")
            return
        
        dept = self.departments[workflow_name]
        if not dept.agents:
            print(f"❌ Workflow '{workflow_name}' has no agents! Configure it first.")
            return
        
        print(f"\n🚀 RUNNING WORKFLOW: {workflow_name}")
        print("="*40)
        
        # Check if we have demo data
        demo_data_dir = Path(__file__).parent / "etl_invoice_processing" / "data" / "invoices"
        if not demo_data_dir.exists():
            print("❌ Demo data not found! Please ensure the ETL demo data is available.")
            return
        
        # Get list of PDF files
        pdf_files = list(demo_data_dir.glob("*.pdf"))
        if not pdf_files:
            print("❌ No PDF files found in demo data!")
            return
        
        print(f"📄 Found {len(pdf_files)} PDF files to process")
        
        # Run the workflow
        try:
            results = self.execution_engine.execute_department(
                dept, 
                {"files": [str(f) for f in pdf_files]}
            )
            
            print(f"\n✅ Workflow completed!")
            print(f"   Processed: {len(pdf_files)} files")
            print(f"   Results: {results}")
            
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
    
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
            "parser": parser_agent,
            "validator": validator_agent, 
            "writer": writer_agent
        })
        self.departments["etl"] = etl_department
        
        # Run the workflow
        await self.run_workflow(["workflow", "etl"])
    
    async def clear_resources(self):
        """Clear all created resources"""
        self.agents.clear()
        self.departments.clear()
        print("🧹 All agents and departments cleared!")

async def main():
    """Main entry point"""
    builder = InteractiveAgentBuilder()
    await builder.start()

if __name__ == "__main__":
    asyncio.run(main()) 