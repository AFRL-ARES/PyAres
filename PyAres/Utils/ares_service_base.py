import asyncio
import inspect
from typing import Any, Optional, Union, Dict

from ares_datamodel.connection import connection_state_pb2
from ares_datamodel.connection import connection_info_pb2
from ares_datamodel.connection import connection_status_pb2
from ares_datamodel import ares_data_schema_pb2

from .grpc_base import AresGrpcServiceBase
from . import ares_value_utils
from . import ares_data_schema_utils
from ..Models.ares_data_models import AresSchemaEntry, Limits


class AresServiceWrapperBase:
    """Base class for ARES gRPC service wrappers to provide common connection and info methods."""

    def __init__(self, service_name: str, version: str, description: str, timeout: int):
        self._service_name = service_name
        self._version = version
        self._description = description
        self._timeout = timeout
        self._settings: Dict[str, ares_data_schema_pb2.AresValueSchema] = {}

    def GetInfo(self, request, context) -> connection_info_pb2.InfoResponse:
        try:
            return connection_info_pb2.InfoResponse(
                name=self._service_name,
                version=self._version,
                description=self._description,
            )
        except Exception as e:
            return connection_info_pb2.InfoResponse(
                name="ERROR",
                version="ERROR",
                description=f"Error fetching information: {e}",
            )

    def GetState(self, request, context) -> connection_state_pb2.StateResponse:
        try:
            return connection_state_pb2.StateResponse(
                state=connection_state_pb2.State.ACTIVE,
                state_message=f"{self._service_name} is active!",
            )
        except Exception as e:
            return connection_state_pb2.StateResponse(
                state=connection_state_pb2.State.ERROR,
                state_message=f"Exception while trying to respond to ARES with state! {e}",
            )

    def GetConnectionStatus(self, request, context) -> connection_status_pb2.ConnectionStatus:
        try:
            return connection_status_pb2.ConnectionStatus(
                status=connection_status_pb2.AresStatus.CONNECTED
            )
        except Exception:
            # If an exception occurs, report a disconnected status.
            return connection_status_pb2.ConnectionStatus(
                status=connection_status_pb2.AresStatus.DISCONNECTED
            )

    def _resolve_awaitable(self, result: Any) -> Any:
        """Helper to resolve awaitables if the custom logic is async."""

        if inspect.isawaitable(result):
            async def resolve(awaitable):
                return await awaitable

            return asyncio.run(resolve(result))
        return result


class AresBaseService(AresGrpcServiceBase):
    """Base class for ARES services to handle common management logic like settings and timeouts."""

    def __init__(
        self,
        service_name: str,
        description: str,
        version: str,
        port: int,
        use_localhost: bool = True,
        max_message_size: int = -1):
        super().__init__(
            service_name=service_name,
            description=description,
            version=version,
            port=port,
            use_localhost=use_localhost,
            max_message_size=max_message_size,
        )

    def add_setting(
        self,
        setting_name: str,
        setting_type: Any,
        default_value: Any = None,
        optional: bool = True,
        constraints: Union[list, None] = None,
        struct_schema: Optional[Dict[str, AresSchemaEntry]] = None,
        list_element_schema: Optional[AresSchemaEntry] = None,
        limits: Optional[Limits] = None,
        description: Optional[str] = None) -> None:
        """Adds a setting to the service wrapper's settings schema.

        This helper is shared by planner, analyzer, and other services. When
        `setting_type` is a LIST, `list_element_schema` can be provided to
        describe the schema for each element in that list.
        """
        try:
            # Ensure constraints is a list if not provided
            choices = constraints if constraints is not None else []

            if default_value is not None:
                default_ares_value = ares_value_utils.create_ares_value(default_value)
                self._service_wrapper._settings[setting_name] = ares_data_schema_utils.create_settings_schema_entry(
                    setting_type=setting_type,
                    optional=optional,
                    choices=choices,
                    struct_schema=struct_schema,
                    list_element_schema=list_element_schema,
                    limits=limits,
                    default_value=default_ares_value,
                    description=description,
                )
            else:
                self._service_wrapper._settings[setting_name] = ares_data_schema_utils.create_settings_schema_entry(
                    setting_type=setting_type,
                    optional=optional,
                    choices=choices,
                    struct_schema=struct_schema,
                    list_element_schema=list_element_schema,
                    limits=limits,
                    description=description,
                )
        except Exception as e:
            self._logger.error(f"Encountered an exception while adding setting {setting_name}: {e}")

    def set_timeout(self, new_timeout: int) -> None:
        """Sets the timeout for the service wrapper."""

        self._service_wrapper._timeout = new_timeout
