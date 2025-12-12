from ares_datamodel.planning import plan_pb2
from ..Planning import PlanResponse
from . import ares_outcome_utils

def proto_plan_response_to_python(proto_response: plan_pb2.PlanningResponse) -> PlanResponse:
  param_names = []
  param_values = []

  for param in proto_response.planned_parameters:
    param_names.append(param.parameter_name)
    param_values.append(param.parameter_value)

  python_response = PlanResponse(param_names, param_values)
  python_response.outcome = ares_outcome_utils.proto_ares_outcome_to_python_ares_outcome(proto_response.planning_outcome)
  python_response.error_string = proto_response.error_string
  return python_response
