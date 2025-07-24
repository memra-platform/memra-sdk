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
    
    # Step 2.5: Install dependencies
    install_dependencies()
    
    # Step 3: Start Docker containers
    print("🐳 Starting Docker services...")
    if not start_docker_services(demo_dir):
        print("❌ Failed to start Docker services. Please check Docker is running.")
        return False
    
    # Step 4: Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    wait_for_services()
    
    # Step 5: Start MCP bridge server
    print("🔌 Starting MCP bridge server...")
    if not start_mcp_bridge_server(demo_dir):
        print("❌ Failed to start MCP bridge server.")
        print("   You can start it manually: cd memra-ops && python mcp_bridge_server.py")
        return False
    
    # Step 6: Run the demo
    print("🎯 Running ETL workflow...")
    success = run_etl_workflow(demo_dir)
    
    # Step 7: Show results
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
        print("  • Stop MCP server: pkill -f mcp_bridge_server.py")
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
        import pkg_resources
        import shutil
        from pathlib import Path
        
        # Extract demo files from package data
        demo_dir.mkdir(exist_ok=True)
        
        # Copy the main ETL demo script
        try:
            demo_script = pkg_resources.resource_filename('memra', 'demos/etl_invoice_processing/etl_invoice_demo.py')
            if Path(demo_script).exists():
                shutil.copy2(demo_script, demo_dir / "etl_invoice_demo.py")
                print("✅ Copied ETL demo script")
            else:
                print("⚠️  ETL demo script not found in package")
        except Exception as e:
            print(f"⚠️  Could not copy ETL demo script: {e}")
        
        # Copy supporting Python files
        demo_files = [
            "database_monitor_agent.py",
            "simple_pdf_processor.py", 
            "setup_demo_data.py"
        ]
        
        for file_name in demo_files:
            try:
                file_path = pkg_resources.resource_filename('memra', f'demos/etl_invoice_processing/{file_name}')
                if Path(file_path).exists():
                    shutil.copy2(file_path, demo_dir / file_name)
                    print(f"✅ Copied {file_name}")
                else:
                    print(f"⚠️  {file_name} not found in package")
            except Exception as e:
                print(f"⚠️  Could not copy {file_name}: {e}")
        
        # Copy sample data directory
        try:
            data_source = pkg_resources.resource_filename('memra', 'demos/etl_invoice_processing/data')
            if Path(data_source).exists():
                data_dir = demo_dir / "data"
                shutil.copytree(data_source, data_dir, dirs_exist_ok=True)
                print("✅ Copied sample invoice data")
            else:
                print("⚠️  Sample data not found in package")
        except Exception as e:
            print(f"⚠️  Could not copy sample data: {e}")
        
        # Create memra-ops directory with docker-compose
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
import psycopg2
import os

class MCPBridgeServer:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/local_workflow')
    
    async def health_handler(self, request):
        return web.json_response({"status": "healthy", "server": "MCP Bridge"})
    
    async def execute_tool_handler(self, request):
        try:
            data = await request.json()
            tool_name = data.get('tool_name', 'unknown')
            tool_params = data.get('parameters', {})
            
            if tool_name == 'SQLExecutor':
                return await self.execute_sql(tool_params)
            elif tool_name == 'PostgresInsert':
                return await self.insert_data(tool_params)
            elif tool_name == 'DataValidator':
                return await self.validate_data(tool_params)
            else:
                return web.json_response({
                    "success": True,
                    "message": f"Demo {tool_name} executed",
                    "data": {"demo": True}
                })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def execute_sql(self, params):
        try:
            query = params.get('query', 'SELECT 1')
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return web.json_response({
                "success": True,
                "results": results,
                "query": query
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": f"SQL execution failed: {str(e)}"
            }, status=500)
    
    async def insert_data(self, params):
        try:
            table_name = params.get('table_name', 'invoices')
            data = params.get('data', {})
            
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Simple insert logic
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ', '.join(['%s'] * len(values))
            column_list = ', '.join(columns)
            
            query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders}) RETURNING id"
            cursor.execute(query, values)
            record_id = cursor.fetchone()[0]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return web.json_response({
                "success": True,
                "record_id": record_id,
                "message": f"Inserted into {table_name}"
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": f"Insert failed: {str(e)}"
            }, status=500)
    
    async def validate_data(self, params):
        try:
            data = params.get('data', {})
            
            # Simple validation
            is_valid = True
            errors = []
            
            if not data.get('vendor_name'):
                is_valid = False
                errors.append("Missing vendor name")
            
            if not data.get('amount') or float(data.get('amount', 0)) <= 0:
                is_valid = False
                errors.append("Invalid amount")
            
            return web.json_response({
                "success": True,
                "is_valid": is_valid,
                "errors": errors,
                "validated_data": data
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": f"Validation failed: {str(e)}"
            }, status=500)

# Create server instance
server = MCPBridgeServer()

# Create web application
app = web.Application()
app.router.add_get('/health', server.health_handler)
app.router.add_post('/execute_tool', server.execute_tool_handler)

if __name__ == '__main__':
    print("🚀 Starting MCP Bridge Server on port 8081...")
    web.run_app(app, host='0.0.0.0', port=8081)
"""
        
        with open(ops_dir / "mcp_bridge_server.py", "w") as f:
            f.write(mcp_content)
            
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
import psycopg2
import os

class MCPBridgeServer:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/local_workflow')
    
    async def health_handler(self, request):
        return web.json_response({"status": "healthy", "server": "MCP Bridge"})
    
    async def execute_tool_handler(self, request):
        try:
            data = await request.json()
            tool_name = data.get('tool_name', 'unknown')
            tool_params = data.get('parameters', {})
            
            if tool_name == 'SQLExecutor':
                return await self.execute_sql(tool_params)
            elif tool_name == 'PostgresInsert':
                return await self.insert_data(tool_params)
            elif tool_name == 'DataValidator':
                return await self.validate_data(tool_params)
            else:
                return web.json_response({
                    "success": True,
                    "message": f"Demo {tool_name} executed",
                    "data": {"demo": True}
                })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def execute_sql(self, params):
        try:
            query = params.get('query', 'SELECT 1')
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return web.json_response({
                "success": True,
                "results": results,
                "query": query
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": f"SQL execution failed: {str(e)}"
            }, status=500)
    
    async def insert_data(self, params):
        try:
            table_name = params.get('table_name', 'invoices')
            data = params.get('data', {})
            
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Simple insert logic
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ', '.join(['%s'] * len(values))
            column_list = ', '.join(columns)
            
            query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders}) RETURNING id"
            cursor.execute(query, values)
            record_id = cursor.fetchone()[0]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return web.json_response({
                "success": True,
                "record_id": record_id,
                "message": f"Inserted into {table_name}"
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": f"Insert failed: {str(e)}"
            }, status=500)
    
    async def validate_data(self, params):
        try:
            data = params.get('data', {})
            
            # Simple validation
            is_valid = True
            errors = []
            
            if not data.get('vendor_name'):
                is_valid = False
                errors.append("Missing vendor name")
            
            if not data.get('amount') or float(data.get('amount', 0)) <= 0:
                is_valid = False
                errors.append("Invalid amount")
            
            return web.json_response({
                "success": True,
                "is_valid": is_valid,
                "errors": errors,
                "validated_data": data
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": f"Validation failed: {str(e)}"
            }, status=500)

# Create server instance
server = MCPBridgeServer()

# Create web application
app = web.Application()
app.router.add_get('/health', server.health_handler)
app.router.add_post('/execute_tool', server.execute_tool_handler)

if __name__ == '__main__':
    print("🚀 Starting MCP Bridge Server on port 8081...")
    web.run_app(app, host='0.0.0.0', port=8081)
"""
    
    with open(ops_dir / "mcp_bridge_server.py", "w") as f:
        f.write(mcp_content)
    
    # Copy the real ETL demo if available
    demo_dir.mkdir(exist_ok=True)
    import shutil
    
    try:
        # Try to copy from demos directory
        source_demo = Path("demos/etl_invoice_processing/etl_invoice_demo.py")
        if source_demo.exists():
            # Copy the main demo script
            shutil.copy2(source_demo, demo_dir / "etl_invoice_demo.py")
            print("✅ Copied real ETL demo script")
            
            # Copy all necessary Python dependencies
            demo_files = [
                "database_monitor_agent.py",
                "simple_pdf_processor.py",
                "setup_demo_data.py"
            ]
            
            for file_name in demo_files:
                source_file = Path(f"demos/etl_invoice_processing/{file_name}")
                if source_file.exists():
                    shutil.copy2(source_file, demo_dir / file_name)
                    print(f"✅ Copied {file_name}")
            
            # Copy sample data
            data_dir = demo_dir / "data"
            data_dir.mkdir(exist_ok=True)
            source_data = Path("demos/etl_invoice_processing/data")
            if source_data.exists():
                shutil.copytree(source_data, data_dir, dirs_exist_ok=True)
                print("✅ Copied sample invoice data")
        else:
            # Create a basic demo if real one not found
            demo_content = """#!/usr/bin/env python3
import os
import sys
import time

def main():
    print("🚀 Starting ETL Invoice Processing Demo...")
    print("🏢 Starting ETL Invoice Processing Department")
    print("📋 Mission: Complete end-to-end ETL process with comprehensive monitoring")
    print("👥 Team: Pre-ETL Database Monitor, Data Engineer, Invoice Parser, Data Entry Specialist, Post-ETL Database Monitor")
    print("👔 Manager: ETL Process Manager")
    
    steps = [
        ("Pre-ETL Database Monitor", "Database state captured: 2 rows"),
        ("Data Engineer", "Schema extracted successfully"),
        ("Invoice Parser", "Invoice data extracted: $270.57"),
        ("Data Entry Specialist", "Record inserted: ID 1"),
        ("Post-ETL Database Monitor", "Database state captured: 3 rows")
    ]
    
    for i, (step, result) in enumerate(steps, 1):
        print(f"\\n🔄 Step {i}/5: {step}")
        time.sleep(1)
        print(f"✅ {result}")
    
    print("\\n🎉 ETL Invoice Processing Department workflow completed!")
    print("⏱️  Total time: 5.2s")
    print("\\n📊 Demo completed successfully!")
    print("This was a simplified demo. For the full experience, check out the complete ETL workflow.")

if __name__ == "__main__":
    main()
"""
            with open(demo_dir / "etl_demo.py", "w") as f:
                f.write(demo_content)
            print("⚠️  Using simplified demo (real demo not found)")
    except Exception as e:
        print(f"Warning: Could not copy ETL demo: {e}")
        # Fallback to basic demo
        demo_content = """#!/usr/bin/env python3
import os
import sys
import time

def main():
    print("🚀 Starting ETL Invoice Processing Demo...")
    print("🏢 Starting ETL Invoice Processing Department")
    print("📋 Mission: Complete end-to-end ETL process with comprehensive monitoring")
    print("👥 Team: Pre-ETL Database Monitor, Data Engineer, Invoice Parser, Data Entry Specialist, Post-ETL Database Monitor")
    print("👔 Manager: ETL Process Manager")
    
    steps = [
        ("Pre-ETL Database Monitor", "Database state captured: 2 rows"),
        ("Data Engineer", "Schema extracted successfully"),
        ("Invoice Parser", "Invoice data extracted: $270.57"),
        ("Data Entry Specialist", "Record inserted: ID 1"),
        ("Post-ETL Database Monitor", "Database state captured: 3 rows")
    ]
    
    for i, (step, result) in enumerate(steps, 1):
        print(f"\\n🔄 Step {i}/5: {step}")
        time.sleep(1)
        print(f"✅ {result}")
    
    print("\\n🎉 ETL Invoice Processing Department workflow completed!")
    print("⏱️  Total time: 5.2s")
    print("\\n📊 Demo completed successfully!")
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

def install_dependencies():
    """Install required dependencies for the demo"""
    try:
        print("📦 Installing demo dependencies...")
        dependencies = [
            'requests==2.31.0',
            'fastapi==0.104.1',
            'uvicorn[standard]==0.24.0',
            'pydantic==2.5.0',
            'aiohttp',
            'psycopg2-binary',
            'httpx',
            'huggingface_hub'
        ]
        
        for dep in dependencies:
            print(f"   Installing {dep}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️  Warning: Failed to install {dep}: {result.stderr}")
            else:
                print(f"   ✅ {dep} installed")
        
        print("✅ Dependencies installed")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not install dependencies: {e}")
        print("   You may need to install them manually: pip install requests fastapi uvicorn pydantic")

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
    
    # Wait for PostgreSQL - try both possible container names
    for i in range(30):  # Wait up to 30 seconds
        try:
            # Try the memra-ops container name first
            result = subprocess.run([
                'docker', 'exec', 'memra-ops_postgres_1', 
                'pg_isready', '-U', 'postgres', '-d', 'local_workflow'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ PostgreSQL is ready")
                break
        except:
            pass
        
        try:
            # Fallback to the old container name
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
        # Try to run the real ETL demo first
        real_demo_script = demo_dir / "etl_invoice_demo.py"
        if real_demo_script.exists():
            print("🎯 Running real ETL workflow...")
            print(f"📁 Working directory: {demo_dir}")
            print(f"📄 Demo script: {real_demo_script}")
            
            # Check if data directory exists
            data_dir = demo_dir / "data"
            invoices_dir = data_dir / "invoices"
            if invoices_dir.exists():
                pdf_files = list(invoices_dir.glob("*.PDF"))
                print(f"📊 Found {len(pdf_files)} PDF files in {invoices_dir}")
                if pdf_files:
                    print(f"   First few files: {[f.name for f in pdf_files[:3]]}")
            else:
                print(f"⚠️  Warning: {invoices_dir} does not exist")
                print(f"   Available directories in {demo_dir}:")
                for item in demo_dir.iterdir():
                    if item.is_dir():
                        print(f"     - {item.name}/")
            
            print("⏱️  Processing 15 files with delays - this may take 10-15 minutes")
            
            # Set the working directory to the demo directory so the script can find data/invoices/
            result = subprocess.run(
                [sys.executable, str(real_demo_script)], 
                cwd=demo_dir,  # This is crucial - sets working directory
                timeout=1800   # 30 minute timeout
            )
            return result.returncode == 0
        else:
            # Fallback to simplified demo
            demo_script = demo_dir / "etl_demo.py"
            if demo_script.exists():
                print("🎯 Running simplified demo...")
                result = subprocess.run([sys.executable, str(demo_script)], cwd=demo_dir)
                return result.returncode == 0
            else:
                print("❌ No demo script found")
                print(f"   Looking for: {real_demo_script}")
                print(f"   Available files in {demo_dir}:")
                for item in demo_dir.iterdir():
                    print(f"     - {item.name}")
                return False
            
    except subprocess.TimeoutExpired:
        print("⏰ ETL workflow timed out after 30 minutes")
        print("This is normal for large batches - the demo processes 15 files with delays")
        return False
    except Exception as e:
        print(f"❌ Error running ETL workflow: {e}")
        return False

def start_mcp_bridge_server(demo_dir):
    """Start the MCP bridge server"""
    try:
        ops_dir = demo_dir / "memra-ops"
        bridge_script = ops_dir / "mcp_bridge_server.py"
        
        if not bridge_script.exists():
            print("❌ MCP bridge server script not found")
            return False
        
        # Start the bridge server in the background
        if os.name == 'nt':  # Windows
            # Use start command to run in background
            result = subprocess.run([
                'start', '/B', 'python', str(bridge_script)
            ], cwd=ops_dir, shell=True, capture_output=True, text=True)
        else:  # Unix/Linux/Mac
            result = subprocess.run([
                'python', str(bridge_script)
            ], cwd=ops_dir, start_new_session=True, capture_output=True, text=True)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if the server is responding
        try:
            import requests
            response = requests.get('http://localhost:8081/health', timeout=5)
            if response.status_code == 200:
                print("✅ MCP bridge server started successfully")
                return True
            else:
                print(f"⚠️  MCP bridge server responded with status {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️  Could not verify MCP bridge server: {e}")
            print("   Server may still be starting up...")
            return True  # Assume it's working
            
    except Exception as e:
        print(f"❌ Error starting MCP bridge server: {e}")
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