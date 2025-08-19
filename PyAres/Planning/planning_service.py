import grpc
from concurrent import futures
from typing import Callable, Awaitable, Union

# Import generated protobuf and gRPC stubs
from .messages import ares_planner_pb2
from .messages import ares_planner_pb2_grpc

from .models import PlanningParameter, PlanRequest, PlanResponse

#Type hint for the user's custom planning logic
#Receives a PlanRequest and returns a PlanResponse
PlanLogicFunction = Callable[[PlanRequest], Union[PlanResponse, Awaitable[PlanResponse]]]

class AresPlannerServiceWrapper(ares_planner_pb2_grpc.AresPlannerGrpcServicer):
    """
    A wrapper around the gRPC service to expose native Python objects for planning
    """
    def __init__(self, service_name: str, custom_plan_logic: PlanLogicFunction):
        self._custom_plan_logic = custom_plan_logic
        self._service_name = service_name
        self._timeout = 30

        #Storage of planners and settings
        self._hosted_planners = []
        self._service_settings = []

    def AddPlannerOption(self, planner_name: str, planner_description: str, planner_version: str):
        new_planner = ares_planner_pb2.Planner(planner_name=planner_name, description=planner_description, version=planner_version)
        self._hosted_planners.append(new_planner)

    def AddPlannerSetting(self, setting_name: str, setting_value):
        new_setting = ares_planner_pb2.PlannerSetting(setting_name=setting_name)
        new_setting = SetValueOfSetting(new_setting, setting_value)
        self._service_settings.append(new_setting)

    def SetTimeout(self, new_timeout: int):
        self._timeout = new_timeout

    def RequestCapabilities(self, request, context) -> ares_planner_pb2.Capabilities:
        print("Capabilities Requested!")
        """
        Implements the gRPC Capabilities request method. Responsible for telling ARES what this planner
        service is capable of.
        """
        response = ares_planner_pb2.Capabilities(service_name=self._service_name, timeout_seconds=self._timeout, available_planners=self._hosted_planners, adapter_settings=self._service_settings)
        return response
    
    def Plan(self, request: ares_planner_pb2.PlanRequest, context) -> ares_planner_pb2.PlanResponse:
        """
        Implements the gRPC Plan method. This method converts protobuf requests to native Python objects
        before executing the users custom planning logic and converting their response back to protobuf.
        """
        print("Received a plan request!")
        parameters = []
        for proto_param in request.planning_parameters:
            parameters.append(
                PlanningParameter
                (
                    name=proto_param.parameter_name,
                    value=proto_param.parameter_value,
                    maxiumum_value=proto_param.maximum_value,
                    minimum_value=proto_param.minimum_value,
                    param_history=proto_param.parameter_history,
                    data_type=proto_param.data_type,
                    is_planned=proto_param.is_planned,
                    is_result=proto_param.is_result,
                    planner_name=proto_param.planner_name
                ))
        
        python_request = PlanRequest(parameters=parameters)
        
        #Handle call using the user's custom planning logic 
        try:
            python_response = self._custom_plan_logic(python_request)
            if isinstance(python_response, Awaitable):
                python_response = python_response.__await__()

        except Exception as e:
            #Handle errors from user's logic
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error in custom planning logic: {e}")
        
        response_proto = ares_planner_pb2.PlanResponse()
        
        for value in python_response.parameter_values:
            response_proto.parameter_values.append(value)

        for name in python_response.parameter_names:
            response_proto.parameter_names.append(name)

        print("Sending Plan Response.....")
        return response_proto
    
class AresPlannerService:
    """
    Manages the gRPC server for the AresPlannerService
    """
    def __init__(self, custom_plan_logic: PlanLogicFunction, service_name: str, service_description: str, service_version: str, use_localhost: bool = True, port: int = 7082):
        """
        Initializes the AresPlannerService

        Args:
            custom_plan_logic: A callable function that will be executed when a PlanRequest is received.
                This function should accept a 'PyARES.AresPlanning.PlanRequest' object and return a
                'PyARES.AresPlanning.PlanResponse' object (or an awaitable that resolves to one).
            service_name: The name descriptor that is associated with your planner service.
            service_description: A brief description describing your implementation of the planner service.
            service_version: The version of your planner service.
            port: The port that your planner service will serve on. Defaults to port 7082.
        """
        #Public Values, designed to be accessible to the user
        self.service_name = service_name
        self.service_description = service_description
        self.service_version = service_version

        #Private values, mostly related to the service
        self._port = port
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self._service_wrapper = AresPlannerServiceWrapper(service_name, custom_plan_logic)
        ares_planner_pb2_grpc.add_AresPlannerGrpcServicer_to_server(self._service_wrapper, self._server)
        if(use_localhost):
            self._server.add_insecure_port(f'localhost:{self._port}')
        else:
            self._server.add_insecure_port(f'[::]:{self._port}')

    def AddPlannerOption(self, planner_name: str, planner_description: str, planner_version: str):
        """
        Adds a planner option that is reported to ARES when your services capabilities are requested.

        Args:
            planner_name: The dedicated name of your planner. ARES will use this to identify which
                planning method within your service was selected for use.
            planner_description: A brief description of your planner that is displayed in ARES.
            planner_version: The version of your planner. 
        """
        self._service_wrapper.AddPlannerOption(planner_name, planner_description, planner_version)
        print(f"Successfully added {planner_name} as a planner option!")

    def AddPlannerSetting(self, setting_name: str, setting_value):
        """
        Adds a planner setting to be reported to ARES when your services capabilities are requested.

        Args:
            setting_name: The name descriptor of your setting.
            setting_value: The value associated with your setting, also tells ARES what the type of your
                setting value is.
        """
        self._service_wrapper.AddPlannerSetting(setting_name, setting_value)
        print(f"Successfully added new setting {setting_name}")

    def SetTimeout(self, new_timeout: int):
        """
        Sets the time, in seconds, that ARES will wait to receive a response from this service.

        Args:
            new_timeout: The time to be assigned as the new timeout value
        """
        self._service_wrapper.SetTimeout(new_timeout)

    def start(self):
        """
        Starts the service on the specified port, and waits for termination.
        """
        print(f"Starting Ares Planner Service on port {self._port}...")
        self._server.start()
        self._server.wait_for_termination()

    def stop(self):
        """
        Stops the service, terminating the connection.
        """
        print("Stopping Ares Planning Service...")
        self._server.stop(0).wait()

def SetValueOfSetting(setting: ares_planner_pb2.PlannerSetting, setting_value) -> ares_planner_pb2.PlannerSetting: 
    if(isinstance(setting_value, str)):
        setting.setting_value.string_value = setting_value
    
    elif(isinstance(setting_value, float)):
        setting.setting_value.float_value = setting_value
    
    elif(isinstance(setting_value, bool)):
        setting.setting_value.bool_value = setting_value

    return setting