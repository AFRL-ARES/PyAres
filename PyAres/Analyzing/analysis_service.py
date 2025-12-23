# Standard Imports
import grpc
from concurrent import futures
from typing import Callable, Awaitable, Union, Mapping, Dict

# Import generated protobuf and gRPC stubs
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2 as analyzer_service
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2_grpc as analyzer_service_grpc
from ares_datamodel.analyzing import analysis_pb2
from ares_datamodel.analyzing import analyzer_capabilities_pb2
from ares_datamodel.connection import connection_state_pb2
from ares_datamodel.connection import connection_status_pb2
from ares_datamodel.connection import connection_info_pb2
from ares_datamodel import ares_data_type_pb2
from ares_datamodel import ares_data_schema_pb2
from ares_datamodel import ares_outcome_enum_pb2

# Import Utilities
from ..Utils import ares_struct_utils
from ..Utils import ares_data_schema_utils
from ..Utils import ares_outcome_utils

# Import python models
from ..Models import ares_data_models, RequestMetadata
from .analyzer_models import AnalysisRequest, Analysis, InfoResponse

# Type hints for the user's custom logic
AnalyzeLogicFunction = Callable[[AnalysisRequest], Union[Analysis, Awaitable[Analysis]]]

class AresAnalyzerServiceWrapper(analyzer_service_grpc.AresRemoteAnalyzerServiceServicer):
    """
    A wrapper around the gRPC service to expose native Python objects for analysis.
    """
    def __init__(self, info: InfoResponse, timeout: int, custom_analysis_logic: AnalyzeLogicFunction):
        self._info = info
        self._timeout = timeout
        self._custom_analysis_logic = custom_analysis_logic
        self._settings: Dict[str, ares_data_schema_pb2.SchemaEntry] = {}
        self._analysis_parameters: Dict[str, ares_data_schema_pb2.SchemaEntry] = {}

    def GetInfo(self, request, context) -> connection_info_pb2.InfoResponse:
        print("Info Requested!")
        try:
            response = connection_info_pb2.InfoResponse(
            name=self._info.name,
            version=self._info.version,
            description=self._info.description)
        
            return response

        except Exception as e:
            response = connection_info_pb2.InfoResponse(
                name="ERROR",
                version="ERROR",
                description="Error fetching information"
            )
            print(f"Exception while trying to respond to ARES with information! {e}")
            return response


    def Analyze(self, request: analyzer_service.AnalysisRequest, context) -> analysis_pb2.Analysis:
        print("Received an analysis request!")
        try:
            python_request = AnalysisRequest(
                inputs=ares_struct_utils.ares_struct_to_dict(request.inputs),
                settings=ares_struct_utils.ares_struct_to_dict(request.settings),
                metadata=RequestMetadata(request.metadata)
            )

            proto_analysis = analysis_pb2.Analysis()
            python_response = self._custom_analysis_logic(python_request)
            if isinstance(python_response, Awaitable):
                python_response = python_response.__await__()

            if not isinstance(python_response, Analysis):
                print("Analysis response was an invalid type, ")
                proto_analysis.analysis_outcome = ares_outcome_enum_pb2.FAILURE
                proto_analysis.error_string = "The user's custom analysis logic returned an invalid type, analysis cannot be processed"
                return proto_analysis
            
            print("Sending Analysis Response.....")
            return analysis_pb2.Analysis(
                result=python_response.result,
                analysis_outcome=ares_outcome_utils.python_ares_outcome_to_proto_ares_outcome(python_response.outcome),
                error_string=python_response.error_string
            )
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error in custom analysis logic: {e}")
            return analysis_pb2.Analysis(analysis_outcome=ares_outcome_enum_pb2.FAILURE, error_string=str(e))
        
    def GetState(self, request, context) -> connection_state_pb2.StateResponse:
        try:
            analyzer_state = connection_state_pb2.StateResponse(state=connection_state_pb2.State.ACTIVE)
            return analyzer_state
        
        except Exception as e:
            print(f"{e}")
            return connection_state_pb2.StateResponse(state=connection_state_pb2.State.ERROR, state_message=f"Exception while trying to respond to ARES with state! {e}")


    def GetAnalysisParameters(self, request, context):
        print("Analysis Parameters Requested")
        try:
            analysisParamResponse = analyzer_service.AnalysisParametersResponse()

            for key, value in self._analysis_parameters.items():
                map_entry = analysisParamResponse.parameter_schema.fields[key]
                map_entry.CopyFrom(value)

            return analysisParamResponse
    
        except Exception as e:
            print(f"Exception while trying to respond to ARES with analysis parameters! {e}")

    def GetAnalyzerCapabilities(self, request, context) -> analyzer_capabilities_pb2.AnalyzerCapabilities:
        print("Capabilities Requested!")
        capabilities = analyzer_capabilities_pb2.AnalyzerCapabilities(timeout_seconds=self._timeout)
        try:
            for(key, value) in self._settings.items():
                settings_entry = capabilities.settings_schema.fields[key]
                settings_entry.type = value.type
                settings_entry.optional = value.optional

                if len(value.string_choices.strings) != 0:
                    settings_entry.string_choices.strings.extend(value.string_choices.strings)

                elif len(value.number_choices.numbers) != 0:
                    settings_entry.number_choices.numbers.extend(value.number_choices.numbers)
            
            return capabilities

        except Exception as e:
            print(f"Exception while trying to respond to ARES capabilities request! {e}") 
            return capabilities
        
    def GetConnectionStatus(self, request, context):
        try:
            return connection_status_pb2.ConnectionStatus(status=connection_status_pb2.AresStatus.CONNECTED)

        except Exception as e:
            print(f"Exception while trying to respond to ARES with connection status! {e}")

    def ValidateInputs(self, request: analyzer_service.ParameterValidationRequest, context): 
        print("Validating Inputs")
        response = analyzer_service.ParameterValidationResult(success=True)
        provided_params: Mapping[str, ares_data_schema_pb2.SchemaEntry] = request.input_schema.fields

        for stored_key, stored_schema in self._analysis_parameters.items():
            print(f"LOOKING AT {stored_key}")
            if stored_key in provided_params:
                matching_schema = provided_params[stored_key]
                if stored_schema.type != matching_schema.type:
                    print(f" THIS IS THE TYPE RIGHT HERE LOOK AT IT: {type(matching_schema)}")
                    message = f"Schema Mismatch! {stored_key} was provided with the value type {stored_schema.type}, but the value type {matching_schema} was expected!"
                    response.messages.append(message)
                    print(message)
            else:
                if not stored_schema.optional:
                    message = f"Schema Missing! {stored_key} is marked as a required piece of data for analysis, but no assignment was found in the provided schema!"
                    response.messages.append(message)
                    print(message)

        if len(response.messages) != 0:
            response.success = False

        return response
 
class AresAnalyzerService:
    """
    Manages the gRPC server for the AresAnalyzerService.
    """
    def __init__(self,
                 custom_analysis_logic: AnalyzeLogicFunction,
                 name: str,
                 version: str,
                 description: str = "",
                 timeout: int = 30,
                 use_localhost: bool = True,
                 port: int = 7083,
                 max_message_size: int = -1):
        """
        Initializes the AresAnalyzerService.

        Args:
            custom_analysis_logic (`AnalyzeLogicFunction`): A callable function that will be executed when an Analysis request is received.
                This function should accept a `PyAres.Analyzing.AnalysisRequest` object and return a
                `PyAres.Analyzing.Analysis` object (or an awaitable that resolves to one).
            name (str): The name of your analyzer.
            version (str): The version of your analyzer.
            description (str): A brief description of your analyzer.
            use_localhost (bool): If true, binds to localhost. Otherwise, binds to [::].
            port (int): The port that your analyzer service will serve on. Defaults to port 7083.
            max_message_size (int): The max size, in megabytes, of the messages your Analysis service is capable of sending. Increasing this can help transfer data like images, but may result in some loss in performance
        """

        self.info = InfoResponse(name=name, version=version, description=description)
        self._capabilities = analyzer_capabilities_pb2.AnalyzerCapabilities(settings_schema={})
        self._port = port
        server_options = []
        if max_message_size != -1:
            print("Setting Custom Max Message Size")
            server_options.append(('grpc.max_receive_message_length', max_message_size * 1024 * 1024))
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=server_options)
        self._service_wrapper = AresAnalyzerServiceWrapper(info=self.info, timeout=timeout, custom_analysis_logic=custom_analysis_logic)
        analyzer_service_grpc.add_AresRemoteAnalyzerServiceServicer_to_server(self._service_wrapper, self._server)

        if use_localhost:
            self._server.add_insecure_port(f'localhost:{self._port}')
        else:
            self._server.add_insecure_port(f'[::]:{self._port}')

    def add_setting(self, setting_name: str, setting_type: ares_data_models.AresDataType, optional: bool = True, constraints: Union[list[int], list[str], list[float]] = []):
        """
        Adds an analyzer setting to be reported to ARES when capabilities are requested.
        While most `PyAres.Models.AresDataType` options are supported, bool arrays and byte arrays
        cannot be used as the type for your setting values.

        Args:
            setting_name (str): The name of the setting.
            setting_type (AresDataType): The type of this settings value.
            optional (bool): Whether the setting is optional.
            constraints: An optional list of values to constrain the available setting choices. Can be integers, strings, or floats.
        """
        self._service_wrapper._settings[setting_name] = ares_data_schema_utils.create_settings_schema_entry(setting_type, optional, constraints)

    def add_analysis_parameter(self, parameter_name: str, parameter_type: ares_data_models.AresDataType, optional: bool = False):
        """
        Adds an analysis parameter that will be reported to ARES. Analysis parameters are inputs your analyzer accepts from ARES, and will be mapped to command outputs
        in experiment scripts.

        Args:
            parameter_name (str): The name of the parameter being created.
            parameter_type (AresDataType): The type associated with the new parameter.
            optional (bool): Defaults to false. Determines whether your analyzer requires this information.
        """
        self._service_wrapper._analysis_parameters[parameter_name] = ares_data_schema_utils.create_settings_schema_entry(parameter_type, optional, [])

    def set_timeout(self, new_timeout: int):
        """
        Sets the time, in seconds, that ARES will wait to receive a response from this service.

        Args:
            new_timeout: The new timeout value in seconds.
        """
        self._capabilities.timeout_seconds = new_timeout

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
        """
        Stops the service, terminating the connection.
        """
        print("Stopping Ares Analyzer Service...")
        self._server.stop(0).wait()









