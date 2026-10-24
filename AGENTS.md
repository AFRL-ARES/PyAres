# AGENTS.md — Repository Navigation Context for PyAres

Context for AI agents and human contributors working **in** (maintaining/extending)
or **with** (consuming/implementing services for) the **PyAres** library.

---

## 1. What This Project Is

**PyAres** is the official Python SDK and gRPC service framework for the **ARES**
(Autonomous Research System) self-driving laboratory ecosystem. It bridges native Python
code with the centralized [ARES OS 2](https://github.com/AFRL-ARES/ARES) orchestrator using
Protocol Buffers and gRPC via [`ares-datamodel`](https://github.com/AFRL-ARES/ares-datamodel).

PyAres abstracts away raw Protobuf messages and gRPC boilerplate, exposing clean,
idiomatic Python interfaces to implement four core service archetypes:

1. **Device Services (`AresDeviceService`)** — Control laboratory hardware, actuators,
   and sensors; expose executable commands, schemas, and live telemetry; implement safety
   interlocks and safe-mode procedures.
2. **Planning Services (`AresPlannerService`)** — Drive experimental campaigns using
   optimization algorithms, active learning, Bayesian optimization, heuristic search, etc. 
   to suggest the next parameter values to evaluate.
3. **Analysis Services (`AresAnalyzerService`)** — Extract quantitative objectives and
   metrics from raw experimental outputs, passing structured results to planners and ARES OS.
4. **Visualizer Services (`AresVisualizerService`)** — Render charts and dashboard widgets
   (e.g., Plotly figures) for display in the ARES OS web interface.

---

## 2. Python Environment & Build System

- **Python Version**: `>= 3.10`
- **Build Backend**: [`hatchling`](https://hatch.pypa.io/) (configured in `pyproject.toml`)
- **Core Dependency**: `ares-datamodel >= 0.36.0` (provides Protobuf/gRPC message stubs)
- **Optional Dependencies**: `visualization = ["plotly >= 5.0"]`
- **Dynamic Versioning**: `hatchling` reads the package version dynamically from the
  `PYARES_PACKAGE_VERSION` environment variable (required during `build` or `pip install -e .`):
  ```bash
  export PYARES_PACKAGE_VERSION="0.0.1"  # or matching release tag
  ```

### Development & Testing Setup

```bash
# Clone and enter repo
cd PyAres

# Set version for hatchling
export PYARES_PACKAGE_VERSION="0.0.1"

# Install in editable mode with test dependencies
pip install -e .
pip install grpcio grpcio-tools protobuf pytest

# Run full test suite
pytest -v tests/
```

---

## 3. Repository Layout & Code Map

```
PyAres/
├── pyproject.toml              # Hatchling build specification & dependencies
├── README.md                   # Upstream package summary & centralized docs link
├── LICENSE                     # MIT License
├── .github/workflows/          # CI/CD: unit tests (ubuntu, py3.10) & PyPI publishing
├── tests/                      # Unit tests & MockGrpcContext
└── PyAres/                     # Root package directory
    ├── __init__.py             # Public top-level API exports
    ├── Device/                 # Hardware control service framework
    │   ├── device_service.py   # AresDeviceService & AresDeviceServiceWrapper (gRPC servicer)
    │   ├── device_models.py    # DeviceCommandDescriptor, DeviceCommandResponse, StatusCode, etc.
    │   └── device_warnings.py  # Warning categories for device services
    ├── Planning/               # Campaign & experiment planning framework
    │   ├── planning_service.py # AresPlannerService & AresPlannerServiceWrapper (gRPC servicer)
    │   └── planner_models.py   # PlanRequest, PlanResponse, PlanningParameter, Plan, etc.
    ├── Analyzing/              # Experiment evaluation & objective calculation framework
    │   ├── analysis_service.py # AresAnalyzerService & AresAnalyzerServiceWrapper (gRPC servicer)
    │   └── analyzer_models.py  # AnalysisRequest, AnalysisResponse, Objective, ObjectiveSchema
    ├── Visualizers/            # UI Visualization rendering framework
    │   ├── visualizer_service.py # AresVisualizerService & AresVisualizerServiceWrapper
    │   └── visualizing_models.py # VisualizationOption, VisualizationRequest, DataPoint
    ├── Models/                 # Shared data models & enums
    │   └── ares_data_models.py # AresDataType, Outcome, PlanStatusCode, RequestMetadata, Limits
    ├── Utils/                  # Protobuf ↔ Python conversion utilities & base infrastructure
    │   ├── grpc_base.py        # AresGrpcServiceBase: server lifecycle, thread pool, message size
    │   ├── ares_service_base.py# AresBaseService & AresServiceWrapperBase: common RPCs & async resolver
    │   ├── metadata_interceptors.py # DatamodelVersionServerInterceptor: handshake version header
    │   ├── ares_value_utils.py # Primitive/AresValue protobuf bi-directional conversion
    │   ├── ares_struct_utils.py# Dict/AresStruct conversion helpers
    │   ├── ares_data_schema_utils.py # Schema builder helpers for inputs, settings, and outputs
    │   ├── ares_data_type_utils.py   # AresDataType enum translation
    │   ├── device_status_code_utils.py # Status code mapping & success evaluation
    │   ├── ares_outcome_utils.py     # Outcome enum translation
    │   ├── plan_request_utils.py     # Protobuf PlanRequest unpacking
    │   └── plan_response_utils.py    # Protobuf PlanResponse packaging
    ├── test_tools/             # Standalone test clients
    │   ├── analyzer_tester.py  # AnalyzerTestClient: test Analyzer services without ARES OS
    │   └── planner_tester.py   # PlannerTestClient: test Planner services without ARES OS
    └── Demo/                   # Working reference implementations
        ├── Devices/            # Example devices (hotplate, rotary mixer, random generator, etc.)
        ├── Planners/           # Example planners (grid, random, test-tools integration)
        └── Analyzers/          # Example analyzers (basic, Ax analyzer, test-tools integration)
```

---

## 4. Architectural Patterns & Core Invariants

### 4.1 Base Service Inheritance Architecture
Every service in PyAres (`Device`, `Planning`, `Analyzing`, `Visualizer`) is split into two components:
1. **The User-Facing Service (`AresBaseService` subclass)**:
   - Manages the gRPC server lifecycle (`start()`, `stop()`).
   - Configures networking (`port`, `use_localhost`, `max_message_size`).
   - Manages service settings and capability schema declarations.
2. **The Internal gRPC Servicer Wrapper (`AresServiceWrapperBase` subclass)**:
   - Implements generated gRPC Servicer stubs from `ares-datamodel`.
   - Exposes standard diagnostic RPCs: `GetInfo`, `GetConnectionStatus`, `GetState`.
   - Intercepts requests, translates protobuf messages to native Python data structures, executes registered callbacks, and packs Python returns back into protobuf responses.

### 4.2 Version Handshake & Metadata Interception
All services run with `DatamodelVersionServerInterceptor` (`PyAres/Utils/metadata_interceptors.py`).
Every RPC attaches the `datamodel-version` header corresponding to the installed `ares_datamodel`
version. This ensures ARES OS and external orchestrators can verify protocol compatibility.

### 4.3 Async & Sync Callback Support
User-supplied logic (e.g., `enter_safe_mode`, `plan_logic`, `custom_analysis_logic`, commands)
can be written as standard synchronous functions or `async` coroutines. The wrapper automatically
resolves awaitables via `_resolve_awaitable()` (`PyAres/Utils/ares_service_base.py`).

### 4.4 Default Port Allocations
- **Device Service**: `7100` (configurable via `port`)
- **Planner Service**: `7082` (configurable via `port`)
- **Analyzer Service**: `7083` (configurable via `port`)

---

## 5. Best Practices: Working WITH PyAres (Developing Services)

### 5.1 Implementing Device Services (`AresDeviceService`)

A device service wraps real or simulated hardware to expose actuators and sensors to ARES OS.

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

#### Invariants & Rules for Device Services:
- **Always return `DeviceCommandResponse`**: Returning bare values or raw dictionaries is deprecated and triggers a `FutureWarning`. Always encapsulate return values in `DeviceCommandResponse(status_code=..., response=...)`.
- **Match Parameter Signatures**: The parameter names and count of your Python callback **must match exactly** with the `input_schema` keys in `DeviceCommandDescriptor`. Mismatches emit warnings or fail at execution.
- **Fail Gracefully via `StatusCode`**: Do not let unhandled hardware exceptions crash the service. Catch exceptions and return appropriate status codes (`StatusCode.HARDWARE_FAULT`, `StatusCode.COMMAND_FAILED`, `StatusCode.OUT_OF_RANGE`, etc.).
- **Always Keep `enter_safe_mode` Safe**: The `enter_safe_mode` callback must never throw an unhandled exception; wrap internal calls in `try/except` and ensure it powers down active heating, radiation, lasers, or mechanical stages.

---

### 5.2 Implementing Planner Services (`AresPlannerService`)

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

#### Invariants & Rules for Planner Services:
- **Use `request.analysis_data` (Not `request.analysis_results`)**: `PlanRequest.analysis_results` is deprecated. Use `request.analysis_data` or the convenience helper `request.analysis_objectives` to access `Objective` instances.
- **Provide `parameter_data` Dict or Matched Lists**: Either pass `parameter_data={"key": value}` or pass two lists of equal length: `parameter_names=[...]` and `parameter_values=[...]`.
- **Stop Campaigns cleanly**: When optimization converges or target thresholds are reached, return `objective_status=ObjectiveStatus.OBJECTIVE_ACHIEVED`.

---

### 5.3 Implementing Analyzer Services (`AresAnalyzerService`)

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

#### Invariants & Rules for Analyzer Services:
- **Return explicit `Objective` instances**: Constructing `AnalysisResponse(result=...)` is deprecated. Always construct `AnalysisResponse(objectives=[Objective(...)], outcome=...)`.
- **Declare schemas via `add_analysis_parameter` and `add_objective_output`**: Declaring input and output schemas allows ARES OS to validate compatibility before starting campaigns.

---

### 5.4 Standalone Testing with `test_tools`

PyAres provides built-in standalone test clients in `PyAres.test_tools` so you can verify services
without running the entire ARES OS orchestrator:
- `AnalyzerTestClient(port=7083, host='localhost')`: Test `get_info()`, `check_status()`, and `run_analysis(inputs, settings)`.
- `PlannerTestClient(port=7082, host='localhost')`: Test `get_info()`, `check_status()`, and `run_planning(request)`.

---

## 6. Best Practices: Working IN PyAres (Maintaining the Library)

### 6.1 Protobuf & Datamodel Compatibility
- PyAres depends strictly on `ares-datamodel`. Never import raw gRPC files from custom paths; always import from `ares_datamodel...`.
- If a Protobuf schema in `ares-datamodel` changes, update the translation layers in `PyAres/Utils/` (`ares_value_utils.py`, `ares_struct_utils.py`, `ares_data_schema_utils.py`, etc.) and ensure both forward and backwards compatibility.

### 6.2 Backwards Compatibility & Deprecation Policy
- Many existing laboratory devices run older PyAres conventions.
- When introducing a new model or schema structure, provide an adapter or backwards compatibility fallback (e.g., how `ExecuteCommand` still accepts legacy raw dict returns and emits a `FutureWarning`, or how `AnalysisResponse` handles legacy `result`).
- Use Python's `warnings.warn` with `FutureWarning` or `DeprecationWarning` rather than throwing errors on older API patterns.

### 6.3 Network Binding & Host Configuration
- `AresGrpcServiceBase` defaults `use_localhost=True`, binding to `localhost:{port}`.
- Setting `use_localhost=False` binds to `[::]:{port}` (IPv6 wildcard, allowing LAN access from other host machines).
- Never hardcode IP addresses or assume external network access.

### 6.4 Unit Testing Practices
- Place unit tests under `tests/`.
- Name test files `test_*.py`.
- Use `unittest.TestCase` or `pytest`.
- Use `MockGrpcContext` (from `tests/mock_grpc_context.py` or inline) to test gRPC servicer logic without needing live socket bindings.
- When spinning up a real service in a test, always ensure `service.stop()` is invoked in `tearDown()` to release the port.

---

## 7. Licensing & Clearance

- **License**: MIT License (see [`LICENSE`](LICENSE)).
- **Clearance**: AFRL Clearance: *Distribution A. Approved for public release: distribution unlimited. AFRL-2025-5332.*
- Keep all first-party code MIT licensed. Do not vendor or introduce copyleft/GPL code into PyAres.
