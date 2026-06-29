from PyAres import *
from typing import List
import random

def generate_plans(request: PlanRequest) -> List[Plan]:    
    plans = []
    for i in request.previous_plan_status_codes:
        print(f"Status Code: {i}")

    # Make as many plans as was requested
    for i in range(request.batch_size):
        current_params = []
        for param in request.parameters:
            # Simple Logic: Pick a random value within the allowed range
            val = random.uniform(param.minimum_value, param.maximum_value)
            current_params.append(PlannedParameter(param.name, val))
        
        plans.append(Plan(current_params, Outcome.SUCCESS))

    return plans

if __name__ == "__main__":
    service = AresPlannerService(
        generate_plans, 
        "Random Search Planner", 
        "This planner picks random values within bounds.", 
        "1.0.0"
    )

    # Tell ARES we can plan for Numeric values
    service.add_supported_type(AresDataType.NUMBER)

    service.start()