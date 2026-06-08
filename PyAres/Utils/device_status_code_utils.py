from ..Device import StatusCode
from ares_datamodel import command_status_code_pb2
from typing import cast

def python_status_code_to_proto_status_code(py_value: StatusCode) -> command_status_code_pb2.CommandStatusCode:
  """ A method to convert from the python AresDataType class to the protobuf version """
  val = cast( command_status_code_pb2.CommandStatusCode, py_value.value)
  return val

def proto_status_code_to_python_status_code(proto_value:  command_status_code_pb2.CommandStatusCode) -> StatusCode:
  """ A method to convert from the protobuf AresDataType class to the python version """
  return StatusCode(proto_value)

def determine_success(code: StatusCode) -> bool:
  if code == StatusCode.COMMAND_SUCCESS or code == StatusCode.SUCCESS_WITH_WARNGINGS:
    return True
  
  else:
    return False