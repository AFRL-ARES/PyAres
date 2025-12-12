import grpc
import time
from ..Utils import plan_request_utils, plan_response_utils
from ..Planning import PlanRequest, PlanResponse
from ..Models import Outcome
from ares_datamodel.planning.remote import ares_remote_planner_service_pb2_grpc as planner_service_grpc
from ares_datamodel import ares_planner_management_service_pb2
from ares_datamodel.connection import connection_status_pb2
from ares_datamodel.planning import plan_pb2
from ares_datamodel import ares_outcome_enum_pb2
from ares_datamodel.connection import connection_info_pb2

class PlannerTestClient:
    def __init__(self, port=7082, host='localhost'):
        """
        Initializes an PlannerTestClient, useful for testing your PyAres Planners.

        Args:
          port (int): The port that your planner test client will use to try and reach your service. Defaults to 7083.
          host (str): The host name that the client will use to try and reach your service. Defaults to localhost.
        """
        self.target = f"{host}:{port}"
        self.channel = grpc.insecure_channel(self.target)
        self.stub = planner_service_grpc.AresRemotePlannerServiceStub(self.channel)
        print(f"Client connected to {self.target}")

    def get_info(self):
        """Used to test that your Planner Service is providing info properly. If successful outputs the name, version and description of your service."""
        print("\n--- Testing GetInfo ---")
        try:
            request = ares_planner_management_service_pb2.PlannerInfoRequest() 
            response: connection_info_pb2.InfoResponse = self.stub.GetInfo(request)
            print(f"Success! Connected to: {response.name} (version {response.version})")
            print(f"Description: {response.description}")

        except grpc.RpcError as e:
            print(f"RPC Failed: {e.code()} - {e.details()}")

    def check_status(self):
        """Checks the status of your Planner Service"""
        print("\n--- Testing Connection Status ---")
        try:
            request = connection_status_pb2.ConnectionStatusRequest() 
            response: connection_status_pb2.ConnectionStatus = self.stub.GetConnectionStatus(request)
            print(f"Status: {response.status}")

        except grpc.RpcError as e:
            print(f"RPC Failed: {e.code()} - {e.details()}")

    def run_planning(self, request: PlanRequest) -> PlanResponse:
        """
        This method is responsible for testing your planning loop. Simply provide whatever values your planner needs to test your logic. 
        
        Args:
          request (PlanRequest): The self crafted plan request. This should include all relevant data for your planner.
        """
        print("\n--- Testing Planning Logic ---")

        try:
            proto_request = plan_request_utils.python_plan_request_to_proto(request)

            start_time = time.perf_counter()
            response: plan_pb2.PlanningResponse = self.stub.Plan(proto_request)
            end_time = time.perf_counter()

            if response.planning_outcome == ares_outcome_enum_pb2.SUCCESS:
                 print(f"Planning Successful!")

            elif response.planning_outcome == ares_outcome_enum_pb2.WARNING:
                print("Planning was successful, but planner emitted a warning.")
                print(f"#### WARNING: {response.error_string} #####")

            else:
                 print(f"Planning Failed (Outcome: {response.planning_outcome})")
                 print(f"Error: {response.error_string}")

            elapsed_time = end_time - start_time
            print(f"Planning request was completed in: {elapsed_time:.4f} seconds")

            return plan_response_utils.proto_plan_response_to_python(response)
        
        except grpc.RpcError as e:
            print(f"RPC Failed: {e.code()} - {e.details()}")
            return PlanResponse([], [], error_string="GRPC FAILURE", planning_outcome=Outcome.FAILURE)


