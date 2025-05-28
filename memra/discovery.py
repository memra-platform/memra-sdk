from typing import List, Dict, Any, Optional
from .tool_registry import ToolRegistry

def discover_tools(hosted_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Discover available tools in the Memra platform.
    
    Args:
        hosted_by: Filter tools by host ("memra" or "mcp"). If None, returns all tools.
    
    Returns:
        List of available tools with their metadata
    """
    registry = ToolRegistry()
    return registry.discover_tools(hosted_by) 