from typing import Union

from ..Device import DeviceCommandDescriptor
from ..Device import DeviceSchemaEntry
from ares_datamodel.device import device_command_descriptor_pb2
from ares_datamodel import ares_data_schema_pb2

from . import ares_data_type_utils

def python_command_description_to_proto(python_description: DeviceCommandDescriptor) -> device_command_descriptor_pb2.DeviceCommandDescriptor:
  proto_description = device_command_descriptor_pb2.DeviceCommandDescriptor()
  
  #First, we need to transform our Python DeviceSchemaEntry classes into the protobuf equivalent. Then add them to our new proto message
  transformed_input_schema = {key: python_device_schema_entry_to_proto(value) for key, value in python_description.input_schema.items()}
  for key, value in transformed_input_schema.items():
    new_entry: ares_data_schema_pb2.SchemaEntry = proto_description.input_schema.fields[key]
    new_entry.CopyFrom(value)

  transformed_output_schema = {key: python_device_schema_entry_to_proto(value) for key, value in python_description.output_schema.items()}
  for key, value in transformed_output_schema.items():
    new_entry: ares_data_schema_pb2.SchemaEntry = proto_description.output_schema.fields[key]
    new_entry.CopyFrom(value)

  proto_description.name = python_description.name
  proto_description.description = python_description.description

  return proto_description


def python_device_schema_entry_to_proto(entry: DeviceSchemaEntry) -> ares_data_schema_pb2.SchemaEntry:
  proto_schema = ares_data_schema_pb2.SchemaEntry()
  proto_schema.type = ares_data_type_utils.python_ares_type_to_proto_ares_type(entry.type)
  proto_schema.optional = entry.optional
  proto_schema.description = entry.description
  proto_schema.unit = entry.unit
  
  if all(isinstance(x, (int, float)) for x in entry.contraints):
    proto_schema.number_choices.numbers.extend(entry.contraints)

  elif all(isinstance(x, str) for x in entry.contraints):
    proto_schema.string_choices.strings.extend(entry.contraints)

  return proto_schema