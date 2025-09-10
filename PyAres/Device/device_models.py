from typing import Dict, Union
from ..Models import ares_data_models

class DeviceSchemaEntry:
  """ A class that describes an input or output parameter for a device command """

  def __init__(self, type: ares_data_models.AresDataType, description: str = "", unit: str = "", optional: bool = False, constraints: Union[list[int], list[float], list[str]] = []):
    """
    Initializes a new DeviceSchemaEntry

    Args:
      type ('ares_data_models.AresDataType'): An AresDataType that describes the type associated with this schema entry
      description (str): A description of the given schema entry
      unit (str): The unit associated with this schema entry
      optional (bool): A boolean value that determines whether or not this schema entry's inclusion is optional
      contraints (Union[list[int], list[float], list[str]]): An optional list of contraints to limit the number of choices available for this schema entry
    """

    self.type = type
    self.optional = optional
    self.description = description
    self.unit = unit
    self.contraints = constraints

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
