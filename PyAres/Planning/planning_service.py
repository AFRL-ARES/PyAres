import grpc
import inspect
import asyncio
from concurrent import futures
from typing import Callable, Awaitable, Union, Dict

from ares_datamodel.planning.remote import ares_remote_planner_service_pb2_grpc as planner_service_grpc
from ares_datamodel.planning import planner_pb2
from ares_datamodel.planning import planner_service_capabilities_pb2
from ares_datamodel.planning import plan_pb2
from ares_datamodel import ares_data_schema_pb2
from ares_datamodel import ares_data_type_pb2
from ares_datamodel import ares_outcome_enum_pb2
from ares_datamodel.connection import connection_state_pb2
from ares_datamodel.connection import connection_info_pb2
from ares_datamodel import ares_struct_pb2

# Import Utilities
from ..Utils import ares_value_utils
from ..Utils import ares_data_schema_utils
from ..Utils import ares_data_type_utils
from ..Utils import ares_struct_utils
from ..Utils import ares_plan_status_code_utils
from ..Utils import plan_response_utils
from ..Utils.ares_service_base import AresServiceWrapperBase, AresBaseService
from ..Utils.logging_utils import setup_logger

# Import python models
from ..Models import ares_data_models, Limits
from .planner_models import *
from ..Analyzing.analyzer_models import Objective

# Type hint for the user's custom planning logic
PlanLogicFunction = Callable[[PlanRequest], Union[PlanResponse, Awaitable[PlanResponse], List[Plan], Awaitable[List[Plan]]]]

class AresPlannerServiceWrapper(AresServiceWrapperBase, planner_service_grpc.AresRemotePlannerServiceServicer):
    """
    A wrapper around the gRPC service to expose native Python objects for planning
    """
    def __init__(self, service_name: str, version: str, description: str, timeout: int, custom_plan_logic: PlanLogicFunction):
        super().__init__(service_name, version, description, timeout)
        self._custom_plan_logic: PlanLogicFunction = custom_plan_logic
        self._current_settings: Dict[str, ares_struct_pb2.AresValue] = {}
        self._planner_options: list[planner_pb2.Planner] = []
        self._supported_types: list[ares_data_type_pb2.AresDataType] = []

    def GetPlannerServiceCapabilities(self, request, context) -> planner_service_capabilities_pb2.PlannerServiceCapabilities:
        print("Capabilities Requested!")
        capabilities = planner_service_capabilities_pb2.PlannerServiceCapabilities(timeout_seconds=self._timeout)
        capabilities.service_name = self._service_name
        capabilities.accepted_types.extend(self._supported_types)
        capabilities.available_planners.extend(self._planner_options)

        for(key, value) in self._settings.items():
            capabilities.settings_schema.fields[key].CopyFrom(value)

        print("Capabilites Sent!")
        return capabilities

    
    def _proto_analysis_data_to_python(self, proto_analysis_data_list) -> list[AnalysisDataEntry]:
        """
        Convert a sequence of proto AnalysisData messages into native AnalysisDataEntry objects.

        Each AnalysisDataEntry contains a list of native Objective instances, fully decoupled from the proto layer.
        """
        analysis_entries: list[AnalysisDataEntry] = []

        for proto_entry in proto_analysis_data_list:
            objectives: list[Objective] = []

            # Each proto_entry.analysis_objectives contains analyzing.Objective messages
            for proto_obj in proto_entry.analysis_objectives:
                objective_metadata = ares_struct_utils.ares_struct_to_dict(
                    proto_obj.objective_metadata
                ) if hasattr(proto_obj, "objective_metadata") else {}

                objectives.append(
                    Objective(
                        objective_name=proto_obj.objective_name,
                        objective_value=ares_value_utils.ares_value_to_py(proto_obj.objective_value),
                        objective_metadata=objective_metadata,
                    )
                )

            analysis_entries.append(AnalysisDataEntry(analysis_objectives=objectives))

        return analysis_entries

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
        
        python_request = PlanRequest(
            parameters=parameters,
            settings=ares_struct_utils.ares_struct_to_dict(request.adapter_settings),
            analysis_results=list(request.analysis_results),
            metadata=RequestMetadata(request.metadata),
            batch_size=request.batch_size,
            previous_plan_status_codes=[
                ares_plan_status_code_utils.proto_plan_status_to_python_plan_status(c)
                for c in request.previous_plan_status_codes
            ],
            analysis_data=self._proto_analysis_data_to_python(request.analysis_data),
        )
        
        #Handle call using the user's custom planning logic 
        response_proto = plan_pb2.PlanningResponse()
        try:
            python_response = self._custom_plan_logic(python_request)
            python_response = self._resolve_awaitable(python_response)

        except Exception as e:
            #Handle errors from user's logic
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error in custom planning logic: {e}")
            response_proto.error_string = f"{e}"
            response_proto.planning_outcome = ares_outcome_enum_pb2.FAILURE
            return response_proto
        
        # This is the depricated response, and should be treated as a single plan. Maybe mention this response is depricated?
        if isinstance(python_response, PlanResponse):
            planned_parameters = []

            for i in range(len(python_response.parameter_names)):
                current_name = python_response.parameter_names[i]
                current_value = python_response.parameter_values[i]

                new_param = PlannedParameter(current_name, current_value)
                planned_parameters.append(new_param)
            
            python_plan = Plan(planned_parameters, python_response.outcome, python_response.error_string, python_response.objective_status)
            response_proto.plans.append(plan_response_utils.python_plan_to_proto_plan(python_plan))

        elif isinstance(python_response, List) and all(isinstance(item, Plan) for item in python_response):
            response_proto.plans.extend(plan_response_utils.python_plan_to_proto_plan(p) for p in python_response)

        else:
            response_proto.error_string = "The returned response from the user planning method was not valid, users must return either a list of plans or a plan response."
            response_proto.planning_outcome = ares_outcome_enum_pb2.FAILURE
        
        print("Sending Plan Response.....")
        return response_proto
    
class AresPlannerService(AresBaseService):
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
        """
        super().__init__(
            service_name=service_name,
            description=service_description,
            version=service_version,
            port=port,
            use_localhost=use_localhost,
            max_message_size=max_message_size
        )
        
        # For backwards compatibility with anyone accessing service_description directly
        self.service_description = service_description

        self._service_wrapper = AresPlannerServiceWrapper(service_name, service_version, service_description, timeout, custom_plan_logic)
        planner_service_grpc.add_AresRemotePlannerServiceServicer_to_server(self._service_wrapper, self.get_server())

    def add_planner_option(self, planner_name: str, planner_description: str, planner_version: str):
        """
        Adds a planner option that is reported to ARES when your services capabilities are requested.
        """
        self._service_wrapper._planner_options.append(planner_pb2.Planner(planner_name=planner_name, description=planner_description, version=planner_version))

    def add_supported_type(self, type: ares_data_models.AresDataType):
        """
        Adds the specified type to the list of value types your planenr service accepts.
        """
        self._service_wrapper._supported_types.append(ares_data_type_utils.python_ares_type_to_proto_ares_type(type))
