from ares_datamodel import ares_data_type_pb2
from ..Models import ares_data_models

def python_ares_type_to_proto_ares_type(py_value: ares_data_models.AresDataType) -> ares_data_type_pb2.AresDataType:
  """ A method to convert from the python AresDataType class to the protobuf version """
  return py_value.value

def proto_ares_type_to_python_ares_type(proto_value: ares_data_type_pb2.AresDataType) -> ares_data_models.AresDataType:
  """ A method to convert from the protobuf AresDataType class to the python version """
  return ares_data_models.AresDataType(proto_value)