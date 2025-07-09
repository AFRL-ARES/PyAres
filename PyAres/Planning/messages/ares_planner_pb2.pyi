from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Capabilities(_message.Message):
    __slots__ = ("service_name", "timeout_seconds", "available_planners", "adapter_settings")
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_PLANNERS_FIELD_NUMBER: _ClassVar[int]
    ADAPTER_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    timeout_seconds: int
    available_planners: _containers.RepeatedCompositeFieldContainer[Planner]
    adapter_settings: _containers.RepeatedCompositeFieldContainer[PlannerSetting]
    def __init__(self, service_name: _Optional[str] = ..., timeout_seconds: _Optional[int] = ..., available_planners: _Optional[_Iterable[_Union[Planner, _Mapping]]] = ..., adapter_settings: _Optional[_Iterable[_Union[PlannerSetting, _Mapping]]] = ...) -> None: ...

class Planner(_message.Message):
    __slots__ = ("planner_name", "description", "version", "unique_id")
    PLANNER_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    planner_name: str
    description: str
    version: str
    unique_id: str
    def __init__(self, planner_name: _Optional[str] = ..., description: _Optional[str] = ..., version: _Optional[str] = ..., unique_id: _Optional[str] = ...) -> None: ...

class PlannerSetting(_message.Message):
    __slots__ = ("setting_name", "setting_value", "optional")
    SETTING_NAME_FIELD_NUMBER: _ClassVar[int]
    SETTING_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    setting_name: str
    setting_value: SettingValue
    optional: bool
    def __init__(self, setting_name: _Optional[str] = ..., setting_value: _Optional[_Union[SettingValue, _Mapping]] = ..., optional: bool = ...) -> None: ...

class SettingValue(_message.Message):
    __slots__ = ("bool_value", "int32_value", "int64_value", "float_value", "double_value", "string_value", "bytes_value")
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BYTES_VALUE_FIELD_NUMBER: _ClassVar[int]
    bool_value: bool
    int32_value: int
    int64_value: int
    float_value: float
    double_value: float
    string_value: str
    bytes_value: bytes
    def __init__(self, bool_value: bool = ..., int32_value: _Optional[int] = ..., int64_value: _Optional[int] = ..., float_value: _Optional[float] = ..., double_value: _Optional[float] = ..., string_value: _Optional[str] = ..., bytes_value: _Optional[bytes] = ...) -> None: ...

class PlanRequest(_message.Message):
    __slots__ = ("planning_parameters",)
    PLANNING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    planning_parameters: _containers.RepeatedCompositeFieldContainer[PlanningParameter]
    def __init__(self, planning_parameters: _Optional[_Iterable[_Union[PlanningParameter, _Mapping]]] = ...) -> None: ...

class PlanResponse(_message.Message):
    __slots__ = ("parameter_names", "parameter_values")
    PARAMETER_NAMES_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_VALUES_FIELD_NUMBER: _ClassVar[int]
    parameter_names: _containers.RepeatedScalarFieldContainer[str]
    parameter_values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, parameter_names: _Optional[_Iterable[str]] = ..., parameter_values: _Optional[_Iterable[float]] = ...) -> None: ...

class PlanningParameter(_message.Message):
    __slots__ = ("parameter_name", "parameter_value", "minimum_value", "maximum_value", "minimum_precision", "parameter_history", "data_type", "metadata", "is_planned", "is_result", "planner_name")
    PARAMETER_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_VALUE_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_VALUE_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_PRECISION_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_HISTORY_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    IS_PLANNED_FIELD_NUMBER: _ClassVar[int]
    IS_RESULT_FIELD_NUMBER: _ClassVar[int]
    PLANNER_NAME_FIELD_NUMBER: _ClassVar[int]
    parameter_name: str
    parameter_value: float
    minimum_value: float
    maximum_value: float
    minimum_precision: float
    parameter_history: _containers.RepeatedScalarFieldContainer[float]
    data_type: str
    metadata: Metadata
    is_planned: bool
    is_result: bool
    planner_name: str
    def __init__(self, parameter_name: _Optional[str] = ..., parameter_value: _Optional[float] = ..., minimum_value: _Optional[float] = ..., maximum_value: _Optional[float] = ..., minimum_precision: _Optional[float] = ..., parameter_history: _Optional[_Iterable[float]] = ..., data_type: _Optional[str] = ..., metadata: _Optional[_Union[Metadata, _Mapping]] = ..., is_planned: bool = ..., is_result: bool = ..., planner_name: _Optional[str] = ...) -> None: ...

class PlannedParameter(_message.Message):
    __slots__ = ("parameter_name", "parameter_value", "metadata")
    PARAMETER_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_VALUE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    parameter_name: str
    parameter_value: float
    metadata: Metadata
    def __init__(self, parameter_name: _Optional[str] = ..., parameter_value: _Optional[float] = ..., metadata: _Optional[_Union[Metadata, _Mapping]] = ...) -> None: ...

class Metadata(_message.Message):
    __slots__ = ("metadata_name",)
    METADATA_NAME_FIELD_NUMBER: _ClassVar[int]
    metadata_name: str
    def __init__(self, metadata_name: _Optional[str] = ...) -> None: ...
