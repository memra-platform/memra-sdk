#!/usr/bin/env python3
"""
Natural Language Agent Builder Demo

This script demonstrates the natural language agent builder by showing
how users can create agents and workflows using job posting style descriptions.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to import memra modules
sys.path.append(str(Path(__file__).parent.parent))

from natural_language_builder import NaturalLanguageBuilder

async def natural_language_demo():
    """Demo the natural language agent builder"""
    
    print("🎬 NATURAL LANGUAGE AGENT BUILDER DEMO")
    print("="*50)
    print("This demo shows how to create AI agents using natural language!")
    print("It's as easy as writing a job posting.\n")
    
    # Create builder instance
    builder = NaturalLanguageBuilder()
    
    # Load tools
    print("🔍 Loading available tools...")
    await builder.load_available_tools()
    print(f"✅ Loaded {len(builder.available_tools)} tools\n")
    
    # Demo examples
    examples = [
        "I need an agent to parse invoice PDFs",
        "Create a data validator",
        "I need a complete ETL pipeline for invoices"
    ]
    
    print("💼 DEMO EXAMPLES:")
    print("="*30)
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. User says: '{example}'")
        print("-" * 40)
        
        if "pipeline" in example.lower() or "etl" in example.lower():
            # This is a workflow request
            print("🏢 System creates a complete workflow:")
            print("   - Data Extractor: Extract data from source files")
            print("   - Data Validator: Validate extracted data for quality and accuracy")
            print("   - Data Writer: Insert validated data into database")
            print("   - Workflow: Data Extractor → Data Validator → Data Writer")
        else:
            # This is a single agent request
            if "parse" in example.lower() or "pdf" in example.lower():
                print("🤖 System creates a Data Extractor agent:")
                print("   - Role: Data Extractor")
                print("   - Job: Extract data from source files")
                print("   - Tools: PDFProcessor")
            elif "validate" in example.lower():
                print("🤖 System creates a Data Validator agent:")
                print("   - Role: Data Validator")
                print("   - Job: Validate extracted data for quality and accuracy")
                print("   - Tools: DataValidator")
    
    print("\n🎯 KEY FEATURES:")
    print("="*30)
    print("✅ Natural language input - just describe what you need")
    print("✅ Automatic tool selection - system chooses appropriate tools")
    print("✅ Smart role assignment - system determines agent roles")
    print("✅ Workflow creation - system builds complete pipelines")
    print("✅ Confirmation system - asks if the configuration looks right")
    print("✅ Interactive execution - run workflows immediately")
    
    print("\n🚀 HOW TO TRY IT:")
    print("="*30)
    print("1. Run the natural language builder:")
    print("   python run_natural_language_builder.py")
    print("\n2. Try these examples:")
    print("   'I need an invoice parser'")
    print("   'Create a data validator'")
    print("   'Build me a complete ETL pipeline'")
    print("   'I need a team to process documents'")
    
    print("\n💡 THE VISION:")
    print("="*30)
    print("This makes creating AI agents as easy as writing a job posting!")
    print("Instead of complex configuration, just describe what you need:")
    print("\n   'I need someone to process invoices and put them in our database'")
    print("   → System creates complete ETL workflow automatically")
    print("\n   'I want someone to check data quality'")
    print("   → System creates validation agent with appropriate tools")
    
    print("\n✅ Natural Language Agent Builder demo completed!")
    print("The future of AI workflow creation is here! 🎉")

if __name__ == "__main__":
    asyncio.run(natural_language_demo()) 