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
        planned_values.append(random.uniform(param.minimum_value, param.maxiumum_value))
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

### Devices

🚧 Coming Soon 🚧

### 📄 License

The PyAres project is licensed under the USAF Open Source Agreement Version 1.0 - see details in [LICENSE.txt](https://github.com/AFRL-ARES/PyAres/blob/Develop/LICENSE.txt)
