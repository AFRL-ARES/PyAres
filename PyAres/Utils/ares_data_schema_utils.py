from typing import Union, Dict, Optional, List
from ares_datamodel import ares_data_schema_pb2
from ..Models import ares_data_models
from ..Models.ares_data_models import AresSchemaEntry

def convert_ares_schema_entry_to_proto(entry: AresSchemaEntry) -> ares_data_schema_pb2.SchemaEntry:
    proto_entry = create_settings_schema_entry(entry.type, entry.optional, entry.choices, entry.struct_schema)
    proto_entry.description = entry.description
    proto_entry.unit = entry.unit
    return proto_entry

def create_settings_schema_entry(
    setting_type: ares_data_models.AresDataType, 
    optional: bool, 
    choices: Union[list[str], list[int], list[float]],
    struct_schema: Optional[Dict[str, AresSchemaEntry]] = None) -> ares_data_schema_pb2.SchemaEntry:
    """
    Creates a protobuf SchemaEntry message from the provided setting details.

    Args:
        setting_type (AresDataType): The data type of the setting.
        optional (bool): Whether the setting is optional.
        choices (Union[list[str], list[int], list[float]]): A list of valid choices for the setting.
        struct_schema (Optional[Dict[str, AresSchemaEntry]]): Nested schema definition for STRUCT types.

    Returns:
        (SchemaEntry): A new SchemaEntry message.
    """

    if(isinstance(choices, list)):
        if(len(choices) == 0):
            schema_entry = ares_data_schema_pb2.SchemaEntry(type=setting_type.value, optional=optional)

        elif(all(isinstance(item, str) for item in choices)):
            schema_entry = ares_data_schema_pb2.SchemaEntry(type=setting_type.value, optional=optional)
            schema_entry.string_choices.strings.extend(choices)
    
        elif(all(isinstance(item, (int, float)) for item in choices)):
            schema_entry = ares_data_schema_pb2.SchemaEntry(type=setting_type.value, optional=optional)
            schema_entry.number_choices.numbers.extend(choices)

        else:
            schema_entry = ares_data_schema_pb2.SchemaEntry(type=setting_type.value, optional=optional)
            
    if struct_schema is not None:
        for key, value in struct_schema.items():
            schema_entry.struct_schema.fields[key].CopyFrom(convert_ares_schema_entry_to_proto(value))

    return schema_entry
