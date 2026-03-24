from typing import Dict, Union, Optional
from ..Models import ares_data_models

class DeviceSchemaEntry:
  """ A class that describes an input or output parameter for a device command """

  def __init__(self, type: ares_data_models.AresDataType, description: str = "", unit: str = "", optional: bool = False, 
               constraints: Union[list[int], list[float], list[str]] = [],
               quantity_schema: Optional[ares_data_models.QuantitySchema] = None,
               struct_schema: Optional[Dict[str, 'DeviceSchemaEntry']] = None,
               list_element_schema: Optional['DeviceSchemaEntry'] = None,
               min_number_value: Optional[float] = None,
               max_number_value: Optional[float] = None):
    """
    Initializes a new DeviceSchemaEntry

    Args:
      type ('ares_data_models.AresDataType'): An AresDataType that describes the type associated with this schema entry
      description (str): A description of the given schema entry
      unit (str): The unit associated with this schema entry
      optional (bool): A boolean value that determines whether or not this schema entry's inclusion is optional
      constraints (Union[list[int], list[float], list[str]]): An optional list of constraints to limit the number of choices available for this schema entry
      quantity_schema (ares_data_models.QuantitySchema): Optional metadata for quantity types
      struct_schema (Dict[str, DeviceSchemaEntry]): Optional schema for struct types
      list_element_schema (DeviceSchemaEntry): Optional schema for list elements
      min_number_value (float): Optional minimum value for numeric types
      max_number_value (float): Optional maximum value for numeric types
    """

    self.type = type
    self.optional = optional
    self.description = description
    self.unit = unit
    self.constraints = constraints
    self.quantity_schema = quantity_schema
    self.struct_schema = struct_schema
    self.list_element_schema = list_element_schema
    self.min_number_value = min_number_value
    self.max_number_value = max_number_value

class DeviceCommandDescriptor:
  """ A class that contains all the necessary information to describe a device command """
  def __init__(self, name: str, description: str, input_schema: Dict[str, DeviceSchemaEntry], output_schema: Dict[str, DeviceSchemaEntry]):
    """
    Initializes a new instance of the device command descriptor class.

    Args:
      name (str): The name of this device command.
      description (str): The description of this device command.
      input_schema (list[ares_data_models.AresDataType]): A dictionary that defines the input parameters to the device command.
      output_schema (list[ares_data_models.AresDataType]): A dictionary that defines the output parameters to the device command.
    """
    self.name = name
    self.description = description
    self.input_schema = input_schema
    self.output_schema = output_schema
