from ..Models import Outcome
from ares_datamodel import ares_outcome_enum_pb2
from typing import cast

def python_ares_outcome_to_proto_ares_outcome(py_value: Outcome) -> ares_outcome_enum_pb2.Outcome:
  """ A method to convert from the python AresDataType class to the protobuf version """
  val = cast(ares_outcome_enum_pb2.Outcome, py_value.value)
  return val

def proto_ares_outcome_to_python_ares_outcome(proto_value: ares_outcome_enum_pb2.Outcome) -> Outcome:
  """ A method to convert from the protobuf AresDataType class to the python version """
  return Outcome(proto_value)