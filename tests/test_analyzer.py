import unittest
from PyAres import AresAnalyzerService, Outcome
from PyAres.Models import ares_data_models
from PyAres.Analyzing.analyzer_models import AnalysisRequest, AnalysisResponse, Objective
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

        def dummy_analyze(request: AnalysisRequest) -> AnalysisResponse:
            self.captured_request = request
            
            # Return a valid Analysis object
            return AnalysisResponse(
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

        self.assertEqual(self.service.service_name, self.analyzer_name)
        self.assertEqual(self.service.version, self.analyzer_version)
        self.assertEqual(self.service.description, self.analyzer_desc)

    def test_configuration(self):
        """Test adding settings and analysis parameters (inputs)."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, port=0)

        # Add a Config Setting (e.g., 'Threshold')
        self.service.add_setting("Threshold", ares_data_models.AresDataType.NUMBER, optional=True, constraints=[0.5, 1.0])
        
        # Add an Input Parameter (e.g., 'Image')
        self.service.add_analysis_parameter("InputImage", ares_data_models.AresDataType.STRING, optional=False)

        # Add a Struct Setting
        nested_schema = {
            "SubField": ares_data_models.AresSchemaEntry(
                type=ares_data_models.AresDataType.STRING,
                description="A nested field"
            )
        }
        self.service.add_setting("Complex Setting", ares_data_models.AresDataType.STRUCT, optional=True, struct_schema=nested_schema)

        # Verify internal storage
        self.assertIn("Threshold", self.service._service_wrapper._settings)
        self.assertIn("InputImage", self.service._service_wrapper._analysis_parameters)
        self.assertIn("Complex Setting", self.service._service_wrapper._settings)

        # Verify capabilities response
        caps = self.service._service_wrapper.GetAnalyzerCapabilities(None, None)
        self.assertIn("Threshold", caps.settings_schema.fields)
        self.assertEqual(caps.settings_schema.fields["Threshold"].type, ares_data_type_pb2.AresDataType.NUMBER)

        # Verify Struct in response
        self.assertIn("Complex Setting", caps.settings_schema.fields)
        complex_field = caps.settings_schema.fields["Complex Setting"]
        self.assertEqual(complex_field.type, ares_data_type_pb2.AresDataType.STRUCT)
        self.assertIn("SubField", complex_field.struct_schema.fields)
        self.assertEqual(complex_field.struct_schema.fields["SubField"].type, ares_data_type_pb2.AresDataType.STRING)

    def test_validation_logic(self):
        """Test that the service correctly validates incoming input schemas."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, port=0)
        
        # Analyzer expects a REQUIRED Number named "Voltage"
        self.service.add_analysis_parameter("Voltage", ares_data_models.AresDataType.NUMBER, optional=False)

        # Case A: Success (Matches Schema)
        req = analyzer_service.ParameterValidationRequest()
        entry = req.input_schema.fields["Voltage"]
        new_schema_entry = ares_data_schema_pb2.AresValueSchema(type=ares_data_type_pb2.AresDataType.NUMBER, optional=False, description="Voltage value")
        entry.CopyFrom(new_schema_entry)
        resp = self.service._service_wrapper.ValidateInputs(req, None)
        self.assertTrue(resp.success, "Validation should pass for correct schema")

        # Case B: Failure (Wrong Type)
        req_bad_type = analyzer_service.ParameterValidationRequest()
        bad_entry = req_bad_type.input_schema.fields["Voltage"]
        bad_schema_entry = ares_data_schema_pb2.AresValueSchema(type=ares_data_type_pb2.AresDataType.STRING, optional=False, description="Voltage value")
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
        self.assertIsInstance(response, analysis_pb2.AnalysisResponse)
        self.assertEqual(response.analysis_outcome, ares_outcome_enum_pb2.SUCCESS)
        self.assertEqual(len(response.objectives), 1)

        objective = response.objectives[0]
        self.assertEqual(objective.objective_name, "result")
        self.assertEqual(objective.objective_value.number_value, 100.0)

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

    def test_get_info(self):
        """Test GetInfo returns correct metadata."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, description=self.analyzer_desc, port=0)
        response = self.service._service_wrapper.GetInfo(None, None)
        self.assertEqual(response.name, self.analyzer_name)
        self.assertEqual(response.version, self.analyzer_version)
        self.assertEqual(response.description, self.analyzer_desc)

    def test_get_state(self):
        """Test GetState returns ACTIVE."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, port=0)
        response = self.service._service_wrapper.GetState(None, None)
        from ares_datamodel.connection import connection_state_pb2
        self.assertEqual(response.state, connection_state_pb2.State.ACTIVE)

    def test_get_analysis_parameters(self):
        """Test GetAnalysisParameters returns correctly configured parameters."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, port=0)
        self.service.add_analysis_parameter("Voltage", ares_data_models.AresDataType.NUMBER, optional=False)
        
        response = self.service._service_wrapper.GetAnalysisParameters(None, None)
        self.assertIn("Voltage", response.parameter_schema.fields)
        self.assertEqual(response.parameter_schema.fields["Voltage"].type, ares_data_type_pb2.AresDataType.NUMBER)

    def test_get_connection_status(self):
        """Test GetConnectionStatus returns CONNECTED."""
        self.service = AresAnalyzerService(self.analyze_func, self.analyzer_name, self.analyzer_version, port=0)
        response = self.service._service_wrapper.GetConnectionStatus(None, None)
        from ares_datamodel.connection import connection_status_pb2
        self.assertEqual(response.status, connection_status_pb2.AresStatus.CONNECTED)

    def test_async_execution_logic(self):
        """Test that the service can handle an awaitable analyze function."""
        import asyncio
        
        async def async_analyze(request):
            return AnalysisResponse(result=200.0, outcome=Outcome.SUCCESS)
            
        self.service = AresAnalyzerService(async_analyze, self.analyzer_name, self.analyzer_version, port=0)
        mock_request = analyzer_service.AnalysisRequest()
        
        # This will likely fail currently due to the bug identified in analysis_service.py
        response = self.service._service_wrapper.Analyze(mock_request, None)
        self.assertEqual(len(response.objectives), 1)
        self.assertEqual(response.analysis_outcome, ares_outcome_enum_pb2.SUCCESS)

        objective = response.objectives[0]
        self.assertEqual(objective.objective_name, "result")
        self.assertEqual(objective.objective_value.number_value, 200.0)


    def test_analyze_explicit_objectives_and_metadata(self):
        """Test that explicit objectives and metadata are converted correctly."""

        def objective_analyze(request: AnalysisRequest) -> AnalysisResponse:
            return AnalysisResponse(
                outcome=Outcome.SUCCESS,
                error_string="",
                objectives=[
                    Objective(
                        objective_name="score",
                        objective_value=42.0,
                        objective_metadata={"tag": "primary", "run": 1},
                    ),
                    Objective(
                        objective_name="label",
                        objective_value="PASS",
                        objective_metadata={},
                    ),
                ],
            )

        self.service = AresAnalyzerService(
            objective_analyze,
            self.analyzer_name,
            self.analyzer_version,
            port=0,
        )

        mock_request = analyzer_service.AnalysisRequest()
        
        ares_struct_utils.dict_to_ares_struct({"Voltage": 5.5}, mock_request.inputs)
        ares_struct_utils.dict_to_ares_struct({"Mode": "Fast"},  mock_request.settings)

        response = self.service._service_wrapper.Analyze(mock_request, MockGrpcContext())

        self.assertIsInstance(response, analysis_pb2.AnalysisResponse)
        self.assertEqual(response.analysis_outcome, ares_outcome_enum_pb2.SUCCESS)
        self.assertEqual(len(response.objectives), 2)

        score_obj = response.objectives[0]
        self.assertEqual(score_obj.objective_name, "score")
        self.assertEqual(score_obj.objective_value.number_value, 42.0)
        self.assertIn("tag", score_obj.objective_metadata.fields)
        self.assertIn("run", score_obj.objective_metadata.fields)
        self.assertEqual(score_obj.objective_metadata.fields["tag"].string_value, "primary")
        self.assertEqual(score_obj.objective_metadata.fields["run"].number_value, 1)

        label_obj = response.objectives[1]
        self.assertEqual(label_obj.objective_name, "label")
        self.assertEqual(label_obj.objective_value.string_value, "PASS")
        self.assertEqual(len(label_obj.objective_metadata.fields), 0)

    def test_analyze_invalid_return_type(self):
        """Test that an invalid return type yields a FAILURE response."""

        def bad_analyze(request: AnalysisRequest):
            return None

        self.service = AresAnalyzerService(
            bad_analyze, "BadAnalyzer", "1.0", port=0
        )

        mock_context = MockGrpcContext()
        mock_request = analyzer_service.AnalysisRequest()

        response = self.service._service_wrapper.Analyze(mock_request, mock_context)

        self.assertIsInstance(response, analysis_pb2.AnalysisResponse)
        self.assertEqual(response.analysis_outcome, ares_outcome_enum_pb2.FAILURE)
        self.assertIn("invalid type", response.error_string)

    def test_analyze_failure_outcome_and_error_string(self):
        """Test that failure outcome and error_string propagate correctly."""

        def failure_analyze(request: AnalysisRequest) -> AnalysisResponse:
            return AnalysisResponse(
                outcome=Outcome.FAILURE,
                error_string="Domain-specific failure",
                objectives=[],
            )

        self.service = AresAnalyzerService(
            failure_analyze, "FailureAnalyzer", "1.0", port=0
        )

        mock_request = analyzer_service.AnalysisRequest()
        response = self.service._service_wrapper.Analyze(
            mock_request, MockGrpcContext()
        )

        self.assertIsInstance(response, analysis_pb2.AnalysisResponse)
        self.assertEqual(response.analysis_outcome, ares_outcome_enum_pb2.FAILURE)
        self.assertEqual(response.error_string, "Domain-specific failure")
        self.assertEqual(len(response.objectives), 0)

    def test_deprecated_result_usage_still_working(self):
        """Test that deprecated result usage still produces a 'result' objective."""

        def deprecated_analyze(request: AnalysisRequest) -> AnalysisResponse:
            return AnalysisResponse(result=123.0, outcome=Outcome.SUCCESS)

        self.service = AresAnalyzerService(
            deprecated_analyze, "DeprecatedAnalyzer", "1.0", port=0
        )

        mock_request = analyzer_service.AnalysisRequest()
        response = self.service._service_wrapper.Analyze(
            mock_request, MockGrpcContext()
        )

        self.assertIsInstance(response, analysis_pb2.AnalysisResponse)
        self.assertEqual(response.analysis_outcome, ares_outcome_enum_pb2.SUCCESS)
        self.assertEqual(len(response.objectives), 1)

        objective = response.objectives[0]
        self.assertEqual(objective.objective_name, "result")
        self.assertEqual(objective.objective_value.number_value, 123.0)
 
if __name__ == '__main__':
    unittest.main(verbosity=2)
