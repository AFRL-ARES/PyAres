# PyAres
The PyAres library is designed to provide support for building planners, analyzers and devices as part of your ARES self driving labratory. PyAres leverages the power of protobuf and gRPC to communicate with your ARES system while providing a simple Pythonic API. 

### ✨ Features
* A Pythonic API built on the performance of Protobuf and gRPC to streamline the creation of self-driving lab components
* Easily define custom decision-making processes with your own PyAres Planners
* Integrate custom data processing and intepretation workflows with PyAres Analyzers
* Connect and control new hardware, making your implementations ARES ready as a PyAres Device

### 🏗️ Installation

PyAres can be installed using pip:
```console
pip install PyAres
```

### 🧠  Planner Usage

Planners can be initialized using the AresPlannerService class. Below is a basic example of setting up a planner.

``` Python
from PyAres import AresPlannerService
from PyAres import PlanRequest
from PyAres import PlanResponse
from PyAres import AresDataType

import random

def plan(request: PlanRequest) -> PlanResponse:
    #This is where your custom planning logic goes
    planned_values = []
    names = []

    for param in request.parameters:
        planned_values.append(random.uniform(param.minimum_value, param.maximum_value))
        names.append(param.name)

    return PlanResponse(parameter_names=names, parameter_values=planned_values)


if __name__ == "__main__":
    #Basic details about your planner
    name = "Demo Planner"
    version = "1.0.0"
    description = "This is a test planner to demonstrate working with PyAres to create planners!"
    pythonDemoPlanner = AresPlannerService(plan, name, description, version)

    #Add Supported Types
    pythonDemoPlanner.add_supported_type(AresDataType.NUMBER)
```
This example creates a simple planner called "Demo Planner", that supports planning for numeric values. The 'plan' method shown here is where our custom planning logic lives. For this example, we generate a random number between the minimum and maximum value of each provided parameter.

### 🔍 Analyzer Usage

Analyzers can be initialized using the AresAnalyzerService class. Below is a basic example of setting up an analyzer.

```Python
from PyAres import AresAnalyzerService
from PyAres import AnalysisRequest
from PyAres import Analysis
from PyAres import AresDataType

def analyze(request: AnalysisRequest) -> Analysis:
    #Custom Analysis Logic
    growth = request.inputs.get("Growth")
    temperature = request.inputs.get("Temperature")

    print(f"Growth: {growth}")
    print(f"Temperature: {temperature}")

    analysis = Analysis(result=growth, success=True)
    return analysis


if __name__ == "__main__":
    #Basic details about your analyzer
    name = "Python Test Analyzer"
    version = "0.0.1"
    description = "This is a test analyzer to demonstrate working with PyAres to create analyzers!"
    pythonDemoAnalyzer = AresAnalyzerService(analyze, name, version, description)

    #Add Analysis Parameters
    pythonDemoAnalyzer.add_analysis_parameter("Growth", AresDataType.NUMBER)
    pythonDemoAnalyzer.add_analysis_parameter("Temperature", AresDataType.NUMBER)

    pythonDemoAnalyzer.start()
```
This example creates a simple analyzer that expects to receive two values from ARES, growth and temperature. It then returns a simple static value of six as the analysis result.

###  💻 Device Usage

PyAres gives you the ability to create devices to communicate with your ARES system. Typically your device would be external hardware connected via serial port or USB to your computer. For demonstration purposes, below is a simulated device that has a modifiable temperature value. It's temperature can be set with the set_temperature method, or retrieved with the get_temperature method. We use a five second delay in the set_temperature method to simulate a delayed response from hardward. It also implements the get_device_state method which returns any data ARES should log as this devices state, and enter_safe_mode to fulfill the required ability for ARES to be able to reset any device to a known state.

```Python
class DemoDevice:
  # A simulated device. In reality, these communications would be happening with external hardware over serial, usb, etc.
  def __init__(self):
    self.temperature = 0.0

  def set_temperature(self, temperature: float):
    self.temperature = temperature
    time.sleep(5)
    return {}

  def get_temperature(self):
    # Dictionary key should match what we defined in our schema earlier
    return { "temperature": self.temperature }
  
  def get_device_state(self):
    state_dictionary = { "temperature": self.temperature }
    return state_dictionary
  
  def enter_safe_mode(self):
    self.temperature = 0
```

PyAres can be used to connect this simulated device with ARES. Below is a basic example of setting up a PyAres device.

```Python
device = DemoDevice()

if __name__ == "__main__":
  # Basic information about my device
  device_name = "Demo Device"
  description = "A device to demonstrate the PyAres device capabilities"
  version = "1.0.0"
  device_service = AresDeviceService(device.enter_safe_mode, device.get_device_state, device_name, description, version)

  #Create Command Descriptor, then add command
  parameter_schema = DeviceSchemaEntry(AresDataType.NUMBER, "A numeric temperature value", "Degree's Celsius")
  input_schema = { "temperature": parameter_schema }
  descriptor = DeviceCommandDescriptor("Set Temperature", "Set's the temperature of the demo device to the provided value.", input_schema, {})
  device_service.add_new_command(descriptor, device.set_temperature)

  output_schema = {"temperature": DeviceSchemaEntry(AresDataType.NUMBER, "The current temperature of the device", "Degree's Celsius")}
  get_temp_desc = DeviceCommandDescriptor("Get Temperature", "Get's the current temperature of the demo device.", {}, output_schema)
  device_service.add_new_command(get_temp_desc, device.get_temperature)

  #Add Settings
  device_service.add_setting("Allow Negative Values", True)

  device_service.start()
```
The central component to your PyAres device is your AresDeviceService. This class acts as a bridge, managing all gRPC communications between PyAres and ARES, and provides the ability to define the behavior and capabilities of your device. Here we create a device with two commands; "Get Temperature" and "Set Temperature". To define commands in PyAres, you must provide a defined schema for both the input and output of the command in the form of a dictionary. This gives the PyAres user a flexible way to represent the data that your commands expect to receive, as well as the data ARES should expect to come from your commands. This information becomes part of your DeviceCommandDescriptor, which also holds a name for your command as well as a brief description. We then report our command capabilities to ARES via the add_new_command method. This method takes in our descriptor, and a reference to the method you defined for your command. 

### 📄 License

The PyAres project is licensed under the MIT License - see details in [LICENSE.txt]([https://github.com/AFRL-ARES/PyAres/blob/Develop/LICENSE.txt](https://github.com/AFRL-ARES/PyAres/blob/Develop/LICENSE)) <br></br>

### CLEARANCE
Distribution A. Approved for public release: distribution unlimited. AFRL-2025-5332.

