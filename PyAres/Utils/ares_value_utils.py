from ares_datamodel import ares_struct_pb2
from ares_datamodel import ares_data_type_pb2
from datetime import datetime, timezone
from google.protobuf import timestamp_pb2
from typing import Union, Any, Dict

from . import ares_data_type_utils
from ..Models import AresDataType, Quantity

def ares_value_to_py(ares_value: ares_struct_pb2.AresValue):
    """Converts an AresValue protobuf message to a Python native type."""
    field = ares_value.WhichOneof("kind")
    if field == "null_value":
        return None
    elif field == "number_value":
        return ares_value.number_value
    elif field == "timestamp_value":
        return ares_value.timestamp_value.ToDatetime(tzinfo=timezone.utc)
    elif field == "float_value":
        return ares_value.float_value
    elif field == "int_value":
        return ares_value.int_value
    elif field == "string_value":
        return ares_value.string_value
    elif field == "bool_value":
        return ares_value.bool_value
    elif field == "string_array_value":
        return list(ares_value.string_array_value.strings)
    elif field == "number_array_value":
        return list(ares_value.number_array_value.numbers)
    elif field == "bytes_value":
        return ares_value.bytes_value
    elif field == "list_value":
        return [ares_value_to_py(v) for v in ares_value.list_value.values]
    elif field == "struct_value":
        return {k: ares_value_to_py(v) for k, v in ares_value.struct_value.fields.items()}
    elif field == "quantity_value":
        return Quantity(scalar=ares_value.quantity_value.scalar, 
                        type=ares_value.quantity_value.type, 
                        unit=ares_value.quantity_value.unit)
    return None

def py_to_ares_value(py_value, ares_value: ares_struct_pb2.AresValue):
    """Sets the appropriate field in an AresValue protobuf message from a Python native type."""
    if isinstance(py_value, str):
        ares_value.string_value = py_value
    elif isinstance(py_value, bool):
        ares_value.bool_value = py_value
    elif isinstance(py_value, (int, float)):
        ares_value.number_value = py_value
    elif isinstance(py_value, (datetime, timestamp_pb2.Timestamp)):
        ares_value.timestamp_value.CopyFrom(_to_timestamp(py_value))
    elif isinstance(py_value, bytes):
        ares_value.bytes_value = py_value
    elif isinstance(py_value, Quantity):
        ares_value.quantity_value.scalar = py_value.scalar
        ares_value.quantity_value.type = py_value.type
        ares_value.quantity_value.unit = py_value.unit
    elif isinstance(py_value, dict):
        for k, v in py_value.items():
            py_to_ares_value(v, ares_value.struct_value.fields[k])
    elif isinstance(py_value, list):
        if(all(isinstance(x, str) for x in py_value)):
            ares_value.string_array_value.strings.extend(py_value)
        elif(all(isinstance(x, bool) for x in py_value)):
            for item in py_value:
                ares_value.list_value.values.append(create_ares_value(item))
        elif(all(isinstance(x, (int, float)) for x in py_value)):
            ares_value.number_array_value.numbers.extend(py_value)
        else:
            for item in py_value:
                ares_value.list_value.values.append(create_ares_value(item))

    elif py_value == None:
        ares_value.null_value = ares_struct_pb2.NullValue.NULL_VALUE

    else:
        raise TypeError(f"Unsupported type for AresValue: {type(py_value)}")

def create_quantity(value: Quantity) -> ares_struct_pb2.AresValue:
    """ Creates a new AresValue, initialized to the provided Quantity. """
    ares_val = ares_struct_pb2.AresValue()
    ares_val.quantity_value.scalar = value.scalar
    ares_val.quantity_value.type = value.type
    ares_val.quantity_value.unit = value.unit
    return ares_val

def create_number(value: Union[int, float]) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided number value.

    Args:
        value (Union[int, float]): The integer or float to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided number value.
    """
    return ares_struct_pb2.AresValue(number_value=value)

def _to_timestamp(value: Union[datetime, timestamp_pb2.Timestamp]) -> timestamp_pb2.Timestamp:
    if isinstance(value, timestamp_pb2.Timestamp):
        return value

    timestamp = timestamp_pb2.Timestamp()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    timestamp.FromDatetime(value.astimezone(timezone.utc))
    return timestamp

def create_timestamp(value: Union[datetime, timestamp_pb2.Timestamp]) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided timestamp value.

    Args:
        value (Union[datetime, Timestamp]): The timestamp to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided timestamp value.
    """
    return ares_struct_pb2.AresValue(timestamp_value=_to_timestamp(value))

def create_float(value: float) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided float value.

    Args:
        value (float): The double-backed float to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided float value.
    """
    return ares_struct_pb2.AresValue(float_value=float(value))

def create_int(value: int) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided int value.

    Args:
        value (int): The integer to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided int value.
    """
    return ares_struct_pb2.AresValue(int_value=int(value))

def create_string(value: str) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided string value.

    Args:
        value (str): The string to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided string value.
    """
    return ares_struct_pb2.AresValue(string_value=value)

def create_number_array(value: list[Union[int, float]]) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided list of numbers.

    Args:
        value (list[Union[int, float]]): The list of numbers to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided list of numbers.
    """
    num_array = ares_struct_pb2.NumberArray(numbers=value)
    return ares_struct_pb2.AresValue(number_array_value=num_array)

def create_string_array(value: list[str]) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided list of strings.

    Args:
        value (list[str]): The list of strings to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided list of strings.
    """
    str_array = ares_struct_pb2.StringArray(strings=value)
    return ares_struct_pb2.AresValue(string_array_value=str_array)

def create_null() -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to a null value.

    Returns:
        (AresValue): A new AresValue containing a null value.
    """
    return ares_struct_pb2.AresValue(null_value=ares_struct_pb2.NullValue.NULL_VALUE)

def create_bool(value: bool) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided boolean value.

    Args:
        value (bool): The boolean to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided boolean value.
    """
    return ares_struct_pb2.AresValue(bool_value=value)

def create_bytes(value: bytes) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided bytes value.

    Args:
        value (bytes): The bytes to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided bytes value.
    """
    return ares_struct_pb2.AresValue(bytes_value=value)

def create_array(values: list[Any]) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided list of AresValues.

    Args:
        value (list[Any]): The list of values to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided list of values.
    """
    ares_value = ares_struct_pb2.AresValue()
    for item in values:
        ares_value.list_value.values.append(create_ares_value(item))

    return ares_value

def create_struct(values: Dict) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized with an AresStruct.

    Args:
        value (Dict): The dictionary of values to be added to the AresStruct.

    Returns:
        (AresValue): A new AresValue containing the provided dictionaries values in an AresStruct.
    """
    ares_value = ares_struct_pb2.AresValue()

    for key, value in values.items():
        new_entry = ares_value.struct_value.fields[key]
        new_entry.CopyFrom(create_ares_value(value))
 

    return ares_value

def create_default(python_datatype: AresDataType) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue with a default value for the given AresDataType.

    Args:
        dataType (ares_data_type_pb2.AresDataType): The data type for which to create a default value.

    Returns:
        (AresValue): A new AresValue containing the default value.
    """
    dataType = ares_data_type_utils.python_ares_type_to_proto_ares_type(python_datatype)

    if(dataType == ares_data_type_pb2.AresDataType.NULL):
        return create_null()
    
    elif(dataType == ares_data_type_pb2.AresDataType.NUMBER):
        return create_number(0)
    elif(dataType == ares_data_type_pb2.AresDataType.TIMESTAMP):
        return create_timestamp(datetime.fromtimestamp(0, tz=timezone.utc))
    elif(dataType == ares_data_type_pb2.AresDataType.FLOAT):
        return create_float(0.0)
    elif(dataType == ares_data_type_pb2.AresDataType.INT):
        return create_int(0)
    
    elif(dataType == ares_data_type_pb2.AresDataType.STRING):
        return create_string("")
    
    elif(dataType == ares_data_type_pb2.AresDataType.BOOLEAN):
        return create_bool(False)
    
    elif(dataType == ares_data_type_pb2.AresDataType.STRING_ARRAY):
        return create_string_array([])
    
    elif(dataType == ares_data_type_pb2.AresDataType.NUMBER_ARRAY):
        return create_number_array([])
    
    elif(dataType == ares_data_type_pb2.AresDataType.LIST):
        return create_array([])
    
    elif(dataType == ares_data_type_pb2.AresDataType.BYTE_ARRAY):
        return create_bytes(bytes())
    
    elif(dataType == ares_data_type_pb2.AresDataType.STRUCT):
        return create_struct({})
    elif(dataType == ares_data_type_pb2.AresDataType.QUANTITY):
        return create_quantity(Quantity(0, 0, ""))
    else:
        return create_null()
    
def create_ares_value(value: Any) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue using the provided value.
    If the provided value is not valid for use in an AresValue, a null AresValue is returned.

    Args:
        value (any): An any that is stored in the newly created AresValue.

    Returns:
        (AresValue): A new AresValue with the provided value stored.
    """
    if(isinstance(value, str)):
        return create_string(value)

    elif(isinstance(value, bool)):
        return create_bool(value)

    elif(isinstance(value, (int, float))):
        return create_number(value)

    elif(isinstance(value, (datetime, timestamp_pb2.Timestamp))):
        return create_timestamp(value)

    elif(isinstance(value, bytes)):
        return create_bytes(value)

    elif(isinstance(value, Quantity)):
        return create_quantity(value)
    
    elif(isinstance(value, list)):
        if all(isinstance(x, bool) for x in value):
            return create_array(value)
        
        elif all(isinstance(x, (int, float)) for x in value):
            return create_number_array(value)
        
        elif all(isinstance(x, str) for x in value):
            return create_string_array(value)
        
        else:
            return create_array(value)
        
    elif(isinstance(value, dict)):
        return create_struct(value)
        
    else:
        return create_null()
