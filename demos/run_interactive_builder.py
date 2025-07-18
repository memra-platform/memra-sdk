#!/usr/bin/env python3
"""
Launcher for Interactive Agent Builder Demo

This script activates the conda environment and runs the interactive
agent builder demo that allows users to construct ETL workflow agents
through a text-based interface.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point"""
    print("🚀 Starting Interactive Agent Builder Demo...")
    print("="*50)
    
    # Check if we're in the right directory
    current_dir = Path(__file__).parent
    if not (current_dir / "interactive_agent_builder.py").exists():
        print("❌ Error: interactive_agent_builder.py not found!")
        print("Please run this script from the demos directory.")
        sys.exit(1)
    
    # Check if conda environment is activated
    if "CONDA_DEFAULT_ENV" not in os.environ or os.environ["CONDA_DEFAULT_ENV"] != "memra":
        print("⚠️  Warning: 'memra' conda environment not detected!")
        print("Please activate it with: conda activate memra")
        print("Continuing anyway...\n")
    
    # Check if required services are running
    print("🔍 Checking required services...")
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "postgres" in result.stdout:
            print("✅ PostgreSQL is running")
        else:
            print("⚠️  PostgreSQL not detected. Starting services...")
            subprocess.run(["docker", "compose", "up", "-d", "postgres"], check=True)
            print("✅ PostgreSQL started")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not check Docker services: {e}")
        print("Continuing anyway...\n")
    
    # Run the interactive builder
    print("🤖 Launching Interactive Agent Builder...\n")
    
    try:
        # Change to the demos directory and run the interactive builder
        os.chdir(current_dir)
        subprocess.run([sys.executable, "interactive_agent_builder.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Thanks for trying the Interactive Agent Builder!")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 