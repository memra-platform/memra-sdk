#!/usr/bin/env python3
"""
Launcher for Natural Language Agent Builder

This script activates the conda environment and runs the natural language
agent builder demo that allows users to create agents using job posting style descriptions.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point"""
    print("🚀 Starting Natural Language Agent Builder...")
    print("="*50)
    
    # Check if we're in the right directory
    current_dir = Path(__file__).parent
    if not (current_dir / "natural_language_builder.py").exists():
        print("❌ Error: natural_language_builder.py not found!")
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
    
    # Run the natural language builder
    print("🎯 Launching Natural Language Agent Builder...\n")
    
    try:
        # Change to the demos directory and run the natural language builder
        os.chdir(current_dir)
        subprocess.run([sys.executable, "natural_language_builder.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Thanks for trying the Natural Language Agent Builder!")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 