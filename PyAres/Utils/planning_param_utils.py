from ..Planning import PlanningParameter, PlanResponse
from ares_datamodel.planning import plan_pb2
from typing import List
from . import param_history_info_utils
from . import ares_data_type_utils
from . import ares_value_utils

def convert_python_plan_param_to_proto(param: PlanningParameter) -> plan_pb2.PlanningParameter:
  new_proto_param = plan_pb2.PlanningParameter()
  new_proto_param.parameter_name = param.name
  new_proto_param.minimum_value = param.minimum_value
  new_proto_param.maximum_value = param.maximum_value
  new_proto_param.parameter_history.extend([param_history_info_utils.convert_python_param_history_to_proto(p) for p in param.param_history])
  new_proto_param.data_type = ares_data_type_utils.python_ares_type_to_proto_ares_type(param.data_type)
  new_proto_param.is_planned = param.is_planned
  new_proto_param.is_result = param.is_result
  new_proto_param.planner_name = param.planner_name
  ares_value_utils.py_to_ares_value(param.initial_value, new_proto_param.initial_value)

  return new_proto_param 