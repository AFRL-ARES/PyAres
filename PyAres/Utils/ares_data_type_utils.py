from typing import Union, cast
from ares_datamodel import ares_data_type_pb2
from ..Models import AresDataType

def python_ares_type_to_proto_ares_type(py_value: AresDataType) -> ares_data_type_pb2.AresDataType:
  """ A method to convert from the python AresDataType class to the protobuf version """
  val = cast(ares_data_type_pb2.AresDataType, py_value.value)
  return val

def proto_ares_type_to_python_ares_type(proto_value: ares_data_type_pb2.AresDataType) -> AresDataType:
  """ A method to convert from the protobuf AresDataType class to the python version """
  return AresDataType(proto_value)

def determine_python_ares_data_type(value: Union[int, float, str, bool, list]):
  """ A method that takes in a value and returns the corresponding `PyAres.Models.AresDataType`"""
  match value:
    case str():
      return AresDataType.STRING
    case bool():
      return AresDataType.BOOLEAN
    case int():
      return AresDataType.NUMBER
    case float():
      return AresDataType.NUMBER
    case list():
      if(all(isinstance(x, bool) for x in value)):
        return AresDataType.LIST
      elif(all(isinstance(x, str) for x in value)):
        return AresDataType.STRING_ARRAY
      elif(all(isinstance(x, (int, float)) for x in value)):
        return AresDataType.NUMBER_ARRAY
      else:
        return AresDataType.LIST
    case _:
      return AresDataType.UNKNOWN
