from ..Device.device_models import WidgetType
from ares_datamodel.device import ares_ui_widget_enum_pb2

def python_ares_outcome_to_proto_ares_outcome(py_value: WidgetType) -> int:
  """ A method to convert from the python AresDataType class to the protobuf version """
  return py_value.value

def proto_ares_outcome_to_python_ares_outcome(proto_value: ares_ui_widget_enum_pb2.WidgetType) -> WidgetType:
  """ A method to convert from the protobuf AresDataType class to the python version """
  return WidgetType(proto_value)