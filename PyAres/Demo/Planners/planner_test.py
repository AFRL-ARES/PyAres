from PyAres import *

import random

def plan(request: PlanRequest) -> PlanResponse:
  print("Planning Requested!")
  new_values = []
  gpdoods = []
  names = []

  for param in request.parameters:
    if param.planner_name == "GPRDood":
      gpdoods.append(param)

    if param.planner_name == "Random Planner":
      new_value = random_planner(param)
      new_values.append(new_value)
      names.append(param.name)

    elif param.planner_name == "Gradual Planner":
      new_value = gradual_planner(param)
      new_values.append(new_value)
      names.append(param.name)

    else:
      print("Invalid planner name detected... defaulting to random")
      new_value = random_planner(param)
      new_values.append(new_value)
      names.append(param.name)

  return PlanResponse(parameter_names=names, parameter_values=new_values)

def random_planner(param: PlanningParameter) -> float:
  if param.data_type == AresDataType.NUMBER:
    return random.uniform(param.minimum_value, param.maximum_value)
 
  else:
    print("Found a non-number....")
    return 0
  
def gradual_planner(param: PlanningParameter) -> float:
  if(param.data_type == AresDataType.NUMBER):
    if len(param.param_history) == 0:
      return param.minimum_value
    
    previous_value = param.param_history[-1].planned_value
    previous_value += 5

    if previous_value > param.maximum_value:
      return param.minimum_value
    
    else:
      return previous_value
    
  else:
    return 0
    
if __name__ == "__main__":
  #Basic details about your planner
  name = "Python Test Planner"
  version = "1.0.0"
  description = "This is a test planner to demonstrate working with PyAres to create planners!"
  pythonDemoPlanner = AresPlannerService(plan, name, description, version)

  #Add Supported Types
  pythonDemoPlanner.add_supported_type(AresDataType.NUMBER)

  #Add Planner Options
  pythonDemoPlanner.add_planner_option("Random Planner", "A planner that returns random values", "1.0.0")
  pythonDemoPlanner.add_planner_option("Gradual Planner", "A planner that gradually increases a value based on the values history", "1.0.0")

  #Add Planner Settings
  pythonDemoPlanner.add_setting("String Setting", AresDataType.STRING)
  pythonDemoPlanner.add_setting("Number Setting", AresDataType.NUMBER)
  pythonDemoPlanner.add_setting("Boolean Setting", AresDataType.BOOLEAN)
  pythonDemoPlanner.add_setting("String Array Setting", AresDataType.STRING_ARRAY)
  pythonDemoPlanner.add_setting("Constrained Strings", AresDataType.STRING_ARRAY, True, ["One", "Two", "Three"])
  pythonDemoPlanner.add_setting("Number Array Setting", AresDataType.NUMBER_ARRAY)
  pythonDemoPlanner.add_setting("Constrained Numbers", AresDataType.NUMBER_ARRAY, True, [1, 2, 3])

  #Set Planner Timeout
  pythonDemoPlanner.set_timeout(60)

  #Start Your Planner Service
  pythonDemoPlanner.start()
