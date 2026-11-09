# AGENTS.md — Repository Navigation Context for PyAres

Context for AI agents and human contributors working **in** (maintaining/extending)
or **with** (consuming/implementing services for) the **PyAres** library.

---

## 1. What This Project Is

**PyAres** is the official Python SDK and gRPC service framework for the **ARES** 
self-driving laboratory ecosystem. It bridges native Python
code with the centralized [ARES OS 2](https://github.com/AFRL-ARES/ARES) orchestrator using
Protocol Buffers and gRPC via [`ares-datamodel`](https://github.com/AFRL-ARES/ares-datamodel).
Official documentation for all aspects of the ARES ecosystem is located on the [Docs Page](https://afrl-ares.github.io/).

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

- **Consult TOML for Dependencies and Build Info** The `pyproject.toml` file in the repository root file serves
  as the single source of truth for dependencies and build information.  
- **Dynamic Versioning**: The [`hatchling`](https://hatch.pypa.io/) build back ends reads the package version 
  dynamically from the `PYARES_PACKAGE_VERSION` environment variable (required during `build` or `pip install -e .`):
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
├── pyproject.toml                          # Hatchling build specification & dependencies
├── README.md                               # Upstream package summary & centralized docs link
├── AGENTS.md                               # This File
├── LICENSE                                 # MIT License
├── .github/workflows/                      # CI/CD: unit tests (ubuntu, py3.10) & PyPI publishing
├── tests/                                  # Unit tests & MockGrpcContext
└── PyAres/                                 # Root package directory
    ├── __init__.py                         # Public top-level API exports
    ├── Device/                             # Hardware control service framework
    │   ├── device_service.py               # AresDeviceService & AresDeviceServiceWrapper (gRPC servicer)
    │   ├── device_models.py                # DeviceCommandDescriptor, DeviceCommandResponse, StatusCode, etc.
    │   └── device_warnings.py              # Warning categories for device services
    ├── Planning/                           # Campaign & experiment planning framework
    │   ├── planning_service.py             # AresPlannerService & AresPlannerServiceWrapper (gRPC servicer)
    │   └── planner_models.py               # PlanRequest, PlanResponse, PlanningParameter, Plan, etc.
    ├── Analyzing/                          # Experiment evaluation & objective calculation framework
    │   ├── analysis_service.py             # AresAnalyzerService & AresAnalyzerServiceWrapper (gRPC servicer)
    │   └── analyzer_models.py              # AnalysisRequest, AnalysisResponse, Objective, ObjectiveSchema
    ├── Visualizers/                        # UI Visualization rendering framework
    │   ├── visualizer_service.py           # AresVisualizerService & AresVisualizerServiceWrapper
    │   └── visualizing_models.py           # VisualizationOption, VisualizationRequest, DataPoint
    ├── Models/                             # Shared data models & enums
    │   └── ares_data_models.py             # AresDataType, Outcome, PlanStatusCode, RequestMetadata, Limits
    ├── Utils/                              # Protobuf ↔ Python conversion utilities & base infrastructure
    │   ├── grpc_base.py                    # AresGrpcServiceBase: server lifecycle, thread pool, message size
    │   ├── ares_service_base.py            # AresBaseService & AresServiceWrapperBase: common RPCs & async resolver
    │   ├── metadata_interceptors.py        # DatamodelVersionServerInterceptor: handshake version header
    │   ├── ares_value_utils.py             # Primitive/AresValue protobuf bi-directional conversion
    │   ├── ares_struct_utils.py            # Dict/AresStruct conversion helpers
    │   ├── ares_data_schema_utils.py       # Schema builder helpers for inputs, settings, and outputs
    │   ├── ares_data_type_utils.py         # AresDataType enum translation
    │   ├── device_status_code_utils.py     # Status code mapping & success evaluation
    │   ├── ares_outcome_utils.py           # Outcome enum translation
    │   ├── plan_request_utils.py           # Protobuf PlanRequest unpacking
    │   └── plan_response_utils.py          # Protobuf PlanResponse packaging
    ├── test_tools/                         # Standalone test clients
    │   ├── analyzer_tester.py              # AnalyzerTestClient: test Analyzer services without ARES OS
    │   └── planner_tester.py               # PlannerTestClient: test Planner services without ARES OS
    └── Demo/                               # Working reference implementations
        ├── BEST_PRACTICES.md               # Best Practcies for PyAres Service Implementations  
        ├── Devices/                        # Example devices (hotplate, rotary mixer, random generator, etc.)
        ├── Planners/                       # Example planners (grid, random, test-tools integration)
        └── Analyzers/                      # Example analyzers (basic, Ax analyzer, test-tools integration)
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
- Examples and guidelines for implementation best bractices are located in `PyAres/Demos/`.

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
