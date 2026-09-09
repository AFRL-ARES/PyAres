# Standard Imports
import grpc
from typing import Callable, Awaitable, Union, Mapping, Dict, Optional, List

# Import generated protobuf and gRPC stubs
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2 as analyzer_service
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2_grpc as analyzer_service_grpc
from ares_datamodel.analyzing import analysis_pb2
from ares_datamodel.analyzing import analyzer_capabilities_pb2
from ares_datamodel import ares_data_schema_pb2
from ares_datamodel import ares_outcome_enum_pb2

# Import Utilities
from ..Utils import ares_struct_utils
from ..Utils import ares_data_schema_utils
from ..Utils import ares_outcome_utils
from ..Utils import ares_value_utils
from ..Utils.ares_service_base import AresServiceWrapperBase, AresBaseService

# Import python models
from ..Models import ares_data_models, RequestMetadata, AresSchemaEntry
from .analyzer_models import AnalysisRequest, AnalysisResponse, ObjectiveSchema

# Type hints for the user's custom logic
AnalyzeLogicFunction = Callable[[AnalysisRequest], Union[AnalysisResponse, Awaitable[AnalysisResponse]]]


class AresAnalyzerServiceWrapper(AresServiceWrapperBase, analyzer_service_grpc.AresRemoteAnalyzerServiceServicer):
    """A wrapper around the gRPC service to expose native Python objects for analysis."""

    def __init__(self, name: str, version: str, description: str, timeout: int, custom_analysis_logic: AnalyzeLogicFunction):
        super().__init__(name, version, description, timeout)
        self._custom_analysis_logic = custom_analysis_logic
        self._analysis_parameters: Dict[str, ares_data_schema_pb2.AresValueSchema] = {}
        self._objective_outputs: Dict[str, ares_data_schema_pb2.AresValueSchema] = {}

    def Analyze(self, request: analyzer_service.AnalysisRequest, context) -> analysis_pb2.AnalysisResponse:
        print("Received an analysis request!")
        try:
            python_request = AnalysisRequest(
                inputs=ares_struct_utils.ares_struct_to_dict(request.inputs),
                settings=ares_struct_utils.ares_struct_to_dict(request.settings),
                metadata=RequestMetadata(request.metadata),
            )

            python_response = self._custom_analysis_logic(python_request)
            python_response = self._resolve_awaitable(python_response)

            if not isinstance(python_response, AnalysisResponse):
                print("Analysis response was an invalid type.")
                proto_response = analysis_pb2.AnalysisResponse()
                proto_response.analysis_outcome = ares_outcome_enum_pb2.FAILURE
                proto_response.error_string = (
                    "The user's custom analysis logic returned an invalid type; "
                    "expected AnalysisResponse."
                )
                return proto_response

            if python_response.deprecated_result_usage:
                print(
                    "WARNING: AnalysisResponse(result=...) usage is deprecated and will be "
                    "removed in a future major version. Please construct objectives explicitly."
                )

            print("Sending AnalysisResponse.....")
            proto_response = analysis_pb2.AnalysisResponse()

            for obj in python_response.objectives:
                obj_proto = analysis_pb2.Objective()
                obj_proto.objective_name = obj.objective_name

                ares_value_utils.py_to_ares_value(obj.objective_value, obj_proto.objective_value)

                if obj.objective_metadata:
                    ares_struct_utils.dict_to_ares_struct(
                        obj.objective_metadata, obj_proto.objective_metadata
                    )

                proto_response.objectives.append(obj_proto)

            proto_response.analysis_outcome = ares_outcome_utils.python_ares_outcome_to_proto_ares_outcome(
                python_response.outcome
            )
            proto_response.error_string = python_response.error_string

            return proto_response

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error in custom analysis logic: {e}")
            proto_response = analysis_pb2.AnalysisResponse()
            proto_response.analysis_outcome = ares_outcome_enum_pb2.FAILURE
            proto_response.error_string = str(e)
            return proto_response

    def GetAnalysisParameters(self, request, context):
        print("Analysis Parameters Requested")
        try:
            analysis_param_response = analyzer_service.AnalysisParametersResponse()

            for key, value in self._analysis_parameters.items():
                map_entry = analysis_param_response.parameter_schema.fields[key]
                map_entry.CopyFrom(value)

            return analysis_param_response

        except Exception as e:
            print(f"Exception while trying to respond to ARES with analysis parameters! {e}")

    def GetAnalyzerCapabilities(self, request, context) -> analyzer_capabilities_pb2.AnalyzerCapabilities:
        print("Capabilities Requested!")
        capabilities = analyzer_capabilities_pb2.AnalyzerCapabilities(timeout_seconds=self._timeout)

        try:
            for key, value in self._settings.items():
                settings_entry = capabilities.settings_schema.fields[key]
                settings_entry.CopyFrom(value)

            for key, value in self._objective_outputs.items():
                objective_entry = capabilities.objective_output_schema.fields[key]
                objective_entry.CopyFrom(value)

            return capabilities

        except Exception as e:
            print(f"Exception while trying to respond to ARES capabilities request! {e}")
            return capabilities

    def ValidateInputs(self, request: analyzer_service.ParameterValidationRequest, context):
        response = analyzer_service.ParameterValidationResult(success=True)
        provided_params: Mapping[str, ares_data_schema_pb2.AresValueSchema] = request.input_schema.fields

        for stored_key, stored_schema in self._analysis_parameters.items():
            if stored_key in provided_params:
                matching_schema = provided_params[stored_key]
                if stored_schema.type != matching_schema.type:
                    message = (
                        f"Schema Mismatch! {stored_key} was provided with the value type "
                        f"{stored_schema.type}, but the value type {matching_schema} was expected!"
                    )
                    response.messages.append(message)
            else:
                if not stored_schema.optional:
                    message = (
                        f"Schema Missing! {stored_key} is marked as a required piece of data for analysis, "
                        f"but no assignment was found in the provided schema!"
                    )
                    response.messages.append(message)

        if len(response.messages) != 0:
            response.success = False

        return response


class AresAnalyzerService(AresBaseService):
    """Manages the gRPC server for the AresAnalyzerService."""

    def __init__(
        self,
        custom_analysis_logic: AnalyzeLogicFunction,
        name: str,
        version: str,
        description: str = "",
        timeout: int = 30,
        use_localhost: bool = True,
        port: int = 7083,
        max_message_size: int = -1,
    ):
        """Initializes the AresAnalyzerService."""
        super().__init__(
            service_name=name,
            description=description,
            version=version,
            port=port,
            use_localhost=use_localhost,
            max_message_size=max_message_size,
        )

        self._service_wrapper = AresAnalyzerServiceWrapper(
            name=name,
            version=version,
            description=description,
            timeout=timeout,
            custom_analysis_logic=custom_analysis_logic,
        )
        analyzer_service_grpc.add_AresRemoteAnalyzerServiceServicer_to_server(
            self._service_wrapper, self.get_server()
        )

    def add_analysis_parameter(
        self,
        parameter_name: str,
        parameter_type: ares_data_models.AresDataType,
        optional: bool = False,
        struct_schema: Optional[Dict[str, AresSchemaEntry]] = None,
        list_element_schema: Optional[AresSchemaEntry] = None,
    ) -> None:
        """Adds an analysis parameter that will be reported to ARES.

        If `parameter_type` is LIST, `list_element_schema` can be used to describe
        the shape of each element in that list.
        """
        self._service_wrapper._analysis_parameters[parameter_name] = ares_data_schema_utils.create_settings_schema_entry(
            setting_type=parameter_type,
            optional=optional,
            choices=[],
            struct_schema=struct_schema,
            list_element_schema=list_element_schema,
        )

    def add_objective_output(
        self,
        objective_name: str,
        objective_type: ares_data_models.AresDataType,
        objective_description: str = "",
        optional: bool = False,
        struct_schema: Optional[Dict[str, AresSchemaEntry]] = None,
        list_element_schema: Optional[AresSchemaEntry] = None,
    ) -> None:
        """Adds an analysis objective to the advertised outputs of this analyzer.

        If `objective_type` is LIST, `list_element_schema` can be used to describe
        the schema of each element in that list.
        """
        self._service_wrapper._objective_outputs[objective_name] = ares_data_schema_utils.create_settings_schema_entry(
            setting_type=objective_type,
            optional=optional,
            choices=[],
            struct_schema=struct_schema,
            list_element_schema=list_element_schema,
            description=objective_description,
        )

    def get_objective_schema(self) -> List[ObjectiveSchema]:
        """Return a fresh Python representation of the configured objective schema."""
        schemas: List[ObjectiveSchema] = []
        for name, proto_schema in self._service_wrapper._objective_outputs.items():
            schemas.append(ObjectiveSchema(name, proto_schema))
            
        return schemas

