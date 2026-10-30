# Best Practices: Working WITH PyAres (Developing Services)

Context for AI agents and human contributors working **with**
(consuming/implementing services for) the **PyAres** library.

## 0. Directory Structure

The `PyAres/Demo/` directory contains reference implementations and test clients for PyAres services:

```text
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
- **Graceful Closeout and Exception Handling** - Services should always take care to exit gracefully in the case of an exception or manual (ctrl+c)closeout of the service by using try-except-finally control structure. If an exception occured while procesing a request from ARES, this exception should be conveyed back to ARES as part of error handling. When the service involves a connection to an extneral hardware interface, network, or software instance logic should be included to safely close down those connections. Ensure that all child threads or sub-processes spawned by the service are terminated upon closeout.
- **Object-Oriented Design for More Complex Services** - Any service logic that needs more that 4 or 5  functions or more
  than a few dozen lines of code should be implmented as a class.
- **Service Portability** - When implemnting a service use a project structure that is suitable for redistribution and installation with package managers such as `pip`. Every service should have documented requirements in a `requirements.txt` or `pyproject.toml` file. If a servce requires proprietary elements that cannot be freely distributed (e.g., an API key, a manufacturer SDK), the service should be structured so that it can interact with user-provided proprietary elements without incorporating them into the redistributable core of the service.
  
## 2 Implementing Device Services (`AresDeviceService`)

A device service wraps real or simulated hardware to expose actuators and sensors to ARES OS. They are also the most flexible class of servce and can be used execute arbitrary logic that is needed within an ARES Experimental. For example:

- **Calculations Outside of Analyzers** - When derived values are needed with the experimental loop (e.g., setting a sample acquistion time based on a the system flowrate).
- **Execution of External Scripts** - When an experimental campaign needs to trigger external actions on the host PC (e.g., compiling software, cleaning up temporary files).
- **Interactions With External Software** - Call external software APIs (e.g., Initialize or post-process computer simulations).

Example device implementations can be found in `PyAres/Demo/Devices`

### Invariants & Rules for Device Services

- **Wrap Generic Device Drivers** - When a python compatible device driver is not provided, it is preferable to implement a separate python interface class that handles device communication and top-level commands and then wrap the device in a PyAres compatibility layer used by the device service. This ensures the device is useable with or without PyAres.
- **Mandatory Safe Mode and Get State Callbacks** - Safe mode and get state callbacks are mandatory on every PyAres device service. Safe mode callbacks must be robust, non-blocking or fast, and idempotent.
- **Always return `DeviceCommandResponse`**: Returning bare values or raw dictionaries is deprecated and triggers a `FutureWarning`. Always encapsulate return values in `DeviceCommandResponse(status_code=..., response=...)`.
- **Match Parameter Signatures**: The parameter names and count of your Python callback **must match exactly** with the `input_schema` keys in `DeviceCommandDescriptor`. Mismatches emit warnings or fail at execution.
- **Fail Gracefully via `StatusCode`**: Do not let unhandled hardware exceptions crash the service. Catch exceptions and return appropriate status codes (`StatusCode.HARDWARE_FAULT`, `StatusCode.COMMAND_FAILED`, `StatusCode.OUT_OF_RANGE`, etc.).
- **Always Keep `enter_safe_mode` Safe**: The `enter_safe_mode` callback must never throw an unhandled exception; wrap internal calls in `try/except` and ensure it sets physical hardware to a safe state.

---

## 2 Implementing Planner Services (`AresPlannerService`)

A planner receives parameter histories and analysis feedback from past experiments and computes
the next set of parameters to test.

Example planner implementations can be found in `PyAres/Demo/Planners`

### Invariants & Rules for Planner Services

- **Batch Planning Support**: Planners should check for the number of requested experiments in `PlanRequest.batch_size` to determine how many sets of parameter values to generate and return in the `Plan` object.
- **Use `request.analysis_data` (Not `request.analysis_results`)**: `PlanRequest.analysis_results` is deprecated. Use `request.analysis_data` or the convenience helper `request.analysis_objectives` to access `Objective` instances.
- **Provide `parameter_data` Dict or Matched Lists**: Either pass `parameter_data={"key": value}` or pass two lists of equal length: `parameter_names=[...]` and `parameter_values=[...]`.
- **Stop Campaigns cleanly**: When optimization converges or target thresholds are reached, return `objective_status=ObjectiveStatus.OBJECTIVE_ACHIEVED`.

---

## 3 Implementing Analyzer Services (`AresAnalyzerService`)

An analyzer ingests data from an experimental source and produces structured objective values that are used as feedback for experimental planning.

Example planner implementations can be found in `PyAres/Demo/Analyzers`

### Invariants & Rules for Analyzer Services

- **Return explicit `Objective` instances**: Constructing `AnalysisResponse(result=...)` is deprecated. Always construct `AnalysisResponse(objectives=[Objective(...)], outcome=...)`.
- **Declare schemas via `add_analysis_parameter` and `add_objective_output`**: Declaring input and output schemas allows ARES OS to validate compatibility before starting campaigns.

---

## 4 Standalone Testing with `test_tools`

PyAres provides built-in standalone test clients in `PyAres.test_tools` so you can verify services
without running the entire ARES OS orchestrator:

- `AnalyzerTestClient(port=7083, host='localhost')`: Test `get_info()`, `check_status()`, and `run_analysis(inputs, settings)`.
- `PlannerTestClient(port=7082, host='localhost')`: Test `get_info()`, `check_status()`, and `run_planning(request)`.

---
