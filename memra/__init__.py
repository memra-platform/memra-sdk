"""
Memra SDK - A declarative orchestration framework for AI-powered business workflows
"""

from .models import (
    Agent, 
    Department, 
    LLM, 
    Tool, 
    ExecutionPolicy, 
    ExecutionTrace, 
    DepartmentResult, 
    DepartmentAudit
)
from .discovery_client import discover_tools, check_api_health, get_api_status

__version__ = "0.1.0"
__all__ = [
    "Agent", 
    "Department", 
    "LLM", 
    "Tool", 
    "ExecutionPolicy", 
    "ExecutionTrace", 
    "DepartmentResult", 
    "DepartmentAudit",
    "discover_tools"
] 