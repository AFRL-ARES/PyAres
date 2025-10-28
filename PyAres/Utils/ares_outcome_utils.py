from ..Models import Outcome
from ares_datamodel import ares_outcome_enum_pb2

def python_ares_outcome_to_proto_ares_outcome(py_value: Outcome) -> ares_outcome_enum_pb2.Outcome:
  """ A method to convert from the python AresDataType class to the protobuf version """
  return py_value.value

def proto_ares_outcome_to_python_ares_outcome(proto_value: ares_outcome_enum_pb2.Outcome) -> Outcome:
  """ A method to convert from the protobuf AresDataType class to the python version """
  return Outcome(proto_value)