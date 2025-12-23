import grpc
import inspect
import time
import warnings
from concurrent import futures
from typing import Dict, Callable, Awaitable, Union, Any

from ares_datamodel.device.remote import ares_remote_device_service_pb2 as device_service
from ares_datamodel.device.remote import ares_remote_device_service_pb2_grpc as device_service_grpc
from ares_datamodel.device import device_status_pb2
from ares_datamodel.device import device_execution_result_pb2
from ares_datamodel.device import device_polling_settings_pb2
from ares_datamodel import ares_data_schema_pb2
from ares_datamodel import ares_struct_pb2
from google.protobuf import empty_pb2

from .device_models import DeviceCommandDescriptor
from ..Utils import ares_device_command_utils
from ..Utils import ares_data_schema_utils
from ..Utils import ares_struct_utils
from ..Utils import ares_value_utils
from ..Utils import ares_data_type_utils

# Type hint for the user's custom methods
EnterSafeModeMethod = Callable[[], None]
DeviceCommandMethod = Callable[..., Dict[str, Any]]
DeviceStateMethod = Callable[[], Dict[str, Any]]

class AresDeviceServiceWrapper(device_service_grpc.AresRemoteDeviceServiceServicer):
  """
  A wrapper around the gRPC service to expose native Python objects for devices
  """

  def __init__(self, device_name: str, description: str, version: str, enter_safe_mode: EnterSafeModeMethod, update_device_state: DeviceStateMethod):
    self.device_name = device_name
    self.description = description
    self.version = version
    self._enter_safe_mode = enter_safe_mode
    self._update_device_state = update_device_state
    self._setting_schema: Dict[str, ares_data_schema_pb2.SchemaEntry] = {}
    self._current_settings: Dict[str, ares_struct_pb2.AresValue] = {}
    self._state_schema: Dict[str, ares_data_schema_pb2.SchemaEntry] = {}
    self._commands: list[DeviceCommandDescriptor] = []
    self._command_methods: Dict[str, Callable] = {}

  def GetOperationalStatus(self, request, context) -> device_status_pb2.DeviceOperationalStatus:
    return device_status_pb2.DeviceOperationalStatus(operational_state=device_status_pb2.OperationalState.ACTIVE, message=f"{self.device_name} is active!")

  def GetInfo(self, request, context) -> device_service.DeviceInfoResponse:
    info = device_service.DeviceInfoResponse()
    info.name = self.device_name
    info.description = self.description
    info.version = self.version
    return info
  
  def GetCommands(self, request, context) -> device_service.CommandsResponse:
    response = device_service.CommandsResponse()

    for command_descriptor in self._commands:
      proto_desc = ares_device_command_utils.python_command_description_to_proto(command_descriptor)
      response.commands.append(proto_desc)

    return response
  
  def ExecuteCommand(self, request: device_service.ExecuteCommandRequest, context) -> device_execution_result_pb2.DeviceExecutionResult:
    response = device_execution_result_pb2.DeviceExecutionResult()

    if request.command_name in self._command_methods:
      method = self._command_methods.get(request.command_name)

      if not isinstance(method, Callable):
        return device_execution_result_pb2.DeviceExecutionResult(success=False, error="Failed to find a valid remote method that corresponds to the requested action.")
      
      method_signature = inspect.signature(method)

      num_parameters: int = len(method_signature.parameters.items())
      num_provided_parameters: int = len(request.arguments.fields)

      if num_parameters != num_provided_parameters:
        response.success = False
        response.error = "Could not execute command as provided parameter count did not match the parameter count of the matching method signature!"
        return response

      #Convert the protobuf map to a Python dictionary
      provided_param_dict = ares_struct_utils.ares_struct_to_dict(request.arguments)
      result : Dict[str, Any] = method(**provided_param_dict)
      
      for key, value in result.items():
        ares_struct_utils.add_value_to_struct(response.result, key, ares_value_utils.create_ares_value(value))
        
      response.success = True
      return response

    else:
      response.success = False
      response.error = "Unable to find requested command, cannot process device command request!"
      return response
  
  def EnterSafeMode(self, request, context) -> None:
    #Handle call using the user's custom safe mode logic 
    try:
        python_response = self._enter_safe_mode()
        if isinstance(python_response, Awaitable):
            python_response = python_response.__await__()

    except Exception as e:
        #Handle errors from user's logic
        context.set_code(grpc.StatusCode.INTERNAL)
        context.set_details(f"Error in safe mode logic: {e}")
  
  def GetSettingsSchema(self, request, context) -> device_service.SettingsSchemaResponse:
    response = device_service.SettingsSchemaResponse()
    for key, value in self._setting_schema.items():
      settings_entry = response.schema.fields[key]
      settings_entry.type = value.type
      settings_entry.optional = value.optional

      if len(value.string_choices.strings) != 0:
        settings_entry.string_choices.strings.extend(value.string_choices.strings)

      elif len(value.number_choices.numbers) != 0:
        settings_entry.number_choices.numbers.extend(value.number_choices.numbers)

    return response

  def GetCurrentSettings(self, request, context) -> device_service.CurrentSettingsResponse:
    response = device_service.CurrentSettingsResponse()
    try:
      for key, value in self._current_settings.items():
        new_entry = response.settings.fields[key]
        new_entry.CopyFrom(value)

      return response
    
    except Exception as e:
      print(f"EXCEPTION CAUGHT: {e}")
      return response
  
  def SetSettings(self, request: device_service.SetSettingsRequest, context) -> empty_pb2.Empty:
    for key, value in request.settings.fields.items():
      if key in self._current_settings:
        self._current_settings[key] = value

    return empty_pb2.Empty()
  
  def GetStateSchema(self, request, context) -> device_service.StateSchemaResponse:
    response = device_service.StateSchemaResponse()
    for key, value in self._state_schema.items():
      settings_entry = response.schema.fields[key]
      settings_entry.type = value.type
      settings_entry.optional = value.optional

      if len(value.string_choices.strings) != 0:
        settings_entry.string_choices.strings.extend(value.string_choices.strings)

      elif len(value.number_choices.numbers) != 0:
        settings_entry.number_choices.numbers.extend(value.number_choices.numbers)

    return response
  
  def GetState(self, request, context) -> device_service.DeviceStateResponse:
    response = self._update_device_state()
    if isinstance(response, Awaitable):
      response = response.__await__()

    proto_response = device_service.DeviceStateResponse()
    proto_response.state = ares_struct_pb2.AresStruct()

    if not isinstance(response, Dict):
      print("State Response was invalid. All state responses should be returned in the form of a dictionary.")
      return proto_response
    
    for key, value in response.items():
      ares_struct_utils.add_value_to_struct(proto_response.state, key, ares_value_utils.create_ares_value(value))

    return proto_response
      
  def GetStateStream(self, request: device_service.DeviceStateStreamRequest, context):
    """ A server-side streaming RPC method that yields device states. """
    polling_info: device_polling_settings_pb2.DevicePollingSettings = request.polling_settings

    try:
      if polling_info.polling_type == device_polling_settings_pb2.PollingType.INTERVAL:
        delay = polling_info.interval_ms/1000
        while True:
          if context.is_active() == False:
            print("Client for ARES device has disconnected.")
            break
          
          response = self._update_device_state()
          if isinstance(response, Awaitable):
            response = response.__await__()

          proto_response = device_service.DeviceStateResponse()

          if not isinstance(response, Dict):
            print("State Response was invalid. All state responses should be returned in the form of a dictionary.")
            return proto_response

          for key, value in response.items():
            ares_struct_utils.add_value_to_struct(proto_response.state, key, ares_value_utils.create_ares_value(value))

          yield proto_response
          time.sleep(delay)
      
      else:
        print("Probably do something here...")


    except grpc.RpcError as e:
      print(f"gRPC error occured in device state stream")

class AresDeviceService:
  """ Manages the gRPC service for the AresDeviceSerivce """
  def __init__(self, 
               enter_safe_mode_logic: EnterSafeModeMethod, 
               get_device_state_logic: DeviceStateMethod, 
               device_name: str,
               description: str, 
               version: str, 
               use_localhost: bool = True, 
               port: int = 7100):
    """
    Initializes the AresDeviceService
    
    Args:
      enter_safe_mode_logic: A callable function that will be executed when the device is instructed to enter safe mode.
        This logic should put your device in a stable state, for instance telling a furnace to return to ambient temperature.
      get_device_state_logic: A callable function that handles gathering device state information for logging purposes. This function
        should return a dictionary containing the keys and values that define your devices state.
      device_name (str): The name description of your device.
      description (str): A brief description of your device.
      version (str): The version associated with your device implementation.
      use_localhost (bool): An optional value that allows the user to specify whether to host the service on the local network. Defaults to True.
      port (int): The port that your device service will serve on. Defaults to port 7100.
    """

    self.device_name = device_name
    self.description = description
    self.version = version

    self._port = port
    self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    self._service_wrapper = AresDeviceServiceWrapper(device_name, description, version, enter_safe_mode_logic, get_device_state_logic)
    device_service_grpc.add_AresRemoteDeviceServiceServicer_to_server(self._service_wrapper, self._server)
    if(use_localhost):
      self._server.add_insecure_port(f'localhost:{self._port}')
    else:
      self._server.add_insecure_port(f'[::]:{self._port}')

  def add_new_command(self, cmd_descriptor: DeviceCommandDescriptor, method):
    """
    Adds a new command for use with this device that is reported to ARES.

    Args:
      cmd_descriptor (`PyAres.Device.DeviceCommandDescriptor`): A DeviceCommandDescriptor object that contains all the necessary information that ARES needs about your command.
      method (Callable[..., Dict[str, any]]): Your command method. This method can take in any number of arguments, but should always return a dictionary of it's results.
    """
    method_signature = inspect.signature(method)
    num_method_parameters: int = len(method_signature.parameters.items())
    num_desc_parameters: int = len(cmd_descriptor.input_schema.items())

    if num_method_parameters != num_desc_parameters:
      warnings.warn(f"A mismatch in the number of input parameters your command method {method.__name__} and command descriptor expects was detected! This may result in unexpected behavior!")

    self._service_wrapper._command_methods[cmd_descriptor.name] = method
    self._service_wrapper._commands.append(cmd_descriptor)

  def add_setting(self, setting_name: str, setting_value: Any, optional: bool = True, constraints: Union[list[int], list[str], list[float]] = []):
    """
    Adds a new device setting to be reported to ARES when your devices capabilities are requested.

    Args:
      setting_name (str): The name of the setting.
      setting_value (Any): The default value of the setting
      optional (bool): Whether the setting is optional
      constraints: An optional list of values to constrain the available setting choices. Can be integers, floats, or strings.
    """
    setting_type = ares_data_type_utils.determine_python_ares_data_type(setting_value)
    self._service_wrapper._setting_schema[setting_name] = ares_data_schema_utils.create_settings_schema_entry(setting_type, optional, constraints)
    new_ares_value = ares_value_utils.create_ares_value(setting_value)
    self._service_wrapper._current_settings[setting_name] = new_ares_value

  def start(self, wait_for_termination: bool = True):
    """ 
    Starts the service on the specified port, and waits for termination. 
    
    Args:
      wait_for_termination (bool): A boolean value that determines whether the start method will use the "wait_for_termination" blocking call. 
      If true, the gRPC service will keep the main thread alive but at the cost of blocking any continued execution of your python logic.
      Setting this value to false will allow you to continue execution after starting your service, however this should ONLY be done if you have
      another mechanism for keeping your process alive (such as a GUI, or a loop). Defaults to true.
    """
    print(f"Starting Ares Device Service on port {self._port}...")
    self._server.start()

    if wait_for_termination:
      self._server.wait_for_termination()

  def stop(self):
    """ Stops the service, terminating the connection. """
    print("Stopping Ares Device Service...")
    self._server.stop(0).wait()    
