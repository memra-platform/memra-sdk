"""
Memra SDK - Declarative AI Workflows

A framework for building AI-powered business workflows using a declarative approach.
Think of it as "Kubernetes for business logic" where agents are the pods and 
departments are the deployments.
"""

__version__ = "0.2.2"

# Core imports
from .models import Agent, Department, Tool
from .execution import ExecutionEngine

# Make key classes available at package level
__all__ = [
    "Agent",
    "Department", 
    "Tool",
    "ExecutionEngine",
    "__version__"
]

# Optional: Add version check for compatibility
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("Memra requires Python 3.8 or higher") 