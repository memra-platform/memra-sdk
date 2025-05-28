import importlib
import logging
import sys
import os
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing and executing tools"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._add_project_to_path()
        self._load_builtin_tools()
    
    def _add_project_to_path(self):
        """Add the project root to Python path so we can import logic modules"""
        # Get the directory containing this file (memra package)
        current_dir = Path(__file__).parent
        # Go up one level to get the project root
        project_root = current_dir.parent
        
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
    
    def _load_builtin_tools(self):
        """Load tools from the logic directory"""
        try:
            # Load invoice tools
            from logic.invoice_tools import (
                DatabaseQueryTool, PDFProcessor, OCRTool, 
                InvoiceExtractionWorkflow, DataValidator, PostgresInsert
            )
            
            self.register_tool("DatabaseQueryTool", DatabaseQueryTool, "memra", 
                             "Query database schemas and data")
            self.register_tool("PDFProcessor", PDFProcessor, "memra", 
                             "Process PDF files and extract content")
            self.register_tool("OCRTool", OCRTool, "memra", 
                             "Perform OCR on images and documents")
            self.register_tool("InvoiceExtractionWorkflow", InvoiceExtractionWorkflow, "memra", 
                             "Extract structured data from invoices")
            self.register_tool("DataValidator", DataValidator, "memra", 
                             "Validate data against schemas")
            self.register_tool("PostgresInsert", PostgresInsert, "memra", 
                             "Insert data into PostgreSQL database")
            
            # Load file tools
            from logic.file_tools import FileReader
            self.register_tool("FileReader", FileReader, "memra", 
                             "Read files from the filesystem")
            
            logger.info(f"Loaded {len(self.tools)} builtin tools")
            
        except ImportError as e:
            logger.warning(f"Could not load some tools: {e}")
    
    def register_tool(self, name: str, tool_class: type, hosted_by: str, description: str):
        """Register a tool in the registry"""
        self.tools[name] = {
            "class": tool_class,
            "hosted_by": hosted_by,
            "description": description
        }
        logger.debug(f"Registered tool: {name} (hosted by {hosted_by})")
    
    def discover_tools(self, hosted_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discover available tools, optionally filtered by host"""
        tools = []
        for name, info in self.tools.items():
            if hosted_by is None or info["hosted_by"] == hosted_by:
                tools.append({
                    "name": name,
                    "hosted_by": info["hosted_by"],
                    "description": info["description"]
                })
        return tools
    
    def execute_tool(self, tool_name: str, hosted_by: str, input_data: Dict[str, Any], 
                    config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a tool with the given input data"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found in registry"
            }
        
        tool_info = self.tools[tool_name]
        if tool_info["hosted_by"] != hosted_by:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' is hosted by '{tool_info['hosted_by']}', not '{hosted_by}'"
            }
        
        try:
            # Instantiate tool
            tool_class = tool_info["class"]
            
            # Some tools need credentials/config for initialization
            if tool_name in ["DatabaseQueryTool", "PostgresInsert"]:
                if "connection" in input_data:
                    # Parse connection string or use credentials
                    credentials = self._parse_connection(input_data["connection"])
                    tool_instance = tool_class(credentials)
                else:
                    return {
                        "success": False,
                        "error": f"Tool '{tool_name}' requires database credentials"
                    }
            elif tool_name == "InvoiceExtractionWorkflow":
                # This tool needs to be instantiated to initialize the LLM client
                tool_instance = tool_class()
            else:
                tool_instance = tool_class()
            
            # Execute tool based on its type
            result = self._execute_tool_method(tool_instance, tool_name, input_data, config)
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_tool_method(self, tool_instance: Any, tool_name: str, 
                           input_data: Dict[str, Any], config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the appropriate method on the tool instance"""
        
        if tool_name == "DatabaseQueryTool":
            return tool_instance.get_schema("invoices")  # Default to invoices table
        
        elif tool_name == "PDFProcessor":
            file_path = input_data.get("file", "")
            return tool_instance.process_pdf(file_path)
        
        elif tool_name == "OCRTool":
            # Assume PDF processor output is passed as input
            return {"extracted_text": tool_instance.extract_text(input_data)}
        
        elif tool_name == "InvoiceExtractionWorkflow":
            text = input_data.get("extracted_text", "")
            schema = input_data.get("invoice_schema", {})
            return tool_instance.extract_data(text, schema)
        
        elif tool_name == "DataValidator":
            data = input_data.get("invoice_data", {})
            schema = input_data.get("invoice_schema", {})
            return tool_instance.validate(data, schema)
        
        elif tool_name == "PostgresInsert":
            data = input_data.get("invoice_data", {})
            return tool_instance.insert_record("invoices", data)
        
        elif tool_name == "FileReader":
            file_path = config.get("path") if config else input_data.get("file_path")
            if not file_path:
                raise ValueError("FileReader requires a file path")
            return tool_instance.read_file(file_path)
        
        else:
            raise ValueError(f"Unknown tool execution method for {tool_name}")
    
    def _parse_connection(self, connection_string: str) -> Dict[str, Any]:
        """Parse a connection string into credentials"""
        # Simple parser for postgres://user:pass@host:port/database
        if connection_string.startswith("postgres://"):
            # This is a simplified parser - in production you'd use a proper URL parser
            parts = connection_string.replace("postgres://", "").split("/")
            db_part = parts[1] if len(parts) > 1 else "finance"
            auth_host = parts[0].split("@")
            host_port = auth_host[1].split(":") if len(auth_host) > 1 else ["localhost", "5432"]
            user_pass = auth_host[0].split(":") if len(auth_host) > 1 else ["user", "pass"]
            
            return {
                "host": host_port[0],
                "port": int(host_port[1]) if len(host_port) > 1 else 5432,
                "database": db_part,
                "user": user_pass[0],
                "password": user_pass[1] if len(user_pass) > 1 else ""
            }
        
        return {"connection_string": connection_string} 