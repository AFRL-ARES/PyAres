from PyAres import AresDeviceService, DeviceCommandDescriptor, DeviceSchemaEntry, AresDataType
from typing import Dict
import time

class DemoDevice:
  # A simulated device. In reality, these communications would be happening with external hardware over serial, usb, etc.
  def __init__(self):
    self.temperature = 0.0

  def set_temperature(self, temperature: float):
    self.temperature = temperature
    time.sleep(5)
    return {}

  def get_temperature(self):
    return { "temperature": self.temperature }
  
  def get_device_state(self) -> Dict:
    state_dict = { "temperature": self.temperature }
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

  # Create the "Set Temperature" Command
  parameter_schema = DeviceSchemaEntry(AresDataType.NUMBER, "A numeric temperature value", "Degree's Celsius")
  input_schema = { "temperature": parameter_schema }
  set_temp_descriptor = DeviceCommandDescriptor("Set Temperature", "Set's the temperature of the demo device to the provided value.", input_schema, {})
  device_service.add_new_command(set_temp_descriptor, device.set_temperature)

  # Create the "Get Temperature" Command
  output_schema = {"temperature": DeviceSchemaEntry(AresDataType.NUMBER, "The current temperature of the device", "Degree's Celsius")}
  get_temp_desc = DeviceCommandDescriptor("Get Temperature", "Get's the current temperature of the demo device.", {}, output_schema)
  device_service.add_new_command(get_temp_desc, device.get_temperature)

  #Add Settings
  device_service.add_setting("Allow Negative Values", True)

  device_service.start()