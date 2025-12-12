from ..Planning import ParameterHistoryItem
from ares_datamodel.planning import plan_pb2
from . import ares_value_utils

def convert_proto_param_history_to_python(proto: plan_pb2.ParameterHistoryInfo) -> ParameterHistoryItem:
  return ParameterHistoryItem(proto.planned_value, proto.achieved_value)

def convert_python_param_history_to_proto(python: ParameterHistoryItem) -> plan_pb2.ParameterHistoryInfo:
  info = plan_pb2.ParameterHistoryInfo(planned_value=ares_value_utils.create_ares_value(python.planned_value), achieved_value=ares_value_utils.create_ares_value(python.achieved_value))
  return info
