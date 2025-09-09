import time

from PyAres import AresDeviceService
from PyAres import DeviceCommandDescriptor
from PyAres import DeviceSchemaEntry
from PyAres import AresDataType

class DemoDevice:
  # A simulated device. In reality, these communications would be happening with external hardware over serial, usb, etc.
  def __init__(self):
    self.temperature = 0.0
    self.current_pillar_number = 1
    self.current_growth = 0.0

  def set_temperature(self, temperature: float):
    self.temperature = temperature
    print("Temperature is being set!")
    time.sleep(5)
    return {}

  def get_temperature(self):
    return self.temperature

  def move_to_next_pillar(self):
    self.current_pillar_number += 1
    self.current_growth - 0.0
    time.sleep(5)

  def get_current_growth(self):
    return self.current_growth
  
  def get_device_state(self):
    state_dict = {}
    state_dict["temperature"] = self.temperature
    state_dict["growth"] = self.current_growth
    return state_dict
  
  def enter_safe_mode(self):
    self.temperature = 0

device = DemoDevice()

if __name__ == "__main__":
  # Basic information about my device
  device_name = "Demo Device"
  description = "A device to demonstrate the PyAres device capabilities"
  version = "1.0.0"
  device_service = AresDeviceService(device.enter_safe_mode, device.get_device_state, device_name, description, version)

  #Create Command Descriptor, then add command
  parameter_schema = DeviceSchemaEntry(AresDataType.NUMBER, False, "A numeric temperature value", "Degree's Celsius")
  input_schema = { "temperature": parameter_schema }
  descriptor = DeviceCommandDescriptor("Set Temperature", "Set's the temperature of the demo device to the provided value.", input_schema, {})
  device_service.add_new_command(descriptor, device.set_temperature)

  #Add Test Settings
  device_service.add_setting("String Setting", AresDataType.STRING)
  device_service.add_setting("Number Setting", AresDataType.NUMBER)
  device_service.add_setting("Boolean Setting", AresDataType.BOOLEAN)
  device_service.add_setting("Number Array Setting", AresDataType.NUMBER_ARRAY)
  device_service.add_setting("String Array Setting", AresDataType.STRING_ARRAY)
  device_service.add_setting("Constrained Strings", AresDataType.STRING, True, ["StringOne", "StringTwo", "StringThree"])
  device_service.add_setting("Constrained Numbers", AresDataType.NUMBER, True, [1, 2, 3])

  device_service.start()