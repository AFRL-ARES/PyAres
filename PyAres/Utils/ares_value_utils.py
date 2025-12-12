from ares_datamodel import ares_struct_pb2
from ares_datamodel import ares_data_type_pb2
from typing import Union, Any

from . import ares_data_type_utils
from ..Models import AresDataType 

def ares_value_to_py(ares_value: ares_struct_pb2.AresValue):
    """Converts an AresValue protobuf message to a Python native type."""
    type_map = {
        "null_value": None,
        "number_value": ares_value.number_value,
        "string_value": ares_value.string_value,
        "bool_value": ares_value.bool_value,
        "string_array_value": ares_value.string_array_value.strings,
        "number_array_value": ares_value.number_array_value.numbers,
        "bytes_value": ares_value.bytes_value
    }
    
    field = ares_value.WhichOneof("kind")
    if field in type_map:
        return type_map[field]
    return None

def py_to_ares_value(py_value, ares_value: ares_struct_pb2.AresValue):
    """Sets the appropriate field in an AresValue protobuf message from a Python native type."""
    if isinstance(py_value, str):
        ares_value.string_value = py_value
    elif isinstance(py_value, bool):
        ares_value.bool_value = py_value
    elif isinstance(py_value, (int, float)):
        ares_value.number_value = py_value
    elif isinstance(py_value, bytes):
        ares_value.bytes_value = py_value
    elif isinstance(py_value, list):
        if(all(isinstance(x, str) for x in py_value)):
            ares_value.string_array_value.strings.extend(py_value)
        elif(all(isinstance(x, (int, float)) for x in py_value)):
            ares_value.number_array_value.numbers.extend(py_value)
        elif(all(isinstance(x, bool) for x in py_value)):
            ares_value.bool_array_value.bools.extend(py_value)
    else:
        raise TypeError(f"Unsupported type for AresValue: {type(py_value)}")

def create_number(value: Union[int, float]) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided number value.

    Args:
        value (Union[int, float]): The integer or float to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided number value.
    """
    return ares_struct_pb2.AresValue(number_value=value)

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

def create_bool_array(value: list[bool]) -> ares_struct_pb2.AresValue:
    """
    Creates a new AresValue, initialized to the provided list of booleans.

    Args:
        value (list[bool]): The list of booleans to be stored in the new AresValue.

    Returns:
        (AresValue): A new AresValue containing the provided list of booleans.
    """
    ares_value = ares_struct_pb2.AresValue()
    ares_value.bool_array_value.bools.extend(value)
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
    
    elif(dataType == ares_data_type_pb2.AresDataType.STRING):
        return create_string("")
    
    elif(dataType == ares_data_type_pb2.AresDataType.BOOLEAN):
        return create_bool(False)
    
    elif(dataType == ares_data_type_pb2.AresDataType.STRING_ARRAY):
        return create_string_array([])
    
    elif(dataType == ares_data_type_pb2.AresDataType.NUMBER_ARRAY):
        return create_number_array([])
    
    elif(dataType == ares_data_type_pb2.AresDataType.BOOL_ARRAY):
        return create_bool_array([])
    
    elif(dataType == ares_data_type_pb2.AresDataType.BYTE_ARRAY):
        return create_bytes(bytes())
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
    
    elif(isinstance(value, (int, float))):
        return create_number(value)
    
    elif(isinstance(value, bool)):
        return create_bool(value)
    
    elif(isinstance(value, bytes)):
        return create_bytes(value)
    
    elif(isinstance(value, list)):
        if all(isinstance(x, (int, float)) for x in value):
            return create_number_array(value)
        
        elif all(isinstance(x, str) for x in value):
            return create_string_array(value)
        
        elif all(isinstance(x, bool) for x in value):
            return create_bool_array(value)
        
        else:
            return create_null()
        
    else:
        return create_null()