import grpc
import time
from typing import Dict

from ..Utils import ares_struct_utils
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2_grpc as analyzer_service_grpc
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2 as analyzer_service
from ares_datamodel import ares_analyzer_management_service_pb2
from ares_datamodel.connection import connection_status_pb2
from ares_datamodel.analyzing import analysis_pb2
from ares_datamodel import ares_outcome_enum_pb2

class AnalyzerTestClient:
    def __init__(self, port=7083, host='localhost'):
        """
        Initializes an AnalyzerTestClient, useful for testing your PyAres Analyzers.

        Args:
          port (int): The port that your analyzer test client will use to try and reach your service. Defaults to 7083.
          host (str): The host name that the client will use to try and reach your service. Defaults to localhost.
        """
        self.target = f"{host}:{port}"
        self.channel = grpc.insecure_channel(self.target)
        self.stub = analyzer_service_grpc.AresRemoteAnalyzerServiceStub(self.channel)
        print(f"Client connected to {self.target}")

    def get_info(self):
        """Used to test that your Analyzer Service is providing info properly. If successful outputs the name, version and description of your service."""
        print("\n--- Testing GetInfo ---")
        try:
            request = ares_analyzer_management_service_pb2.AnalyzerInfoRequest() 
            response = self.stub.GetInfo(request)
            print(f"Success! Connected to: {response.name} (version {response.version})")
            print(f"Description: {response.description}")

        except grpc.RpcError as e:
            print(f"RPC Failed: {e.code()} - {e.details()}")

    def check_status(self):
        """Checks the status of your Analyzer Service"""
        print("\n--- Testing Connection Status ---")
        try:
            request = connection_status_pb2.ConnectionStatusRequest() 
            response: connection_status_pb2.ConnectionStatus = self.stub.GetConnectionStatus(request)
            print(f"Status: {response.status}")

        except grpc.RpcError as e:
            print(f"RPC Failed: {e.code()} - {e.details()}")

    def run_analysis(self, inputs: Dict, settings: Dict = { }):
        """
        This method is responsible for testing your analysis loop. Simply provide whatever values your analyzer needs to test your logic. 
        
        Args:
          inputs (Dict): The inputs required by your analyzer. Ensure the names (keys) match exactly as your analyzer expects, otherwise analysis will fail
          settings (Dict): A dictionary that contains any specific settings you want to pass to your analyzer. Defaults to an empty dictionary.
        """
        print(f"\n--- Testing Analysis ---")
        if settings is None:
            settings = {}

        try:
            input_struct = ares_struct_utils.create_empty_struct()
            ares_struct_utils.dict_to_ares_struct(inputs, input_struct)
            
            settings_struct = ares_struct_utils.create_empty_struct()
            ares_struct_utils.dict_to_ares_struct(settings, input_struct)

            request = analyzer_service.AnalysisRequest(inputs=input_struct, settings=settings_struct)
            
            start_time = time.perf_counter()
            response: analysis_pb2.Analysis = self.stub.Analyze(request)
            end_time = time.perf_counter()

            if response.analysis_outcome == ares_outcome_enum_pb2.SUCCESS:
                 print(f"Analysis Successful!")
                 print(f"Result: {response.result}")

            elif response.analysis_outcome == ares_outcome_enum_pb2.WARNING:
                print("Analysis was successful, but analyzer emitted a warning.")
                print(f"Result: {response.result}")
                print(f"#### WARNING: {response.error_string} #####")

            else:
                 print(f"Analysis Failed (Outcome: {response.analysis_outcome})")
                 print(f"Error: {response.error_string}")

            elapsed_time = end_time - start_time
            print(f"Analysis request was completed in: {elapsed_time:.4f} seconds")

        except grpc.RpcError as e:
            print(f"RPC Failed: {e.code()} - {e.details()}")