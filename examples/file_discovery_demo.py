#!/usr/bin/env python3
"""
File Discovery and Management Demo
Simple demonstration of intelligent file discovery tools
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memra import Agent, Department
from memra.execution import ExecutionEngine

# Set up environment
os.environ['MEMRA_API_KEY'] = 'memra-prod-2024-001'

def create_file_discovery_department():
    """Create a simple department for file discovery"""
    file_manager_agent = Agent(
        role="File Manager",
        job="Discover and manage files in directories",
        sops=[
            "Scan specified directory for files matching pattern",
            "List all discovered files with metadata",
            "Copy files from external locations to standard directories",
            "Provide file selection interface for multiple files"
        ],
        systems=["FileSystem"],
        tools=[
            {"name": "FileDiscovery", "hosted_by": "mcp"}
        ],
        input_keys=["directory", "pattern"],
        output_key="file_operations"
    )
    
    return Department(
        name="File Discovery",
        mission="Discover files in directories",
        agents=[file_manager_agent],
        workflow_order=["File Manager"],
        context={
            "mcp_bridge_url": "http://localhost:8081",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )

def create_file_copy_department():
    """Create a simple department for file copying"""
    file_copy_agent = Agent(
        role="File Copier",
        job="Copy files from external locations to standard directories",
        sops=[
            "Accept source file path and destination directory",
            "Copy file to destination with proper naming",
            "Verify copy operation success",
            "Return copy confirmation with metadata"
        ],
        systems=["FileSystem"],
        tools=[
            {"name": "FileCopy", "hosted_by": "mcp"}
        ],
        input_keys=["source_path", "destination_dir"],
        output_key="file_operations"
    )
    
    return Department(
        name="File Copy",
        mission="Copy files to standard directories",
        agents=[file_copy_agent],
        workflow_order=["File Copier"],
        context={
            "mcp_bridge_url": "http://localhost:8081",
            "mcp_bridge_secret": "test-secret-for-development"
        }
    )

def main():
    print("📁 File Discovery and Management Demo")
    print("=" * 50)
    
    engine = ExecutionEngine()
    
    # Demo 1: Discover files in invoices directory
    print("\n🔍 Demo 1: Discover files in invoices/ directory")
    
    discovery_dept = create_file_discovery_department()
    discovery_input = {
        "directory": "invoices",
        "pattern": "*.pdf"
    }
    
    result = engine.execute_department(discovery_dept, discovery_input)
    
    if result.success:
        print("✅ File discovery completed!")
        file_data = result.data.get('file_operations', {})
        
        if 'files' in file_data:
            print(f"\n📄 Found {file_data['files_found']} files:")
            for file_info in file_data['files']:
                print(f"  • {file_info['filename']} ({file_info['size']}) - {file_info['modified']}")
        else:
            print(f"📊 Scanned: {file_data.get('directory', 'unknown')} directory")
            print(f"🔍 Pattern: {file_data.get('pattern', 'unknown')}")
            print(f"📁 Files found: {file_data.get('files_found', 0)}")
    else:
        print(f"❌ Discovery failed: {result.error}")
    
    print("\n" + "="*50)
    
    # Demo 2: Copy external file
    print("\n📋 Demo 2: Copy external file to invoices/ directory")
    
    copy_dept = create_file_copy_department()
    copy_input = {
        "source_path": "/Users/tarpus/Downloads/new_invoice.pdf",
        "destination_dir": "invoices"
    }
    
    result = engine.execute_department(copy_dept, copy_input)
    
    if result.success:
        print("✅ File copy completed!")
        copy_data = result.data.get('file_operations', {})
        
        print(f"\n📁 Copy Details:")
        print(f"  Source: {copy_data.get('source_path', 'unknown')}")
        print(f"  Destination: {copy_data.get('destination_path', 'unknown')}")
        print(f"  Size: {copy_data.get('file_size', 'unknown')}")
        print(f"  Status: {copy_data.get('message', 'unknown')}")
    else:
        print(f"❌ Copy failed: {result.error}")
    
    print("\n" + "="*50)
    
    # Demo 3: Discover files in different directory
    print("\n🗂 Demo 3: Discover files in documents/ directory")
    
    docs_input = {
        "directory": "documents",
        "pattern": "*.*"
    }
    
    result = engine.execute_department(discovery_dept, docs_input)
    
    if result.success:
        print("✅ Document discovery completed!")
        doc_data = result.data.get('file_operations', {})
        print(f"📊 Scanned: {doc_data.get('directory', 'unknown')} directory")
        print(f"🔍 Pattern: {doc_data.get('pattern', 'unknown')}")
        print(f"📁 Files found: {doc_data.get('files_found', 0)}")
    else:
        print(f"❌ Document discovery failed: {result.error}")

if __name__ == "__main__":
    main() 