import grpc
from concurrent import futures
from typing import Callable, Awaitable, Union, Dict

from ares_datamodel.planning.remote import ares_remote_planner_service_pb2 as planner_service
from ares_datamodel.planning.remote import ares_remote_planner_service_pb2_grpc as planner_service_grpc
from ares_datamodel.planning import planner_pb2
from ares_datamodel.planning import planner_settings_pb2
from ares_datamodel.planning import planner_service_capabilities_pb2
from ares_datamodel.planning import plan_pb2
from ares_datamodel import ares_data_schema_pb2
from ares_datamodel import ares_data_type_pb2
from ares_datamodel import ares_outcome_enum_pb2
from ares_datamodel.connection import connection_state_pb2
from ares_datamodel.connection import connection_info_pb2

# Import Utilities
from ..Utils import ares_value_utils
from ..Utils import ares_data_schema_utils
from ..Utils import ares_data_type_utils
from ..Utils import ares_struct_utils
from ..Utils import ares_outcome_utils

# Import python models
from ..Models import ares_data_models
from .planner_models import *

# Type hint for the user's custom planning logic
PlanLogicFunction = Callable[[PlanRequest], Union[PlanResponse, Awaitable[PlanResponse]]]

class AresPlannerServiceWrapper(planner_service_grpc.AresRemotePlannerServiceServicer):
    """
    A wrapper around the gRPC service to expose native Python objects for planning
    """
    def __init__(self, service_name: str, description: str, version: str, timeout: int, custom_plan_logic: PlanLogicFunction):
        self._custom_plan_logic: PlanLogicFunction = custom_plan_logic
        self._service_name: str = service_name
        self._description: str = description
        self._version: str = version
        self._settings: Dict[str, ares_data_schema_pb2.SchemaEntry] = {}
        self._planner_options: list[planner_pb2.Planner] = []
        self._supported_types: list[ares_data_type_pb2.AresDataType] = []
        self._timeout: int = timeout

    def GetPlannerServiceCapabilities(self, request, context) -> planner_service_capabilities_pb2.PlannerServiceCapabilities:
        print("Capabilities Requested!")
        """
        Implements the gRPC Capabilities request method. Responsible for telling ARES what this planner
        service is capable of.
        """
        capabilities = planner_service_capabilities_pb2.PlannerServiceCapabilities(timeout_seconds=self._timeout)
        capabilities.service_name = self._service_name
        capabilities.accepted_types.extend(self._supported_types)
        capabilities.available_planners.extend(self._planner_options)

        for(key, value) in self._settings.items():
            settings_entry: ares_data_schema_pb2.SchemaEntry = capabilities.settings_schema.fields[key]
            settings_entry.type = value.type
            settings_entry.optional = value.optional

            if len(value.string_choices.strings) != 0:
                settings_entry.string_choices.strings.extend(value.string_choices.strings)

            elif len(value.number_choices.numbers) != 0:
                settings_entry.number_choices.numbers.extend(value.number_choices.numbers)

        print("Capabilites Sent!")
        return capabilities
    
    def GetInfo(self, request, context) -> connection_info_pb2.InfoResponse:
        try:
            response = connection_info_pb2.InfoResponse(
                name=self._service_name,
                version=self._version,
                description=self._description
            )

            return response
        
        except Exception as e:
            response = connection_info_pb2.InfoResponse(
                name="ERROR",
                version="ERROR",
                description="Error fetching information"
            )
            print(f"Exception while trying to respond to ARES with information! {e}")
            return response

    def GetState(self, request, context) -> connection_state_pb2.StateResponse:
        try:
            return connection_state_pb2.StateResponse(state=connection_state_pb2.State.ACTIVE, state_message=f"{self._service_name} is active!")
        
        except Exception as e:
            print(f"{e}")
            return connection_state_pb2.StateResponse(state=connection_state_pb2.State.ERROR, state_message=f"Exception while trying to respond to ARES with state! {e}")
 

    
    def GetConnectionStatus(self, request, context):
        try:
            return connection_state_pb2.StateResponse(state=connection_state_pb2.State.ACTIVE, state_message=f"{self._service_name} is active!")

        except Exception as e:
            print(f"Exception while trying to respond to ARES with connection status! {e}")

    
    def Plan(self, request: plan_pb2.PlanningRequest, context) -> plan_pb2.PlanningResponse:
        """
        Implements the gRPC Plan method. This method converts protobuf requests to native Python objects
        before executing the users custom planning logic and converting their response back to protobuf.
        """
        parameters = []
        for proto_param in request.planning_parameters:
            parameters.append(
                PlanningParameter
                (
                    name=proto_param.parameter_name,
                    maximum_value=proto_param.maximum_value,
                    minimum_value=proto_param.minimum_value,
                    param_history=[ParameterHistoryItem(ares_value_utils.ares_value_to_py(val.planned_value), ares_value_utils.ares_value_to_py(val.achieved_value)) for val in proto_param.parameter_history],
                    data_type=ares_data_type_utils.proto_ares_type_to_python_ares_type(proto_param.data_type),
                    is_planned=proto_param.is_planned,
                    is_result=proto_param.is_result,
                    planner_name=proto_param.planner_name,
                    initial_value=ares_value_utils.ares_value_to_py(proto_param.initial_value)
                ))
        
        python_request = PlanRequest(parameters=parameters, 
                                     settings=ares_struct_utils.ares_struct_to_dict(request.adapter_settings), 
                                     analysis_results=list(request.analysis_results),
                                     metadata=RequestMetadata(request.metadata))
        
        #Handle call using the user's custom planning logic 
        response_proto = plan_pb2.PlanningResponse()
        try:
            python_response = self._custom_plan_logic(python_request)
            if isinstance(python_response, Awaitable):
                python_response = python_response.__await__()

        except Exception as e:
            #Handle errors from user's logic
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error in custom planning logic: {e}")
            response_proto.error_string = f"{e}"
            response_proto.planning_outcome = ares_outcome_enum_pb2.FAILURE
            return response_proto
        
        if not isinstance(python_response, PlanResponse):
            response_proto.error_string = "The returned response from the user planning method was not a plan response, and thus was invalid."
            response_proto.planning_outcome = ares_outcome_enum_pb2.FAILURE
            return response_proto
        
        response_proto.planning_outcome = ares_outcome_utils.python_ares_outcome_to_proto_ares_outcome(python_response.outcome)
        response_proto.error_string = python_response.error_string

        for i in range(len(python_response.parameter_names)):
            planned_parameter = plan_pb2.PlannedParameter(parameter_value=ares_value_utils.create_ares_value(python_response.parameter_values[i]))
            planned_parameter.parameter_name = python_response.parameter_names[i]
            new_planned_parameter = response_proto.planned_parameters.add()
            new_planned_parameter.CopyFrom(planned_parameter)

        print("Sending Plan Response.....")
        return response_proto
    
class AresPlannerService:
    """
    Manages the gRPC server for the AresPlannerService
    """
    def __init__(self, custom_plan_logic: PlanLogicFunction, 
                 service_name: str, 
                 service_description: str, 
                 service_version: str, 
                 timeout: int = 30, 
                 use_localhost: bool = True, 
                 port: int = 7082,
                 max_message_size: int = -1):
        """
        Initializes the AresPlannerService

        Args:
            custom_plan_logic (PlanLogicFunction): A callable function that will be executed when a PlanRequest is received.
                This function should accept a 'PyARES.AresPlanning.PlanRequest' object and return a
                'PyARES.AresPlanning.PlanResponse' object (or an awaitable that resolves to one).
            service_name (str): The name descriptor that is associated with your planner service.
            service_description (str): A brief description describing your implementation of the planner service.
            service_version (str): The version of your planner service.
            use_localhost (bool): An optional value that allows the user to specify whether to host the service on the local network. Defaults to True.
            port (int): The port that your planner service will serve on. Defaults to port 7082.
            max_message_size (int): The max size, in megabytes, of the messages your Planning service is capable of sending. Increasing this can help transfer heavy data like images, but may result in some loss in performance
        """
        #Public Values, designed to be accessible to the user
        self.service_name = service_name
        self.service_description = service_description
        self.service_version = service_version

        #Private values, mostly related to the service
        self._port = port
        server_options = []
        if max_message_size != -1:
            print("Setting Custom Max Message Size")
            server_options.append(('grpc.max_receive_message_length', max_message_size * 1024 * 1024))
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=server_options)
        self._service_wrapper = AresPlannerServiceWrapper(service_name, service_description, service_version, timeout, custom_plan_logic)
        planner_service_grpc.add_AresRemotePlannerServiceServicer_to_server(self._service_wrapper, self._server)
        if(use_localhost):
            self._server.add_insecure_port(f'localhost:{self._port}')
        else:
            self._server.add_insecure_port(f'[::]:{self._port}')

    def add_planner_option(self, planner_name: str, planner_description: str, planner_version: str):
        """
        Adds a planner option that is reported to ARES when your services capabilities are requested.

        Args:
            planner_name (str): The dedicated name of your planner.
            planner_description (str): A brief description of your planner that is displayed in ARES.
            planner_version (str): The version of your planner. 
        """
        self._service_wrapper._planner_options.append(planner_pb2.Planner(planner_name=planner_name, description=planner_description, version=planner_version))

    def add_setting(self, setting_name: str, setting_type: ares_data_models.AresDataType, optional: bool = True, constraints: Union[list[int], list[str], list[float]] = []):
        """
        Adds a planner setting to be reported to ARES when your services capabilities are requested.

        Args:
            setting_name (str): The name of the setting.
            setting_type (AresDataType): The type of this settings value.
            optional (bool): Whether the setting is optional.
            constraints: An optional list of values to constrain the available setting choices. Can be integers, strings, or floats.
        """
        self._service_wrapper._settings[setting_name] = ares_data_schema_utils.create_settings_schema_entry(setting_type, optional, constraints)

    def add_supported_type(self, type: ares_data_models.AresDataType):
        """
        Adds the specified type to the list of value types your planenr service accepts.

        Args:
            type (AresDataType): The type being added to the list of allowed types.
        """
        self._service_wrapper._supported_types.append(ares_data_type_utils.python_ares_type_to_proto_ares_type(type))

    def set_timeout(self, new_timeout: int):
        """
        Sets the time, in seconds, that ARES will wait to receive a response from this service.

        Args:
            new_timeout: The time to be assigned as the new timeout value
        """
        self._service_wrapper._timeout = new_timeout

    def start(self, wait_for_termination: bool = True):
        """ 
        Starts the service on the specified port, and waits for termination. 
        
        Args:
        wait_for_termination (bool): A boolean value that determines whether the start method will use the "wait_for_termination" blocking call. 
        If true, the gRPC service will keep the main thread alive but at the cost of blocking any continued execution of your python logic.
        Setting this value to false will allow you to continue execution after starting your service, however this should ONLY be done if you have
        another mechanism for keeping your process alive (such as a GUI, or a loop). Defaults to true.
        """
        print(f"Starting Ares Planning Service on port {self._port}...")
        self._server.start()

        if wait_for_termination:
            self._server.wait_for_termination()

    def stop(self):
        """
        Stops the service, terminating the connection.
        """
        print("Stopping Ares Planning Service...")
        self._server.stop(0).wait()
