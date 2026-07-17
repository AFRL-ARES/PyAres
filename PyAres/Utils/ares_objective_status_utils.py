from ..Planning.planner_models import ObjectiveStatus
from ares_datamodel.planning import plan_pb2

def python_ares_outcome_to_proto_ares_outcome(py_value: ObjectiveStatus) -> int:
  """ A method to convert from the python AresDataType class to the protobuf version """
  return py_value.value

def proto_ares_outcome_to_python_ares_outcome(proto_value: plan_pb2.ObjectiveStatus) -> ObjectiveStatus:
  """ A method to convert from the protobuf AresDataType class to the python version """
  return ObjectiveStatus(proto_value)