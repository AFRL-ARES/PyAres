from typing import Union, Dict, Optional, List, Any
from ares_datamodel import ares_data_schema_pb2, ares_struct_pb2
from ..Models import ares_data_models
from ..Models.ares_data_models import AresSchemaEntry, Limits


def convert_ares_schema_entry_to_proto(entry: AresSchemaEntry) -> ares_data_schema_pb2.AresValueSchema:
    proto_entry = create_settings_schema_entry(
        setting_type=entry.type,
        optional=entry.optional,
        choices=entry.choices,
        struct_schema=entry.struct_schema,
    )
    proto_entry.description = entry.description
    
    if entry.quantity_schema:
        proto_entry.quantity_schema.quantity_type = entry.quantity_schema.quantity_type
        proto_entry.quantity_schema.bounds_unit = entry.quantity_schema.bounds_unit
        if entry.quantity_schema.min_scalar_value is not None:
            proto_entry.quantity_schema.min_scalar_value = entry.quantity_schema.min_scalar_value
        if entry.quantity_schema.max_scalar_value is not None:
            proto_entry.quantity_schema.max_scalar_value = entry.quantity_schema.max_scalar_value

    if entry.list_element_schema:
        proto_entry.list_element_schema.CopyFrom(
            convert_ares_schema_entry_to_proto(entry.list_element_schema)
        )

    if entry.min_number_value is not None:
        proto_entry.min_number_value = entry.min_number_value

    if entry.max_number_value is not None:
        proto_entry.max_number_value = entry.max_number_value

    return proto_entry


def create_settings_schema_entry(
    setting_type: ares_data_models.AresDataType,
    optional: bool,
    default_value: Any = None,
    choices: Union[List[str], List[int], List[float]] | None = None,
    struct_schema: Optional[Dict[str, AresSchemaEntry]] = None,
    list_element_schema: Optional[AresSchemaEntry] = None,
    limits: Optional[Limits] = None,
    description: Optional[str] = None,
) -> ares_data_schema_pb2.AresValueSchema:
    """Creates a protobuf AresValueSchema message from the provided setting details.

    Args:
        setting_type (AresDataType): The data type of the setting.
        optional (bool): Whether the setting is optional.
        choices (Union[list[str], list[int], list[float]]): A list of valid choices for the setting.
        struct_schema (Optional[Dict[str, AresSchemaEntry]]): Nested schema definition for STRUCT types.
        list_element_schema (Optional[AresSchemaEntry]): Schema definition for elements of a LIST type.

    Returns:
        AresValueSchema: A new AresValueSchema message.
    """
    schema_entry = ares_data_schema_pb2.AresValueSchema()
    schema_entry.type = setting_type.value
    schema_entry.optional = optional

    if isinstance(choices, list) and len(choices) > 0:
        if all(isinstance(item, str) for item in choices):
            schema_entry.string_choices.strings.extend(choices)
        elif all(isinstance(item, (int, float)) for item in choices):
            schema_entry.number_choices.numbers.extend(choices)

    if struct_schema is not None:
        for key, value in struct_schema.items():
            schema_entry.struct_schema.fields[key].CopyFrom(
                convert_ares_schema_entry_to_proto(value)
            )

    if list_element_schema is not None:
        schema_entry.list_element_schema.CopyFrom(
            convert_ares_schema_entry_to_proto(list_element_schema)
        )

    if limits is not None:
        schema_entry.limits.minimum = limits.minimum
        schema_entry.limits.maximum = limits.maximum

    if description is not None:
        schema_entry.description = description

    if isinstance(default_value, ares_struct_pb2.AresValue):
        schema_entry.default_value.CopyFrom(default_value)

    return schema_entry
