import importlib
import logging
import sys
import os
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing and executing tools via API calls only"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_known_tools()
    
    def _register_known_tools(self):
        """Register known tools with their metadata (no actual implementations)"""
        # Server-hosted tools (executed via Memra API)
        server_tools = [
            ("DatabaseQueryTool", "Query database schemas and data"),
            ("PDFProcessor", "Process PDF files and extract content"),
            ("OCRTool", "Perform OCR on images and documents"),
            ("InvoiceExtractionWorkflow", "Extract structured data from invoices"),
            ("FileReader", "Read files from the filesystem"),
        ]
        
        for tool_name, description in server_tools:
            self.register_tool(tool_name, None, "memra", description)
        
        # MCP-hosted tools (executed via MCP bridge)
        mcp_tools = [
            ("DataValidator", "Validate data against schemas"),
            ("PostgresInsert", "Insert data into PostgreSQL database"),
        ]
        
        for tool_name, description in mcp_tools:
            self.register_tool(tool_name, None, "mcp", description)
        
        logger.info(f"Registered {len(self.tools)} tool definitions")
    
    def register_tool(self, name: str, tool_class: Optional[type], hosted_by: str, description: str):
        """Register a tool in the registry (metadata only)"""
        self.tools[name] = {
            "class": tool_class,  # Will be None for API-based tools
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
        """Execute a tool - this should not be called directly in API-based mode"""
        logger.warning(f"Direct tool execution attempted for {tool_name}. Use API client instead.")
        return {
            "success": False,
            "error": "Direct tool execution not supported. Use API client for tool execution."
        } 