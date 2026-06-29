import unittest

from ares_datamodel import ares_data_type_pb2
from ares_datamodel.planning import plan_pb2

from PyAres.Models import AresDataType, PlanStatusCode, RequestMetadata
from PyAres.Planning import PlanRequest
from PyAres.Utils import ares_plan_status_code_utils, planning_param_utils


class TestBatchPlanningRegressions(unittest.TestCase):
    def test_convert_proto_planning_parameter_to_python(self):
        proto_parameter = plan_pb2.PlanningParameter(
            parameter_name="temperature",
            minimum_value=20.0,
            maximum_value=100.0,
            data_type=ares_data_type_pb2.AresDataType.NUMBER,
            is_planned=True,
            is_result=False,
            planner_name="Test Planner",
            initial_value=None)
        proto_parameter.initial_value.number_value = 25.0

        parameter = planning_param_utils.convert_proto_plan_param_to_python(proto_parameter)

        self.assertEqual(parameter.name, "temperature")
        self.assertEqual(parameter.minimum_value, 20.0)
        self.assertEqual(parameter.maximum_value, 100.0)
        self.assertEqual(parameter.data_type, AresDataType.NUMBER)
        self.assertTrue(parameter.is_planned)
        self.assertFalse(parameter.is_result)
        self.assertEqual(parameter.planner_name, "Test Planner")
        self.assertEqual(parameter.initial_value, 25.0)

    def test_python_status_can_be_added_to_protobuf_request(self):
        status = ares_plan_status_code_utils.python_plan_status_to_proto_plan_status(PlanStatusCode.PLAN_ACCEPTED)
        request = plan_pb2.PlanningRequest()

        request.previous_plan_status_codes.append(status)

        self.assertEqual(
            request.previous_plan_status_codes[0],
            plan_pb2.PLAN_ACCEPTED,
        )

    def test_fourth_positional_argument_remains_metadata(self):
        metadata = RequestMetadata.from_default_values()

        request = PlanRequest([], {}, [], metadata)

        self.assertIs(request.request_metadata, metadata)
        self.assertEqual(request.batch_size, 1)

    def test_default_status_code_lists_are_independent(self):
        first_request = PlanRequest([], {}, [])
        second_request = PlanRequest([], {}, [])

        first_request.previous_plan_status_codes.append(PlanStatusCode.PLAN_ACCEPTED)

        self.assertEqual(second_request.previous_plan_status_codes, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
