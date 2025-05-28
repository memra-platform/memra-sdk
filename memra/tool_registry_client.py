import httpx
import logging
import os
from typing import Dict, Any, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class ToolRegistryClient:
    """Client-side registry that calls Memra API for tool execution"""
    
    def __init__(self):
        self.api_base = os.getenv("MEMRA_API_URL", "https://api.memra.co")
        self.api_key = os.getenv("MEMRA_API_KEY")
        self.tools_cache = None
        
        if not self.api_key:
            raise ValueError(
                "MEMRA_API_KEY environment variable is required. "
                "Please contact info@memra.co for an API key."
            )
    
    def discover_tools(self, hosted_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discover available tools from the API"""
        try:
            # Use sync httpx for compatibility with existing sync code
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.api_base}/tools/discover",
                    headers={"X-API-Key": self.api_key}
                )
                response.raise_for_status()
                
                data = response.json()
                tools = data.get("tools", [])
                
                # Filter by hosted_by if specified
                if hosted_by:
                    tools = [t for t in tools if t.get("hosted_by") == hosted_by]
                
                self.tools_cache = tools
                logger.info(f"Discovered {len(tools)} tools from API")
                return tools
                
        except Exception as e:
            logger.error(f"Failed to discover tools from API: {e}")
            # Return empty list if API is unavailable
            return []
    
    def execute_tool(self, tool_name: str, hosted_by: str, input_data: Dict[str, Any], 
                    config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a tool via the API"""
        try:
            logger.info(f"Executing tool {tool_name} via API")
            
            # Prepare request payload
            payload = {
                "tool_name": tool_name,
                "hosted_by": hosted_by,
                "input_data": input_data,
                "config": config
            }
            
            # Make API call
            with httpx.Client(timeout=120.0) as client:  # Longer timeout for tool execution
                response = client.post(
                    f"{self.api_base}/tools/execute",
                    headers={
                        "X-API-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Tool {tool_name} executed successfully via API")
                return result
                
        except httpx.TimeoutException:
            logger.error(f"Tool {tool_name} execution timed out")
            return {
                "success": False,
                "error": f"Tool execution timed out after 120 seconds"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"API error for tool {tool_name}: {e.response.status_code}")
            return {
                "success": False,
                "error": f"API error: {e.response.status_code} - {e.response.text}"
            }
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def health_check(self) -> bool:
        """Check if the API is available"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.api_base}/health")
                return response.status_code == 200
        except:
            return False 