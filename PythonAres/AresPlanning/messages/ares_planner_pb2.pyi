from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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
    __slots__ = ("parameter_name", "parameter_value", "minimum_value", "maximum_value", "minimum_precision", "parameter_history", "data_type", "metadata", "is_planned", "is_result")
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
    def __init__(self, parameter_name: _Optional[str] = ..., parameter_value: _Optional[float] = ..., minimum_value: _Optional[float] = ..., maximum_value: _Optional[float] = ..., minimum_precision: _Optional[float] = ..., parameter_history: _Optional[_Iterable[float]] = ..., data_type: _Optional[str] = ..., metadata: _Optional[_Union[Metadata, _Mapping]] = ..., is_planned: bool = ..., is_result: bool = ...) -> None: ...

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
