#!/usr/bin/env python3
"""
Test script for Interactive Agent Builder Demo

This script demonstrates the interactive agent builder functionality
by running through a complete workflow creation process.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to import memra modules
sys.path.append(str(Path(__file__).parent.parent))

from interactive_agent_builder import InteractiveAgentBuilder

async def test_interactive_builder():
    """Test the interactive agent builder with automated commands"""
    
    print("🧪 TESTING INTERACTIVE AGENT BUILDER")
    print("="*50)
    
    # Create builder instance
    builder = InteractiveAgentBuilder()
    
    # Load tools
    await builder.load_available_tools()
    
    print("\n📋 Available tools loaded:")
    for name, tool in builder.available_tools.items():
        print(f"  - {name}: {tool.description}")
    
    # Test creating agents
    print("\n🤖 Creating test agents...")
    
    from memra.models import Agent as MemraAgent
    
    # Create parser agent
    builder.agents["parser"] = MemraAgent(
        role='Invoice Parser',
        job='Extract data from invoice PDFs',
        tools=[builder.available_tools.get("PDFProcessor")],
        output_key='invoice_data'
    )
    
    # Create validator agent
    builder.agents["validator"] = MemraAgent(
        role='Data Validator',
        job='Validate extracted invoice data',
        tools=[builder.available_tools.get("DataValidator")],
        output_key='validated_data'
    )
    
    # Create writer agent
    builder.agents["writer"] = MemraAgent(
        role='Database Writer',
        job='Insert validated data into database',
        tools=[
            builder.available_tools.get("PostgresInsert"),
            builder.available_tools.get("SQLExecutor")
        ],
        output_key='insertion_result'
    )
    
    print("✅ Test agents created:")
    for name, agent in builder.agents.items():
        print(f"  - {name}: {agent.job}")
    
    # Test creating department
    print("\n🏢 Creating test department...")
    
    from memra.models import Department
    
    builder.departments["etl"] = Department(
        name="ETL Pipeline",
        mission="Complete ETL workflow for invoice processing",
        agents=list(builder.agents.values()),
        workflow_order=[agent.role for agent in builder.agents.values()]
    )
    
    print("✅ Test department created:")
    print(f"  - Name: {builder.departments['etl'].name}")
    print(f"  - Mission: {builder.departments['etl'].mission}")
    print(f"  - Agents: {[a.role for a in builder.departments['etl'].agents]}")
    print(f"  - Workflow: {' → '.join(builder.departments['etl'].workflow_order)}")
    
    # Test listing resources
    print("\n📋 Testing resource listing...")
    await builder.list_resources([])
    await builder.list_resources(['agents'])
    await builder.list_resources(['departments'])
    
    # Test showing resources
    print("\n🔍 Testing resource inspection...")
    await builder.show_resource(['parser'])
    await builder.show_resource(['etl'])
    
    print("\n✅ Interactive Agent Builder test completed successfully!")
    print("\n🎯 To run the full interactive demo:")
    print("   python interactive_agent_builder.py")
    print("\n📚 Available commands:")
    print("   - help: Show all commands")
    print("   - create agent <name>: Create a new agent")
    print("   - configure agent <name>: Configure an agent")
    print("   - create department <name>: Create a new department")
    print("   - configure department <name>: Configure a department")
    print("   - run workflow <name>: Run a workflow")
    print("   - demo: Run the complete ETL demo")

if __name__ == "__main__":
    asyncio.run(test_interactive_builder()) 