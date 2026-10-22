import json
from collections.abc import Iterable, Mapping
from typing import Any, Awaitable, Callable, Optional, Union

import grpc

from ares_datamodel import ares_data_schema_pb2
from ares_datamodel.visualizing.remote import ares_remote_visualizer_service_pb2 as visualizer_service
from ares_datamodel.visualizing.remote import ares_remote_visualizer_service_pb2_grpc as visualizer_service_grpc

from ..Models import AresSchemaEntry
from ..Utils import ares_data_schema_utils, ares_struct_utils
from ..Utils.ares_service_base import AresBaseService, AresServiceWrapperBase
from .visualizing_models import VisualizationDataPoint, VisualizationOption, VisualizationRequest


VisualizationResult = Union[str, Mapping[str, Any], Any]
VisualizationLogicFunction = Callable[[VisualizationRequest], Union[VisualizationResult, Awaitable[VisualizationResult]]]

class AresVisualizerServiceWrapper(AresServiceWrapperBase, visualizer_service_grpc.RemoteVisualizerServiceServicer):
    """Expose native Python visualization callbacks through the gRPC contract."""

    def __init__(self, name: str, version: str, description: str, timeout: int):
        super().__init__(name, version, description, timeout)
        self._visualizations: dict[str, tuple[VisualizationOption, VisualizationLogicFunction]] = {}

    def add_visualization(self, option: VisualizationOption, custom_visualization_logic: VisualizationLogicFunction) -> None:
        """Register a visualization option and the callback that renders it."""
        if not option.visualization_name:
            raise ValueError("visualization_name must not be empty")
        self._visualizations[option.visualization_name] = (option, custom_visualization_logic)

    @staticmethod
    def _schema_to_proto(schema: Any) -> ares_data_schema_pb2.AresStructSchema:
        result = ares_data_schema_pb2.AresStructSchema()
        if schema is None:
            return result
        if isinstance(schema, ares_data_schema_pb2.AresStructSchema):
            result.CopyFrom(schema)
            return result
        if not isinstance(schema, Mapping):
            raise TypeError("visualization schemas must be mappings or AresStructSchema messages")

        for name, entry in schema.items():
            if isinstance(entry, ares_data_schema_pb2.AresValueSchema):
                result.fields[name].CopyFrom(entry)
            elif isinstance(entry, AresSchemaEntry):
                result.fields[name].CopyFrom(ares_data_schema_utils.convert_ares_schema_entry_to_proto(entry))
            else:
                raise TypeError(f"Schema entry '{name}' must be an AresSchemaEntry or AresValueSchema")
        return result

    def GetVisualizationOptions(self, request, context):
        response = visualizer_service.VisualizationOptionsResponse()
        for option, _ in self._visualizations.values():
            proto_option = response.visualization_options.add(visualization_name=option.visualization_name, chart_type=option.chart_type)
            proto_option.visualization_input_schema.CopyFrom(self._schema_to_proto(option.visualization_input_schema))
            proto_option.visualization_settings_schema.CopyFrom(self._schema_to_proto(option.visualization_settings_schema))

        return response

    @staticmethod
    def _request_to_python(request) -> VisualizationRequest:
        return VisualizationRequest(
            visualization_name=request.visualization_name,
            visualization_data=[VisualizationDataPoint(index=point.index, values=ares_struct_utils.ares_struct_to_dict(point.values),) for point in request.visualization_data]
        )

    def _get_logic(self, visualization_name: str) -> VisualizationLogicFunction:
        registered = self._visualizations.get(visualization_name)
        if registered is not None:
            return registered[1]
        if self._custom_visualization_logic is not None:
            return self._custom_visualization_logic
        raise KeyError(f"No visualization named '{visualization_name}' is registered")

    @staticmethod
    def _chart_to_json(chart: VisualizationResult) -> str:
        if isinstance(chart, str):
            return chart
        
        if isinstance(chart, Mapping):
            return json.dumps(chart)

        # Plotly Figure exposes to_json(), so no hard import is needed here.
        to_json = getattr(chart, "to_json", None)
        if callable(to_json):
            serialized = to_json()
            if not isinstance(serialized, str):
                raise TypeError("Plotly Figure.to_json() must return a string")
            return serialized
        raise TypeError("Visualization callbacks must return chart JSON, a mapping, or a Plotly Figure")

    def _render(self, request) -> str:
        python_request = self._request_to_python(request)
        result = self._get_logic(request.visualization_name)(python_request)
        return self._chart_to_json(self._resolve_awaitable(result))

    @staticmethod
    def _set_internal_error(context, message: str) -> None:
        if context is not None:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(message)

    def RequestUpdatedVisualization(self, request, context):
        response = visualizer_service.GetUpdatedVisualResponse()
        try:
            response.chart_json_data = self._render(request)
        except Exception as exc:
            self._set_internal_error(context, f"Error generating visualization: {exc}")
        return response

    def StreamPlotlyVisualization(self, request, context):
        try:
            python_request = self._request_to_python(request)
            result = self._resolve_awaitable(self._get_logic(request.visualization_name)(python_request))

            is_chart = callable(getattr(result, "to_json", None))
            if isinstance(result, Iterable) and not isinstance(result, (str, bytes, Mapping)) and not is_chart:
                charts = result

            else:
                charts = (result,)

            for chart in charts:
                yield visualizer_service.GetUpdatedVisualResponse(chart_json_data=self._chart_to_json(chart))
                
        except Exception as exc:
            self._set_internal_error(context, f"Error streaming visualization: {exc}")


class AresVisualizerService(AresBaseService):
    """Manage a gRPC server hosting one or more remote visualizations."""

    def __init__(
        self,
        name: str,
        version: str,
        description: str = "",
        timeout: int = 30,
        use_localhost: bool = True,
        port: int = 7084,
        max_message_size: int = -1,
    ):
        super().__init__(
            service_name=name,
            description=description,
            version=version,
            port=port,
            use_localhost=use_localhost,
            max_message_size=max_message_size,
        )

        self._service_wrapper = AresVisualizerServiceWrapper(
            name=name,
            version=version,
            description=description,
            timeout=timeout
        )

        visualizer_service_grpc.add_RemoteVisualizerServiceServicer_to_server(self._service_wrapper, self.get_server())

    def add_visualization(self,
        visualization_name: str,
        custom_visualization_logic: VisualizationLogicFunction,
        visualization_input_schema: Optional[dict[str, AresSchemaEntry]] = None,
        visualization_settings_schema: Optional[dict[str, AresSchemaEntry]] = None,
        chart_type: str = "") -> None:
        """Advertise a visualization and register its rendering callback."""
        self._service_wrapper.add_visualization(
            VisualizationOption(
                visualization_name=visualization_name,
                visualization_input_schema=visualization_input_schema,
                visualization_settings_schema=visualization_settings_schema,
                chart_type=chart_type,
            ),
            custom_visualization_logic,
        )