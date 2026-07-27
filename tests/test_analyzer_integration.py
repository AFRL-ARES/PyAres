import unittest
import grpc
from google.protobuf.empty_pb2 import Empty
from PyAres import AresAnalyzerService, Outcome, AresDataType
from PyAres.Analyzing.analyzer_models import AnalysisRequest, AnalysisResponse
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2 as analyzer_service
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2_grpc as analyzer_service_grpc
from PyAres.Utils import ares_value_utils, ares_struct_utils

class TestAresAnalyzerIntegration(unittest.TestCase):
    def setUp(self):
        # Define a simple custom analysis logic
        def simple_analyze(request: AnalysisRequest) -> AnalysisResponse:
            val = request.inputs.get("test_val", 0)
            return AnalysisResponse(
                result=float(val) * 2,
                outcome=Outcome.SUCCESS
            )

        # Initialize the service on port 0 (OS assigns a free port)
        self.service = AresAnalyzerService(
            custom_analysis_logic=simple_analyze,
            name="Integration Test Analyzer",
            version="1.0.0",
            port=0
        )
        
        # Find the actual port assigned
        self.port = self.service._port 
        # Note: Since we used port=0, we need to check the server's bound port. 
        # However, AresAnalyzerService currently sets self._port = port.
        # For a real integration test with port=0, we'd need to capture the actual port from the grpc server.
        # To keep this simple and reliable for now, we'll use a fixed high port or 
        # assume the user can modify the service to report the actual bound port.
        
        # For the sake of this implementation, let's force a port we know is likely free
        # or use a fixed one for the test.
        self.service.stop() 
        self.service = AresAnalyzerService(
            custom_analysis_logic=simple_analyze,
            name="Integration Test Analyzer",
            version="1.0.0",
            port=7085 
        )
        self.port = 7085
        self.service.start(wait_for_termination=False)
        
        # Create a gRPC channel and stub
        self.channel = grpc.insecure_channel(f'localhost:{self.port}')
        self.stub = analyzer_service_grpc.AresRemoteAnalyzerServiceStub(self.channel)

    def tearDown(self):
        self.service.stop()
        self.channel.close()

    def test_end_to_end_analysis(self):
        """Verify a real gRPC request flows through the service to the logic and back."""
        # Prepare a protobuf request
        request = analyzer_service.AnalysisRequest()
        ares_struct_utils.add_value_to_struct(
            request.inputs, 
            "test_val", 
            ares_value_utils.create_ares_value(10)
        )
        
        # Call the remote method
        response = self.stub.Analyze(request)
        
        # Verify results
        self.assertEqual(response.result, 20.0)
        self.assertEqual(response.analysis_outcome, 1) # SUCCESS

    def test_remote_capabilities(self):
        """Verify that capabilities are correctly returned over gRPC."""
        # Add a setting to the service
        self.service.add_setting("Sensitivity", AresDataType.INT, optional=True)
        
        # Request capabilities
        # Using None as the request as GetAnalyzerCapabilities typically takes an empty request
        response = self.stub.GetAnalyzerCapabilities(Empty())
        
        self.assertIn("Sensitivity", response.settings_schema.fields)
        self.assertEqual(response.settings_schema.fields["Sensitivity"].type, 16) # NUMBER

if __name__ == '__main__':
    unittest.main(verbosity=2)