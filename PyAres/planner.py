from PyAres import AresPlannerService
from PyAres import PlanRequest
from PyAres import PlanResponse
from PyAres import AresDataType

import random

def plan(request: PlanRequest) -> PlanResponse:
    print("Planning Requested!")
    planned_values = []
    names = []

    for param in request.parameters:
        planned_values.append(random.uniform(param.minimum_value, param.maxiumum_value))
        names.append(param.name)

    return PlanResponse(parameter_names=names, parameter_values=planned_values)


if __name__ == "__main__":
    #Basic details about your planner
    name = "Demo Planner"
    version = "1.0.0"
    description = "This is a test planner to demonstrate working with PyAres to create planners!"
    pythonDemoPlanner = AresPlannerService(plan, name, description, version)

    #Add Supported Types
    pythonDemoPlanner.add_supported_type(AresDataType.NUMBER)