from memra.sdk.models import Agent, Department, Tool

# Define the tools that our agents will use
data_extraction_tool = Tool(
    name="PropaneDataExtractor",
    description="Extracts propane-related data from various sources",
    hosted_by="memra"
)

planning_tool = Tool(
    name="PropaneDeliveryPlanner",
    description="Plans optimal propane delivery routes and schedules",
    hosted_by="memra"
)

execution_tool = Tool(
    name="PropaneDeliveryExecutor",
    description="Executes and tracks propane deliveries",
    hosted_by="memra"
)

# Define our agents
data_extractor = Agent(
    role="Data Extraction Specialist",
    job="Extract and validate propane delivery data",
    tools=[data_extraction_tool],
    systems=["CustomerDatabase", "PropaneLevelsAPI"],
    input_keys=["customer_ids", "date_range"],
    output_key="extracted_data"
)

delivery_planner = Agent(
    role="Delivery Route Planner",
    job="Plan optimal delivery routes and schedules",
    tools=[planning_tool],
    systems=["RouteOptimizationEngine"],
    input_keys=["extracted_data"],
    output_key="delivery_plan"
)

delivery_executor = Agent(
    role="Delivery Coordinator",
    job="Execute and monitor propane deliveries",
    tools=[execution_tool],
    systems=["DeliveryTrackingSystem"],
    input_keys=["delivery_plan"],
    output_key="delivery_status"
)

# Define the manager agent that oversees the workflow
manager = Agent(
    role="Propane Operations Manager",
    job="Oversee and coordinate the propane delivery workflow",
    llm={"model": "claude-3-opus"},
    sops=[
        "Validate data quality",
        "Handle delivery exceptions",
        "Optimize resource allocation"
    ],
    input_keys=["extracted_data", "delivery_plan", "delivery_status"],
    output_key="workflow_status"
)

# Create the Propane Delivery Department
propane_department = Department(
    name="Propane Delivery Operations",
    mission="Efficiently manage and execute propane deliveries",
    agents=[data_extractor, delivery_planner, delivery_executor],
    manager_agent=manager,
    workflow_order=[
        "Data Extraction Specialist",
        "Delivery Route Planner",
        "Delivery Coordinator"
    ]
)

# Example usage
if __name__ == "__main__":
    # This is how a developer would use the department
    result = propane_department.run({
        "customer_ids": ["CUST001", "CUST002"],
        "date_range": {
            "start": "2024-03-20",
            "end": "2024-03-27"
        }
    })
    print(f"Workflow result: {result}") 