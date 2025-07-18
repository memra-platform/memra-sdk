#!/usr/bin/env python3
"""
Quick Demo of Interactive Agent Builder

This script demonstrates the interactive agent builder by running
through a complete workflow creation process automatically.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to import memra modules
sys.path.append(str(Path(__file__).parent.parent))

from interactive_agent_builder import InteractiveAgentBuilder

async def quick_demo():
    """Run a quick demo of the interactive agent builder"""
    
    print("🎬 QUICK DEMO: Interactive Agent Builder")
    print("="*50)
    print("This demo shows how to build an ETL workflow step by step.\n")
    
    # Create builder instance
    builder = InteractiveAgentBuilder()
    
    # Load tools
    print("🔍 Loading available tools...")
    await builder.load_available_tools()
    print(f"✅ Loaded {len(builder.available_tools)} tools\n")
    
    # Demo: Create agents
    print("🤖 STEP 1: Creating Agents")
    print("-" * 30)
    
    # Create parser agent
    from memra.models import Agent
    parser_agent = Agent(
        role="Invoice Parser",
        job="Extract data from invoice PDFs",
        tools=[builder.available_tools.get("PDFProcessor")],
        output_key="invoice_data"
    )
    builder.agents["parser"] = parser_agent
    print("✅ Created 'parser' agent")
    
    # Create validator agent
    validator_agent = Agent(
        role="Data Validator",
        job="Validate extracted invoice data",
        tools=[builder.available_tools.get("DataValidator")],
        output_key="validated_data"
    )
    builder.agents["validator"] = validator_agent
    print("✅ Created 'validator' agent")
    
    # Create writer agent
    writer_agent = Agent(
        role="Database Writer",
        job="Insert validated data into database",
        tools=[
            builder.available_tools.get("PostgresInsert"),
            builder.available_tools.get("SQLExecutor")
        ],
        output_key="insertion_result"
    )
    builder.agents["writer"] = writer_agent
    print("✅ Created 'writer' agent")
    
    # Show created agents
    print("\n📋 Created Agents:")
    for name, agent in builder.agents.items():
        print(f"  - {name}: {agent.job}")
        print(f"    Tools: {[t.name for t in agent.tools]}")
    
    # Demo: Create department
    print("\n🏢 STEP 2: Creating Department")
    print("-" * 30)
    
    from memra.models import Department
    etl_department = Department(
        name="ETL Pipeline",
        mission="Complete ETL workflow for invoice processing",
        agents=list(builder.agents.values()),
        workflow_order=[agent.role for agent in builder.agents.values()]
    )
    builder.departments["etl"] = etl_department
    print("✅ Created 'etl' department")
    
    print(f"\n📋 Department Configuration:")
    print(f"  - Name: {etl_department.name}")
    print(f"  - Mission: {etl_department.mission}")
    print(f"  - Agents: {[a.role for a in etl_department.agents]}")
    print(f"  - Workflow: {' → '.join(etl_department.workflow_order)}")
    
    # Demo: Show resources
    print("\n📋 STEP 3: Resource Management")
    print("-" * 30)
    
    print("Listing all resources:")
    await builder.list_resources([])
    
    print("\nShowing agent details:")
    await builder.show_resource(['parser'])
    
    print("\nShowing department details:")
    await builder.show_resource(['etl'])
    
    # Demo: Workflow execution (simulated)
    print("\n🚀 STEP 4: Workflow Execution")
    print("-" * 30)
    
    print("Ready to execute ETL workflow!")
    print("The workflow would:")
    print("  1. Parse invoice PDFs using PDFProcessor")
    print("  2. Validate extracted data using DataValidator")
    print("  3. Insert data into database using PostgresInsert")
    print("  4. Execute any follow-up SQL queries using SQLExecutor")
    
    print("\n🎯 To run the actual workflow:")
    print("  python interactive_agent_builder.py")
    print("  run workflow etl")
    
    print("\n🎓 To build your own workflow:")
    print("  1. create agent <name>")
    print("  2. configure agent <name>")
    print("  3. create department <name>")
    print("  4. configure department <name>")
    print("  5. run workflow <name>")
    
    print("\n✅ Quick demo completed!")
    print("The Interactive Agent Builder is ready to use!")

if __name__ == "__main__":
    asyncio.run(quick_demo()) 