from ..Device import StatusCode
from ares_datamodel import command_status_code_pb2
from typing import cast

def python_status_code_to_proto_status_code(py_value: StatusCode) -> int:
  """ A method to convert from the python StatusCode enum class to the protobuf version """
  return py_value.value

def proto_status_code_to_python_status_code(proto_value:  command_status_code_pb2.CommandStatusCode) -> StatusCode:
  """ A method to convert from the protobuf StatusCode enum class to the python version """
  return StatusCode(proto_value)

def determine_success(code: StatusCode) -> bool:
  if code == StatusCode.COMMAND_SUCCESS or code == StatusCode.SUCCESS_WITH_WARNGINGS:
    return True
  
  else:
    return False