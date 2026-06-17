from PyAres import AresPlannerService, PlanRequest, PlanResponse, AresDataType
import random

def generate_plan(request: PlanRequest) -> PlanResponse:
    planned_values = []
    names = []

    # Iterate through every parameter configured in the ARES Experiment
    for param in request.parameters:
        # Simple Logic: Pick a random value within the allowed range
        val = random.uniform(param.minimum_value, param.maximum_value)
        
        names.append(param.name)
        planned_values.append(val)

    return PlanResponse(parameter_names=names, parameter_values=planned_values)

if __name__ == "__main__":
    service = AresPlannerService(
        generate_plan, 
        "Random Search Planner", 
        "This planner picks random values within bounds.", 
        "1.0.0"
    )

    # Tell ARES we can plan for Numeric values
    service.add_supported_type(AresDataType.NUMBER)

    service.start()