#!/usr/bin/env python3
"""
Minimal test to debug workflow orchestration
"""

import os
import sys
from memra import Agent, Department, LLM
from memra.execution import ExecutionEngine

def test_minimal_orchestration():
    """Test minimal workflow orchestration"""
    
    print("🔍 TESTING MINIMAL WORKFLOW ORCHESTRATION")
    print("=" * 60)
    
    # Create simple LLM
    test_llm = LLM(model="llama-3.2-11b-vision-preview", temperature=0.1)
    
    # Agent 1: Simple data source
    agent1 = Agent(
        role="Data Source",
        job="Create test data",
        llm=test_llm,
        tools=[],  # No tools needed for this test
        output_key="test_data",
        input_keys=["test_input"]  # Accept input to pass through
    )
    
    # Agent 2: Data receiver
    agent2 = Agent(
        role="Data Receiver",
        job="Receive and display data",
        llm=test_llm,
        tools=[],  # No tools needed for this test
        input_keys=["test_data"],
        output_key="received_data"
    )
    
    # Create department
    test_department = Department(
        name="Minimal Test",
        mission="Test data flow between agents",
        agents=[agent1, agent2],
        workflow_order=["Data Source", "Data Receiver"]
    )
    
    # Mock input
    input_data = {"test_input": "hello", "test_data": "generated_data"}
    
    # Execute
    engine = ExecutionEngine()
    result = engine.execute_department(test_department, input_data)
    
    print(f"\n📊 Result: {result.success}")
    if result.data:
        print(f"📄 Data: {result.data}")
    else:
        print("❌ No data returned")

if __name__ == "__main__":
    test_minimal_orchestration() 