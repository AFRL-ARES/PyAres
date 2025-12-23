import unittest
from PyAres import AresPlannerService, AresDataType, PlanRequest, PlanResponse, ParameterHistoryItem
from ares_datamodel.planning import plan_pb2
from ares_datamodel import ares_data_type_pb2
from PyAres.Utils import ares_value_utils, ares_struct_utils
from .mock_grpc_context import MockGrpcContext

class TestAresPlannerService(unittest.TestCase):
  def setUp(self):
    def dummy_plan(request: PlanRequest) -> PlanResponse:
      self.captured_request = request
      return PlanResponse(parameter_names=["test_param"], parameter_values=[1.0])

    self.captured_request: PlanRequest | None = None 
    self.plan_func = dummy_plan
    self.planner_name = "Test Planner"
    self.planner_desc = "Unit Test Description"
    self.planner_version = "0.0.1"
    self.service = None

  def tearDown(self):
    if hasattr(self, 'service') and self.service:
        self.service.stop()

  def test_initialization(self):
    """Test that the service initializes with the correct metadata."""
    self.service = AresPlannerService(self.plan_func, self.planner_name, self.planner_desc, self.planner_version, port=0)

    self.assertEqual(self.service.service_name, self.planner_name)
    self.assertEqual(self.service.service_description, self.planner_desc)
    self.assertEqual(self.service.service_version, self.planner_version)

  def test_add_supported_type(self):
    """Test adding a supported data type."""
    self.service = AresPlannerService(self.plan_func, self.planner_name, self.planner_desc, self.planner_version, port=0)
    self.service.add_supported_type(AresDataType.NUMBER)
    self.assertIn(ares_data_type_pb2.AresDataType.NUMBER, self.service._service_wrapper._supported_types)

  def test_add_setting(self):
    """Test adding planner settings."""
    self.service = AresPlannerService(self.plan_func, self.planner_name, self.planner_desc, self.planner_version, port=0)
    self.service.add_setting(setting_name="Test Setting", setting_type=AresDataType.NUMBER, constraints=[0.0, 1.0, 2.0])

    #Ensure setting exists
    self.assertIn("Test Setting", self.service._service_wrapper._settings)

    internal_setting = self.service._service_wrapper._settings["Test Setting"]
    self.assertEqual(len(internal_setting.number_choices.numbers), 3)
    self.assertEqual(internal_setting.type, ares_data_type_pb2.AresDataType.NUMBER)

  def test_execution_logic(self):
    """Test the user-provided plan function is called correctly"""
    self.service = AresPlannerService(self.plan_func, self.planner_name, self.planner_desc, self.planner_version, port=0)

    #Craft out Mock planning request. Load it with data to test all of our conversions.
    mock_request = plan_pb2.PlanningRequest()
    ares_struct_utils.add_value_to_struct(mock_request.adapter_settings, "Test Setting", ares_value_utils.create_ares_value(1.0))

    test_param = plan_pb2.PlanningParameter()
    test_param.parameter_name = "Test Parameter"
    test_param.minimum_value = 0.0
    test_param.maximum_value = 100.0
    test_param.parameter_history.append(plan_pb2.ParameterHistoryInfo(achieved_value=ares_value_utils.create_ares_value(32.0), planned_value=ares_value_utils.create_ares_value(35.0)))
    test_param.data_type = ares_data_type_pb2.AresDataType.NUMBER
    test_param.metadata.metadata_name = "Test Metadata"
    test_param.is_planned = True
    test_param.is_result = True
    test_param.planner_name = "Test Planner"
    test_param.initial_value.number_value = 22.0
    mock_request.planning_parameters.append(test_param)

    response = self.service._service_wrapper.Plan(mock_request, None)
    self.assertIsNotNone(self.captured_request, "ERROR: Plan method failed to run!")
    request = self.captured_request

    if(request is None):
      return
    
    #Assertions to check that our request data successfully translated from protobuf -> python
    self.assertEqual(len(request.parameters), 1)
    param = request.parameters[0]
    self.assertEqual(param.name, "Test Parameter")
    self.assertEqual(param.minimum_value, 0.0)
    self.assertEqual(param.maximum_value, 100.0)
    self.assertEqual(len(param.param_history), 1)
    history = param.param_history[0]
    self.assertEqual(history.achieved_value, 32.0)
    self.assertEqual(history.planned_value, 35.0)
    self.assertEqual(param.data_type, AresDataType.NUMBER)
    self.assertEqual(param.is_planned, True)
    self.assertEqual(param.is_result, True)
    self.assertEqual(param.planner_name, "Test Planner")
    self.assertEqual(param.initial_value, 22.0)
    self.assertIn("Test Setting", request.settings)
    self.assertEqual(request.settings["Test Setting"], 1.0)

    parameter_names = [x.parameter_name for x in response.planned_parameters]
    parameter_values = [ares_value_utils.ares_value_to_py(x.parameter_value) for x in response.planned_parameters]

    self.assertIsInstance(response, plan_pb2.PlanningResponse)
    self.assertEqual(parameter_names, ["test_param"])
    self.assertEqual(parameter_values, [1.0])


  def test_error_handling(self):
    """Test that exceptions in user code are caught and reported to gRPC context."""

    # 1. Define a function that CRASHES
    def failing_plan(request: PlanRequest) -> PlanResponse:
        raise ValueError("Something went wrong in the user calculation!")

    # 2. Initialize service with the failing function
    self.service = AresPlannerService(failing_plan, self.planner_name, self.planner_desc, self.planner_version, port=0)

    # 3. Create the Mock Context
    mock_context = MockGrpcContext()
    mock_request = plan_pb2.PlanningRequest()

    # 4. Execute
    # We wrap this in try/except because our MockContext.abort() raises an exception
    # (simulating real gRPC behavior)
    try:
        self.service._service_wrapper.Plan(mock_request, mock_context)
    except Exception as e:
        # We expect the abort exception here
        pass

    # 5. Assertions
    # Verify that the wrapper actually reported the error to the context
    self.assertIsNotNone(mock_context._code, "The service did not set an error code on the context.")

    # Verify the details contain the user's error message
    self.assertIn("Something went wrong", mock_context._details)

    # Optional: specific status check (depends on how you import grpc)
    # self.assertEqual(mock_context._code, grpc.StatusCode.INTERNAL)

if __name__ == '__main__':
  unittest.main(verbosity=2)