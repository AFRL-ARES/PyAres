from typing import Union

from ..Device import DeviceCommandDescriptor
from ..Device import DeviceSchemaEntry
from ares_datamodel.device import device_command_descriptor_pb2
from ares_datamodel import ares_data_schema_pb2

from . import ares_data_type_utils

def python_command_description_to_proto(python_description: DeviceCommandDescriptor) -> device_command_descriptor_pb2.DeviceCommandDescriptor:
  proto_description = device_command_descriptor_pb2.DeviceCommandDescriptor()
  
  # Update input_schema (AresStructSchema)
  for key, value in python_description.input_schema.items():
    proto_description.input_schema.fields[key].CopyFrom(python_device_schema_entry_to_proto(value))

  # Update output_schema (AresValueSchema)
  # If there is only one output and the key is empty or "output", we can use it directly.
  # Otherwise, if there are multiple outputs, we should probably wrap them in a struct.
  # However, the proto says output_schema is a single AresValueSchema.
  # For now, let's assume we use the first one if there's only one, or wrap in a struct if there are multiple.
  if len(python_description.output_schema) == 1:
    first_val = list(python_description.output_schema.values())[0]
    proto_description.output_schema.CopyFrom(python_device_schema_entry_to_proto(first_val))
  elif len(python_description.output_schema) > 1:
    proto_description.output_schema.type = ares_data_schema_pb2.AresDataType.STRUCT
    for key, value in python_description.output_schema.items():
      proto_description.output_schema.struct_schema.fields[key].CopyFrom(python_device_schema_entry_to_proto(value))

  proto_description.name = python_description.name
  proto_description.description = python_description.description

  return proto_description


def python_device_schema_entry_to_proto(entry: DeviceSchemaEntry) -> ares_data_schema_pb2.AresValueSchema:
  proto_schema = ares_data_schema_pb2.AresValueSchema()
  proto_schema.type = ares_data_type_utils.python_ares_type_to_proto_ares_type(entry.type)
  proto_schema.optional = entry.optional
  proto_schema.description = entry.description
  
  if entry.constraints:
    if all(isinstance(x, (int, float)) for x in entry.constraints):
      proto_schema.number_choices.numbers.extend(entry.constraints)
    elif all(isinstance(x, str) for x in entry.constraints):
      proto_schema.string_choices.strings.extend(entry.constraints)

  if entry.quantity_schema:
    proto_schema.quantity_schema.quantity_type = entry.quantity_schema.quantity_type
    proto_schema.quantity_schema.bounds_unit = entry.quantity_schema.bounds_unit
    if entry.quantity_schema.min_scalar_value is not None:
      proto_schema.quantity_schema.min_scalar_value = entry.quantity_schema.min_scalar_value
    if entry.quantity_schema.max_scalar_value is not None:
      proto_schema.quantity_schema.max_scalar_value = entry.quantity_schema.max_scalar_value

  if entry.struct_schema:
    for key, sub_entry in entry.struct_schema.items():
      proto_schema.struct_schema.fields[key].CopyFrom(python_device_schema_entry_to_proto(sub_entry))

  if entry.list_element_schema:
    proto_schema.list_element_schema.CopyFrom(python_device_schema_entry_to_proto(entry.list_element_schema))

  if entry.min_number_value is not None:
    proto_schema.min_number_value = entry.min_number_value
  if entry.max_number_value is not None:
    proto_schema.max_number_value = entry.max_number_value

  return proto_schema