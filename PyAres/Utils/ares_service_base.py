import grpc
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

class AresServiceWrapperBase:
    """
    Base class for ARES gRPC service wrappers to provide common connection and info methods.
    """
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
                description=self._description
            )
        except Exception as e:
            return connection_info_pb2.InfoResponse(
                name="ERROR",
                version="ERROR",
                description=f"Error fetching information: {e}"
            )

    def GetState(self, request, context) -> connection_state_pb2.StateResponse:
        try:
            return connection_state_pb2.StateResponse(
                state=connection_state_pb2.State.ACTIVE, 
                state_message=f"{self._service_name} is active!"
            )
        except Exception as e:
            return connection_state_pb2.StateResponse(
                state=connection_state_pb2.State.ERROR, 
                state_message=f"Exception while trying to respond to ARES with state! {e}"
            )

    def GetConnectionStatus(self, request, context) -> connection_status_pb2.ConnectionStatus:
        try:
            return connection_status_pb2.ConnectionStatus(
                status=connection_status_pb2.AresStatus.CONNECTED
            )
        except Exception as e:
            # Note: connection_status_pb2 might not have a way to return an error status in the same way.
            # We return a disconnected status or let gRPC handle the exception.
            return connection_status_pb2.ConnectionStatus(
                status=connection_status_pb2.AresStatus.DISCONNECTED
            )

    def _resolve_awaitable(self, result: Any) -> Any:
        """
        Helper to resolve awaitables if the custom logic is async.
        """
        if inspect.isawaitable(result):
            async def resolve(awaitable):
                return await awaitable
            return asyncio.run(resolve(result))
        return result

class AresBaseService(AresGrpcServiceBase):
    """
    Base class for ARES services to handle common management logic like settings and timeouts.
    """
    def __init__(self, 
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
            max_message_size=max_message_size
        )

    def add_setting(self, 
                    setting_name: str, 
                    setting_type: Any, 
                    default_value: Any = None, 
                    optional: bool = True, 
                    constraints: Union[list, None] = None, 
                    struct_schema: Optional[Dict] = None, 
                    limits: Optional[Any] = None, 
                    description: Optional[str] = None):
        """
        Adds a setting to the service wrapper's settings schema.
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
                    limits=limits, 
                    default_value=default_ares_value,
                    description=description
                )
            else:
                self._service_wrapper._settings[setting_name] = ares_data_schema_utils.create_settings_schema_entry(
                    setting_type=setting_type, 
                    optional=optional, 
                    choices=choices, 
                    struct_schema=struct_schema, 
                    limits=limits, 
                    description=description
                )
        except Exception as e:
            self._logger.error(f"Encountered an exception while adding setting {setting_name}: {e}")

    def set_timeout(self, new_timeout: int):
        """
        Sets the timeout for the service wrapper.
        """
        self._service_wrapper._timeout = new_timeout