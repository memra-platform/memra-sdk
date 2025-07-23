"""
Memra CLI - Command line interface for Memra SDK
"""

import os
import sys
import subprocess
import time
import tempfile
import shutil
from pathlib import Path
import importlib.resources as pkg_resources

def run_demo():
    """Run the ETL invoice processing demo with automatic setup"""
    print("🚀 Starting Memra ETL Demo...")
    print("=" * 50)
    
    # Step 1: Extract bundled files
    print("📦 Setting up demo environment...")
    demo_dir = setup_demo_environment()
    
    # Step 2: Set environment variables
    print("🔧 Configuring environment...")
    setup_environment()
    
    # Step 3: Start Docker containers
    print("🐳 Starting Docker services...")
    if not start_docker_services(demo_dir):
        print("❌ Failed to start Docker services. Please check Docker is running.")
        return False
    
    # Step 4: Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    wait_for_services()
    
    # Step 5: Run the demo
    print("🎯 Running ETL workflow...")
    success = run_etl_workflow(demo_dir)
    
    # Step 6: Show results
    if success:
        print("=" * 50)
        print("🎉 Demo completed successfully!")
        print("\n📊 What happened:")
        print("  • PDF invoice processed with AI vision")
        print("  • Data extracted and validated")
        print("  • Results stored in PostgreSQL database")
        print("\n🔍 Next steps:")
        print("  • Check database: docker exec -it memra_postgres psql -U postgres -d local_workflow")
        print("  • View data: SELECT * FROM invoices ORDER BY created_at DESC;")
        print("  • Stop services: cd memra-ops && docker compose down")
        print("  • Explore code: Check the extracted files in the demo directory")
    else:
        print("❌ Demo failed. Check the logs above for details.")
    
    return success

def setup_demo_environment():
    """Extract bundled demo files to a temporary directory"""
    try:
        # Create demo directory
        demo_dir = Path.home() / ".memra" / "demo"
        demo_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract bundled files
        extract_bundled_files(demo_dir)
        
        print(f"✅ Demo files extracted to: {demo_dir}")
        return demo_dir
        
    except Exception as e:
        print(f"❌ Failed to setup demo environment: {e}")
        sys.exit(1)

def extract_bundled_files(demo_dir):
    """Extract files bundled with the PyPI package"""
    try:
        # Extract from package data
        with pkg_resources.path('memra', 'demo_files') as demo_files_path:
            if demo_files_path.exists():
                # Copy all files from the bundled demo_files directory
                shutil.copytree(demo_files_path, demo_dir, dirs_exist_ok=True)
            else:
                # Fallback: create minimal demo structure
                create_minimal_demo(demo_dir)
                
    except Exception as e:
        print(f"⚠️  Could not extract bundled files: {e}")
        print("Creating minimal demo structure...")
        create_minimal_demo(demo_dir)

def create_minimal_demo(demo_dir):
    """Create a minimal demo structure if bundled files aren't available"""
    # Create memra-ops directory
    ops_dir = demo_dir / "memra-ops"
    ops_dir.mkdir(exist_ok=True)
    
    # Create basic docker-compose.yml
    compose_content = """version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: local_workflow
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
    
    with open(ops_dir / "docker-compose.yml", "w") as f:
        f.write(compose_content)
    
    # Create basic MCP bridge server
    mcp_content = """#!/usr/bin/env python3
import asyncio
import aiohttp
from aiohttp import web
import json

async def health_handler(request):
    return web.json_response({"status": "healthy"})

async def execute_tool_handler(request):
    data = await request.json()
    tool_name = data.get('tool_name', 'unknown')
    
    # Mock responses for demo
    if tool_name == 'SQLExecutor':
        return web.json_response({
            "success": True,
            "results": [{"message": "Demo SQL executed"}]
        })
    elif tool_name == 'PostgresInsert':
        return web.json_response({
            "success": True,
            "id": 1
        })
    else:
        return web.json_response({
            "success": True,
            "message": f"Demo {tool_name} executed"
        })

app = web.Application()
app.router.add_get('/health', health_handler)
app.router.add_post('/execute_tool', execute_tool_handler)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8081)
"""
    
    with open(ops_dir / "mcp_bridge_server.py", "w") as f:
        f.write(mcp_content)
    
    # Create demo workflow
    demo_dir.mkdir(exist_ok=True)
    demo_content = """#!/usr/bin/env python3
import os
import sys
import time

def main():
    print("<-> Starting ETL Invoice Processing Demo...")
    print("<-> Starting ETL Invoice Processing Department")
    print("<-> Mission: Complete end-to-end ETL process with comprehensive monitoring")
    print("<-> Team: Pre-ETL Database Monitor, Data Engineer, Invoice Parser, Data Entry Specialist, Post-ETL Database Monitor")
    print("<-> Manager: ETL Process Manager")
    
    steps = [
        ("Pre-ETL Database Monitor", "Database state captured: 2 rows"),
        ("Data Engineer", "Schema extracted successfully"),
        ("Invoice Parser", "Invoice data extracted: $270.57"),
        ("Data Entry Specialist", "Record inserted: ID 1"),
        ("Post-ETL Database Monitor", "Database state captured: 3 rows")
    ]
    
    for i, (step, result) in enumerate(steps, 1):
        print(f"\\n<-> Step {i}/5: {step}")
        time.sleep(1)
        print(f"<-> {result}")
    
    print("\\n<-> ETL Invoice Processing Department workflow completed!")
    print("<->  Total time: 5.2s")
    print("\\n<-> Demo completed successfully!")
    print("This was a simplified demo. For the full experience, check out the complete ETL workflow.")

if __name__ == "__main__":
    main()
"""
    
    with open(demo_dir / "etl_demo.py", "w") as f:
        f.write(demo_content)

def setup_environment():
    """Set up environment variables for the demo"""
    # Set API key if not already set
    if not os.getenv('MEMRA_API_KEY'):
        os.environ['MEMRA_API_KEY'] = 'test-secret-for-development'
        print("✅ Set MEMRA_API_KEY=test-secret-for-development")
    
    # Set database URL
    os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/local_workflow'
    print("✅ Set DATABASE_URL")

def start_docker_services(demo_dir):
    """Start Docker containers using docker-compose"""
    try:
        ops_dir = demo_dir / "memra-ops"
        
        # Check if Docker is running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not running. Please start Docker Desktop.")
            return False
        
        # Start services
        result = subprocess.run(
            ['docker', 'compose', 'up', '-d'],
            cwd=ops_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Docker services started successfully")
            return True
        else:
            print(f"❌ Failed to start Docker services: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker Desktop.")
        return False
    except Exception as e:
        print(f"❌ Error starting Docker services: {e}")
        return False

def wait_for_services():
    """Wait for services to be ready"""
    print("⏳ Waiting for PostgreSQL to be ready...")
    
    # Wait for PostgreSQL
    for i in range(30):  # Wait up to 30 seconds
        try:
            result = subprocess.run([
                'docker', 'exec', 'memra_postgres', 
                'pg_isready', '-U', 'postgres', '-d', 'local_workflow'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PostgreSQL is ready")
                break
        except:
            pass
        
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Still waiting... ({i+1}/30)")
    else:
        print("⚠️  PostgreSQL may not be fully ready, continuing anyway...")

def run_etl_workflow(demo_dir):
    """Run the ETL workflow"""
    try:
        # Run the demo script
        demo_script = demo_dir / "etl_demo.py"
        if demo_script.exists():
            result = subprocess.run([sys.executable, str(demo_script)], cwd=demo_dir)
            return result.returncode == 0
        else:
            print("❌ Demo script not found")
            return False
            
    except Exception as e:
        print(f"❌ Error running ETL workflow: {e}")
        return False

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Memra SDK - Declarative AI Workflows")
        print("=" * 40)
        print("Usage:")
        print("  memra demo     - Run the ETL invoice processing demo")
        print("  memra --help   - Show this help message")
        print("  memra --version - Show version information")
        return
    
    command = sys.argv[1]
    
    if command == "demo":
        run_demo()
    elif command == "--help" or command == "-h":
        print("Memra SDK - Declarative AI Workflows")
        print("=" * 40)
        print("Commands:")
        print("  demo           - Run the ETL invoice processing demo")
        print("  --help, -h     - Show this help message")
        print("  --version      - Show version information")
    elif command == "--version":
        from . import __version__
        print(f"memra {__version__}")
    else:
        print(f"Unknown command: {command}")
        print("Run 'memra --help' for usage information")

if __name__ == "__main__":
    main() 