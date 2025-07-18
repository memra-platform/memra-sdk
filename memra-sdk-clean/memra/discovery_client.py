"""
Client-side tool discovery for Memra SDK
Queries the Memra API to discover available tools
"""

from typing import List, Dict, Any, Optional
from .tool_registry_client import ToolRegistryClient

def discover_tools(hosted_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Discover available tools from the Memra API
    
    Args:
        hosted_by: Filter tools by hosting provider ("memra" or "mcp")
        
    Returns:
        List of available tools with their descriptions
    """
    registry = ToolRegistryClient()
    return registry.discover_tools(hosted_by)

def check_api_health() -> bool:
    """
    Check if the Memra API is available
    
    Returns:
        True if API is healthy, False otherwise
    """
    registry = ToolRegistryClient()
    return registry.health_check()

def get_api_status() -> Dict[str, Any]:
    """
    Get detailed API status information
    
    Returns:
        Dictionary with API status details
    """
    registry = ToolRegistryClient()
    
    is_healthy = registry.health_check()
    tools = registry.discover_tools() if is_healthy else []
    
    return {
        "api_healthy": is_healthy,
        "api_url": registry.api_base,
        "tools_available": len(tools),
        "tools": tools
    } 