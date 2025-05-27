from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import importlib
import logging
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Memra Tool Execution API",
    description="API for executing Memra workflow tools",
    version="1.0.0"
)

# Request/Response models
class ToolExecutionRequest(BaseModel):
    tool_name: str
    hosted_by: str
    input_data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None

class ToolExecutionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ToolDiscoveryResponse(BaseModel):
    tools: List[Dict[str, str]]

# Authentication
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key against hardcoded list of valid keys"""
    # Get valid keys from environment variable or use defaults
    valid_keys = os.getenv("MEMRA_API_KEYS", "dev-key,demo-key,early-access-001,early-access-002").split(",")
    
    if not x_api_key:
        raise HTTPException(
            status_code=401, 
            detail="Missing API key. Please provide X-API-Key header."
        )
    
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=401, 
            detail="Invalid API key. Please contact info@memra.co for access."
        )
    
    logger.info(f"Valid API key used: {x_api_key}")
    return x_api_key

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Memra API Server", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check for Fly.io"""
    return {"status": "healthy"}

@app.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecutionRequest,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """Execute a tool with the given input data"""
    try:
        logger.info(f"Executing tool: {request.tool_name}")
        
        # Import the tool registry from local logic
        from memra.tool_registry import ToolRegistry
        
        # Create registry and execute tool
        registry = ToolRegistry()
        result = registry.execute_tool(
            request.tool_name,
            request.hosted_by,
            request.input_data,
            request.config
        )
        
        return ToolExecutionResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return ToolExecutionResponse(
            success=False,
            error=str(e)
        )

@app.get("/tools/discover", response_model=ToolDiscoveryResponse)
async def discover_tools(api_key: Optional[str] = Depends(verify_api_key)):
    """Discover available tools"""
    try:
        from memra.tool_registry import ToolRegistry
        
        registry = ToolRegistry()
        tools = registry.discover_tools()
        
        return ToolDiscoveryResponse(tools=tools)
        
    except Exception as e:
        logger.error(f"Tool discovery failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 