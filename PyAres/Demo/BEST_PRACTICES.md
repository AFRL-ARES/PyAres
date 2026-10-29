# Best Practices: Working WITH PyAres (Developing Services)

Context for AI agents and human contributors working **with**
(consuming/implementing services for) the **PyAres** library.

## 0. Directory Structure

The `PyAres/Demo/` directory contains reference implementations and test clients for PyAres services:

```
PyAres/Demo/
├── BEST_PRACTICES.md                   # This File. Service implementation guidelines and best practices
├── Analyzers/                          # Example analyzer services and test scripts
│   ├── analyzer_test.py                # Basic analyzer implementation example
│   ├── analyzer_test_tools_demo.py     # Standalone analyzer testing with AnalyzerTestClient
│   ├── analyzer_wiki.py                # Reference analyzer returning structured Objective metrics
│   └── ax_analyzer_test.py             # Ground-truth evaluation service for Ax optimization
├── Devices/                            # Example device services and hardware wrappers
│   ├── device_test.py                  # Simulated device with temperature control and state
│   ├── failure_test_device.py          # Device demonstrating intentional failures & error handling
│   ├── hotplate.py                     # Virtual hotplate with safe mode, polling, & command schemas
│   ├── random_number_device.py         # Virtual sensor generating random numbers with schemas
│   └── rotary_mixer.py                 # Virtual rotary mixer with RPM speed control
└── Planners/                           # Example planning services and test scripts
    ├── planner_test.py                 # Planner example processing parameter histories & objectives
    ├── planner_test_tools_demo.py      # Standalone planner testing with PlannerTestClient
    └── planner_wiki.py                 # Batch random parameter generation planner
```

## 1. General Guidance

- **Soft Preference for Stateless Services** - When possible, services should be designed to be stateless, treating each request independently,
  and retaining no data between calls. Sometimes, a purely stateless desgin is not possible or may result in large time delays due to computational overhead. For example a service with a persistent connection to hardware or software, a streamed data source, a large database that must be loaded into ram etc. In these cases the execution logic should be contained within a class that initializes and manages the persistent resources either on class instantiation or on the receipt of the first request from ARES
- **Graceful Closeout and Exception Handling** - Services should always take care to exit gracefully in the case of an exception or manual 
  closeout of the service by using try-except-finally control structure. If an exception occured while procesing a request from ARES, this exception should be conveyed back to ARES as part of error handling. When the service involves a connection to an extneral hardware interface, network, or software instance logic should be included to safely close down those connections. Ensure that all child threads or sub-processes spawned by the service are terminated upon closeout.
- **Object-Oriented Design for more complex services** - Any service logic that excedes more that 4 or 5 subsidiary functions or more than a few dozen
   lines of code should be implmented as a class.
- **Service Portability** - When implemnting a service use a project structure that is suitable for redistribution and installation with package managers 
  such as `pip`. Every service should have documented requirements in a `requirements.txt` or `pyproject.toml` file.
  

## 2 Implementing Device Services (`AresDeviceService`)

A device service wraps real or simulated hardware to expose actuators and sensors to ARES OS.
They are also the most flexible class of servce and can be used execute arbitrary logic that is needed 
within an ARES Experimental. For example:

- **Calculations Outside of Analyzers** - When derived values are needed with the experimental loop (e.g., setting a sample acquistion time based on a the system flow   
    rate).
- **Execution of External Scripts** - When an experimental campaign needs to trigger external actions on the host PC (e.g., compiling software, cleaning up temporary files).
- **Interactions With External Software** - Call external software APIs (e.g., Initialize or post-process computer simulations).

```python
from PyAres import AresDeviceService, DeviceCommandDescriptor, DeviceSchemaEntry, AresDataType, StatusCode
from PyAres.Device.device_models import DeviceCommandResponse

# 1. Mandatory Safe Mode Callback (must be robust, non-blocking or fast, and idempotent)
def enter_safe_mode():
    heater.set_power(0.0)
    motors.stop()

# 2. Mandatory State Polling Callback (returns telemetry dictionary)
def get_device_state() -> dict:
    return {
        "temperature": sensor.read_temp(),
        "is_moving": motors.is_active(),
    }

service = AresDeviceService(
    enter_safe_mode_logic=enter_safe_mode,
    get_device_state_logic=get_device_state,
    device_name="Tubular Furnace",
    description="High temperature furnace driver",
    version="1.0.0",
    port=7100,
)

# 3. Register Commands
set_temp_descriptor = DeviceCommandDescriptor(
    name="set_temperature",
    description="Sets the target furnace temperature in Celsius.",
    input_schema={
        "target_celsius": DeviceSchemaEntry(
            type=AresDataType.FLOAT,
            description="Target temperature in deg C",
            min_number_value=20.0,
            max_number_value=1200.0,
        )
    },
    output_schema={
        "achieved_target": DeviceSchemaEntry(type=AresDataType.FLOAT)
    }
)

def set_temperature(target_celsius: float) -> DeviceCommandResponse:
    try:
        hardware.set_temp(target_celsius)
        return DeviceCommandResponse(
            status_code=StatusCode.COMMAND_SUCCESS,
            response={"achieved_target": target_celsius}
        )
    except Exception as e:
        return DeviceCommandResponse(
            status_code=StatusCode.HARDWARE_FAULT,
            error_string=str(e),
            response={}
        )

service.add_new_command(set_temp_descriptor, set_temperature)
service.start()
```

### Invariants & Rules for Device Services:
- **Always return `DeviceCommandResponse`**: Returning bare values or raw dictionaries is deprecated and triggers a `FutureWarning`. Always encapsulate return values in `DeviceCommandResponse(status_code=..., response=...)`.
- **Match Parameter Signatures**: The parameter names and count of your Python callback **must match exactly** with the `input_schema` keys in `DeviceCommandDescriptor`. Mismatches emit warnings or fail at execution.
- **Fail Gracefully via `StatusCode`**: Do not let unhandled hardware exceptions crash the service. Catch exceptions and return appropriate status codes (`StatusCode.HARDWARE_FAULT`, `StatusCode.COMMAND_FAILED`, `StatusCode.OUT_OF_RANGE`, etc.).
- **Always Keep `enter_safe_mode` Safe**: The `enter_safe_mode` callback must never throw an unhandled exception; wrap internal calls in `try/except` and ensure it powers down active heating, radiation, lasers, or mechanical stages.

---

## 2 Implementing Planner Services (`AresPlannerService`)

A planner receives parameter histories and analysis feedback from past experiments and computes
the next set of parameters to test.

```python
from PyAres import AresPlannerService, PlanRequest, PlanResponse, Outcome, ObjectiveStatus

def my_planning_logic(request: PlanRequest) -> PlanResponse:
    # 1. Access parameter definitions & histories
    for param in request.parameters:
        print(f"Param: {param.name}, Min: {param.minimum_value}, Max: {param.maximum_value}")
        for item in param.param_history:
            print(f"  Planned: {item.planned_value}, Achieved: {item.achieved_value}")

    # 2. Access analysis objectives from previous runs
    for entry in request.analysis_data:
        for obj in entry.analysis_objectives:
            print(f"  Objective {obj.objective_name} = {obj.objective_value}")

    # 3. Calculate next suggestion
    next_temp = 350.0
    next_speed = 12.5

    # 4. Return PlanResponse
    return PlanResponse(
        parameter_data={"temperature": next_temp, "speed": next_speed},
        outcome=Outcome.SUCCESS,
        objective_status=ObjectiveStatus.OBJECTIVE_UNACHIEVED,
    )

service = AresPlannerService(
    plan_logic=my_planning_logic,
    service_name="BayesianOptimizer",
    description="Gaussian Process planner for synthesis optimization",
    version="0.1.0",
    port=7082,
)
service.start()
```

### Invariants & Rules for Planner Services:
- **Use `request.analysis_data` (Not `request.analysis_results`)**: `PlanRequest.analysis_results` is deprecated. Use `request.analysis_data` or the convenience helper `request.analysis_objectives` to access `Objective` instances.
- **Provide `parameter_data` Dict or Matched Lists**: Either pass `parameter_data={"key": value}` or pass two lists of equal length: `parameter_names=[...]` and `parameter_values=[...]`.
- **Stop Campaigns cleanly**: When optimization converges or target thresholds are reached, return `objective_status=ObjectiveStatus.OBJECTIVE_ACHIEVED`.

---

## 3 Implementing Analyzer Services (`AresAnalyzerService`)

An analyzer ingests raw sensor or device measurements and produces structured objective values.

```python
from PyAres import AresAnalyzerService, AnalysisRequest, AnalysisResponse, Objective, Outcome, AresDataType

def my_analysis_logic(request: AnalysisRequest) -> AnalysisResponse:
    raw_resistance = request.inputs.get("ldr_resistance")
    if raw_resistance is None:
        return AnalysisResponse(
            objectives=[],
            outcome=Outcome.FAILURE,
            error_string="Missing input 'ldr_resistance'"
        )

    # Compute metric
    normalized_intensity = 1.0 / (raw_resistance + 1e-6)

    return AnalysisResponse(
        objectives=[
            Objective(
                objective_name="optical_transmission",
                objective_value=normalized_intensity,
                objective_metadata={"units": "a.u.", "confidence": 0.98}
            )
        ],
        outcome=Outcome.SUCCESS
    )

service = AresAnalyzerService(
    custom_analysis_logic=my_analysis_logic,
    name="PhotodiodeAnalyzer",
    version="1.0.0",
    description="Computes optical transmission from resistance readings",
    port=7083,
)

service.add_analysis_parameter(name="ldr_resistance", data_type=AresDataType.FLOAT, optional=False)
service.add_objective_output(name="optical_transmission", data_type=AresDataType.FLOAT)
service.start()
```

### Invariants & Rules for Analyzer Services:
- **Return explicit `Objective` instances**: Constructing `AnalysisResponse(result=...)` is deprecated. Always construct `AnalysisResponse(objectives=[Objective(...)], outcome=...)`.
- **Declare schemas via `add_analysis_parameter` and `add_objective_output`**: Declaring input and output schemas allows ARES OS to validate compatibility before starting campaigns.

---

## 4 Standalone Testing with `test_tools`

PyAres provides built-in standalone test clients in `PyAres.test_tools` so you can verify services
without running the entire ARES OS orchestrator:
- `AnalyzerTestClient(port=7083, host='localhost')`: Test `get_info()`, `check_status()`, and `run_analysis(inputs, settings)`.
- `PlannerTestClient(port=7082, host='localhost')`: Test `get_info()`, `check_status()`, and `run_planning(request)`.

---
