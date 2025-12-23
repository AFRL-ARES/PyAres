import unittest
from PyAres import AresAnalyzerService, Outcome
from PyAres.Models import ares_data_models
from PyAres.Analyzing.analyzer_models import AnalysisRequest, Analysis
from ares_datamodel.analyzing.remote import ares_remote_analyzer_service_pb2 as analyzer_service
from ares_datamodel.analyzing import analysis_pb2
from ares_datamodel import ares_data_type_pb2, ares_outcome_enum_pb2, ares_data_schema_pb2
from PyAres.Utils import ares_value_utils, ares_struct_utils

class MockGrpcContext:
    def __init__(self):
        self._code = None
        self._details = ""

    def set_code(self, code):
        self._code = code

    def set_details(self, details):
        self._details = details
    
    def abort(self, code, details):
        self._code = code
        self._details = details
        raise Exception(f"gRPC Abort: {code} - {details}")

class TestAresAnalyzerService(unittest.TestCase):
    
    def setUp(self):
        self.captured_request: AnalysisRequest | None = None

        def dummy_analyze(request: AnalysisRequest) -> Analysis:
            self.captured_request = request
            
            # Return a valid Analysis object
            return Analysis(
                result=100.0,
                outcome=Outcome.SUCCESS
            )

        self.analyze_func = dummy_analyze
        self.analyzer_name = "Test Analyzer"
        self.analyzer_version = "1.0.0"
        self.analyzer_desc = "Unit Test Description"
        self.service = None 

    def tearDown(self):
        if hasattr(self, 'service') and self.service:
            try:
                self.service.stop()
            except Exception:
                pass 

    def test_initialization(self):
        """Test metadata and basic startup."""
        self.service = AresAnalyzerService(
            self.analyze_func, self.analyzer_name, self.analyzer_version, 
            description=self.analyzer_desc, port=0
        )
        
        self.assertEqual(self.service.info.name, self.analyzer_name)
        self.assertEqual(self.service.info.version, self.analyzer_version)
        self.assertEqual(self.service.info.description, self.analyzer_desc)

    def test_configuration(self):
        """Test adding settings and analysis parameters (inputs)."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, port=0)

        # Add a Config Setting (e.g., 'Threshold')
        self.service.add_setting("Threshold", ares_data_models.AresDataType.NUMBER, optional=True, constraints=[0.5, 1.0])
        
        # Add an Input Parameter (e.g., 'Image')
        self.service.add_analysis_parameter("InputImage", ares_data_models.AresDataType.STRING, optional=False)

        # Verify internal storage
        self.assertIn("Threshold", self.service._service_wrapper._settings)
        self.assertIn("InputImage", self.service._service_wrapper._analysis_parameters)

        # Verify capabilities response
        caps = self.service._service_wrapper.GetAnalyzerCapabilities(None, None)
        self.assertIn("Threshold", caps.settings_schema.fields)
        self.assertEqual(caps.settings_schema.fields["Threshold"].type, ares_data_type_pb2.AresDataType.NUMBER)

    def test_validation_logic(self):
        """Test that the service correctly validates incoming input schemas."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, port=0)
        
        # Analyzer expects a REQUIRED Number named "Voltage"
        self.service.add_analysis_parameter("Voltage", ares_data_models.AresDataType.NUMBER, optional=False)

        # Case A: Success (Matches Schema)
        req = analyzer_service.ParameterValidationRequest()
        entry = req.input_schema.fields["Voltage"]
        new_schema_entry = ares_data_schema_pb2.SchemaEntry(type=ares_data_type_pb2.AresDataType.NUMBER, optional=False, description="Voltage value", unit="Volts")
        entry.CopyFrom(new_schema_entry)
        resp = self.service._service_wrapper.ValidateInputs(req, None)
        self.assertTrue(resp.success, "Validation should pass for correct schema")

        # Case B: Failure (Wrong Type)
        req_bad_type = analyzer_service.ParameterValidationRequest()
        bad_entry = req_bad_type.input_schema.fields["Voltage"]
        bad_schema_entry = ares_data_schema_pb2.SchemaEntry(type=ares_data_type_pb2.AresDataType.STRING, optional=False, description="Voltage value", unit="Volts")
        bad_entry.CopyFrom(bad_schema_entry)
        resp_bad = self.service._service_wrapper.ValidateInputs(req_bad_type, None)
        self.assertFalse(resp_bad.success, "Validation should fail for type mismatch")
        self.assertIn("Schema Mismatch", resp_bad.messages[0])

        # Case C: Failure (Missing Required Field)
        req_missing = analyzer_service.ParameterValidationRequest()
        # "Voltage" is missing entirely
        resp_missing = self.service._service_wrapper.ValidateInputs(req_missing, None)
        self.assertFalse(resp_missing.success, "Validation should fail for missing required parameter")
        self.assertIn("Schema Missing", resp_missing.messages[0])

    def test_execution_logic(self):
        """Test the Analyze method: Protobuf -> Python -> User Logic -> Protobuf."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, port=0)

        mock_proto_request = analyzer_service.AnalysisRequest()
        
        
        ares_struct_utils.add_value_to_struct(mock_proto_request.inputs, "Voltage", ares_value_utils.create_ares_value(5.5))
        ares_struct_utils.add_value_to_struct(mock_proto_request.settings, "Mode", ares_value_utils.create_ares_value("Fast"))
        mock_proto_request.metadata.experiment_id = "EXP-001"

        response = self.service._service_wrapper.Analyze(mock_proto_request, None)

        # Verify Protobuf -> Python Conversions
        self.assertIsNotNone(self.captured_request, "User function was never called")
        request = self.captured_request
        if request is None: return

        self.assertEqual(request.inputs["Voltage"], 5.5)        
        self.assertEqual(request.settings["Mode"], "Fast")
        self.assertEqual(request.request_metadata.experiment_id, "EXP-001")
        self.assertIsInstance(response, analysis_pb2.Analysis)
        self.assertEqual(response.analysis_outcome, ares_outcome_enum_pb2.SUCCESS)
        self.assertEqual(response.result, 100.0)

    def test_error_handling(self):
        """Test that user exceptions are caught gracefully."""
        
        def failing_analyze(request):
            raise ValueError("Calculation failed")

        self.service = AresAnalyzerService(failing_analyze, "FailBot", "1.0", port=0)
        
        mock_context = MockGrpcContext()
        mock_request = analyzer_service.AnalysisRequest()

        # The service implementation catches the exception and sets the context code
        response = self.service._service_wrapper.Analyze(mock_request, mock_context)

        # Verify gRPC Context was updated
        self.assertIsNotNone(mock_context._code, "Context error code was not set")
        self.assertIn("Calculation failed", mock_context._details)

        # Verify the returned object indicates failure
        self.assertEqual(response.analysis_outcome, ares_outcome_enum_pb2.FAILURE)
        self.assertIn("Calculation failed", response.error_string)

if __name__ == '__main__':
    unittest.main(verbosity=2)