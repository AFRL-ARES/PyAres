from ares_datamodel.planning import plan_pb2
from ..Planning import PlanRequest
from . import planning_param_utils
from . import ares_struct_utils

def python_plan_request_to_proto(request: PlanRequest) -> plan_pb2.PlanningRequest:
  proto_request = plan_pb2.PlanningRequest()
  proto_request.analysis_results.extend(request.analysis_results)
  ares_struct_utils.dict_to_ares_struct(request.settings, proto_request.adapter_settings)
  proto_request.planning_parameters.extend([planning_param_utils.convert_python_plan_param_to_proto(p) for p in request.parameters]) 
  return proto_request