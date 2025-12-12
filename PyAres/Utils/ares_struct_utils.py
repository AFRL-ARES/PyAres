from ares_datamodel import ares_struct_pb2
from typing import Union, Dict, Any

from . import ares_value_utils
import copy

def ares_struct_to_dict(ares_struct: ares_struct_pb2.AresStruct) -> Dict[str, Any]:
    """Converts an AresStruct protobuf message to a Python dictionary."""
    return {k: ares_value_utils.ares_value_to_py(v) for k, v in ares_struct.fields.items()}

def ares_string_array_to_list(string_array: ares_struct_pb2.StringArray) -> list[str]:
    """Convert an Ares String Array protobuf message to a Python list of strings."""
    return [item for item in string_array.strings]

def ares_number_array_to_list(number_array: ares_struct_pb2.NumberArray) -> Union[list[int], list[float]]:
    """Convert an Ares String Array protobuf message to a Python list of strings."""
    return [item for item in number_array.numbers]

def dict_to_ares_struct(py_dict: dict, ares_struct: ares_struct_pb2.AresStruct):
    """Converts a Python dictionary to an AresStruct protobuf message."""
    for k, v in py_dict.items():
        ares_value_utils.py_to_ares_value(v, ares_struct.fields[k])

def create_string_struct(key: str, value: str) -> ares_struct_pb2.AresStruct:
    """
    Creates a new AresStruct with a string initialized using the provided key and value.

    Args:
        key (str): The associated key to be used when storing the given value.
        value (str): The string to be stored in the new AresStruct.

    Returns:
        (AresStruct): A new AresStruct containing the provided key and value.
    """
    new_struct = ares_struct_pb2.AresStruct()
    new_struct.fields[key] = ares_value_utils.create_string(value)
    return new_struct

def create_number_struct(key: str, value: Union[int, float]) -> ares_struct_pb2.AresStruct:
    """
    Creates a new AresStruct with the provided integer or float and key.

    Args:
        key (str): The associated key to be used when storing the given value.
        value (Union[int, float]): The number to be stored in the new AresStruct.

    Returns:
        (AresStruct): A new AresStruct containing the provided key and value.
    """
    new_struct = ares_struct_pb2.AresStruct()
    new_struct.fields[key] = ares_value_utils.create_number(value)
    return new_struct

def create_bool_struct(key: str, value: bool) -> ares_struct_pb2.AresStruct:
    """
    Creates a new AresStruct with the provided bool and key.

    Args:
        key (str): The associated key to be used when storing the given value.
        value (bool): The boolean to be stored in the new AresStruct.

    Returns:
        (AresStruct): A new AresStruct containing the provided key and value.
    """
    new_struct = ares_struct_pb2.AresStruct()
    new_struct.fields[key] = ares_value_utils.create_bool(value)
    return new_struct

def create_null_struct(key: str) -> ares_struct_pb2.AresStruct:
    """
    Creates a new AresStruct with a null value initialized using the provided key.

    Args:
        key (str): The associated key to be used when storing the given value.

    Returns:
        (AresStruct): A new AresStruct containing the provided key and a null value.
    """
    new_struct = ares_struct_pb2.AresStruct()
    new_struct.fields[key] = ares_value_utils.create_null()
    return new_struct

def create_string_array_struct(key: str, value: list[str]) -> ares_struct_pb2.AresStruct:
    """
    Creates a new AresStruct with a string array initialized using the provided key and value.

    Args:
        key (str): The associated key to be used when storing the given value.
        value (list[str]): The list of strings to be stored in the new AresStruct.

    Returns:
        (AresStruct): A new AresStruct containing the provided key and value
    """
    new_struct = ares_struct_pb2.AresStruct()
    new_struct.fields[key] = ares_value_utils.create_string_array(value)
    return new_struct

def create_number_array_struct(key: str, value: list[Union[int, float]]) -> ares_struct_pb2.AresStruct:
    """
    Creates a new AresStruct with a number array initialized using the provided key and value.

    Args:
        key (str): The associated key to be used when storing the given value.
        value (Union[list[int], list[float]]): The list of integers or floats to be stored in the new AresStruct.

    Returns:
        (AresStruct): A new AresStruct containing the provided key and value
    """
    new_struct = ares_struct_pb2.AresStruct()
    new_struct.fields[key] = ares_value_utils.create_number_array(value)
    return new_struct

def create_bool_array_struct(key: str, value: list[bool]) -> ares_struct_pb2.AresStruct:
    """
    Creates a new AresStruct with a bool array initialized using the provided key and value.

    Args:
        key (str): The associated key to be used when storing the given value.
        value (list[bool]): The list of bools to be stored in the new AresStruct.

    Returns:
        (AresStruct): A new AresStruct containing the provided key and value
    """
    new_struct = ares_struct_pb2.AresStruct()
    new_struct.fields[key] = ares_value_utils.create_bool_array(value)
    return new_struct

def create_bytes_array_struct(key: str, value: bytes) -> ares_struct_pb2.AresStruct:
    """
    Creates a new AresStruct with a byte array initialized using the provided key and value.

    Args:
        key (str): The associated key to be used when storing the given value.
        value (bytes): The byte array to be stored in the new AresStruct.

    Returns:
        (AresStruct): A new AresStruct containing the provided key and value
    """
    new_struct = ares_struct_pb2.AresStruct()
    new_struct.fields[key] = ares_value_utils.create_bytes(value)
    return new_struct

def add_value_to_struct(existing_struct: ares_struct_pb2.AresStruct, key: str, new_value: ares_struct_pb2.AresValue, replace: bool = True) -> ares_struct_pb2.AresStruct:
    """
    Adds a provided value to an existing struct, with an optional bool value that determines whether any existing value should be overwritten

    Args:
        existing_struct (AresStruct): The AresStruct that the new value appended to.
        key (str): The key to be associated with the new value.
        new_value (ares_struct_pb2.AresValue): The AresValue that will be added to the provided struct.
        replace (bool): An optional boolean value that determines whether to overwrite any existing values in your struct.
    
    Returns:
        (AresStruct): The provided struct with the new value appended. 
    """
    if replace or key not in existing_struct.fields:
        new_entry = existing_struct.fields[key]
        new_entry.CopyFrom(new_value)
        
    return existing_struct

def copy_struct(existing_struct: ares_struct_pb2.AresStruct) -> ares_struct_pb2.AresStruct:
    """
    Creates a deep copy of an existing AresStruct.

    Args:
        existing_struct (AresStruct): The struct you want the contents of copied.

    Returns:
        (AresStruct): A new struct with all the items copied over.
    """
    return copy.deepcopy(existing_struct)

def create_empty_struct() -> ares_struct_pb2.AresStruct:
    """
    Creates a new empty AresStruct
    
    Returns:
        (AresStruct): The newly created empty AresStruct.
    """
    return ares_struct_pb2.AresStruct()

def create_ares_struct(key: str, value: Any):
    """
    Creates a new AresStruct using the provided key and value.

    Args:
        key (str): The key used to store the first AresValue created in this AresStruct.
        value (any): The value to be associated with the provided key.
    
    Returns:
        (AresStruct): The newly created AresStruct.
    """

    if(isinstance(value, str)):
        return create_string_struct(key, value)
    
    elif(isinstance(value, (int, float))):
        return create_number_struct(key, value)
    
    elif(isinstance(value, bool)):
        return create_bool_struct(key, value)
    
    elif(isinstance(value, bytes)):
        return create_bytes_array_struct(key, value)
    
    elif(isinstance(value, list)):
        if(len(value) == 0):
            return create_null_struct(key)

        elif(all(isinstance(item, str) for item in value)):
            return create_string_array_struct(key, value)
        
        elif(all(isinstance(item, (float, int)) for item in value)):
            return create_number_array_struct(key, value)
        
        elif(all(isinstance(item, bool) for item in value)):
            return create_bool_array_struct(key, value)
    
    else:
        return create_null_struct(key)

    

