from typing import Union
from ares_datamodel import ares_data_schema_pb2
from ..Models import ares_data_models

def create_settings_schema_entry(
    setting_type: ares_data_models.AresDataType, 
    optional: bool, 
    choices: Union[list[str], list[int], list[float]]) -> ares_data_schema_pb2.SchemaEntry:
    """
    Takes in an AresSetting object and converts it into the protobuf SchemaEntry message.

    Args:
        new_setting: The AresSetting object that provides all the details around the setting implementation.

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
            

    return schema_entry

