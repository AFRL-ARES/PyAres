import unittest
from typing import Dict, Any

# Import Service
from PyAres import AresDeviceService, DeviceSchemaEntry, AresDataType
from PyAres.Device.device_models import DeviceCommandDescriptor

# Import Protobufs
from ares_datamodel.device.remote import ares_remote_device_service_pb2 as device_service
from ares_datamodel.device import device_polling_settings_pb2
from ares_datamodel import ares_data_type_pb2

# Import Utils
from PyAres.Utils import ares_value_utils, ares_struct_utils, ares_data_schema_utils

# --- Mock Context with Streaming Support ---
class MockGrpcContext:
    def __init__(self):
        self._code = None
        self._details = ""
        self._active_count = 3 # Allow loop to run 3 times by default

    def set_code(self, code):
        self._code = code

    def set_details(self, details):
        self._details = details
    
    def abort(self, code, details):
        self._code = code
        self._details = details
        raise Exception(f"gRPC Abort: {code} - {details}")

    def is_active(self):
        # Simulate a client disconnecting after a few iterations
        if self._active_count > 0:
            self._active_count -= 1
            return True
        return False

# --- Main Test Class ---
class TestAresDeviceService(unittest.TestCase):
    
    def setUp(self):
        # 1. Define Dummy Logic
        self.safe_mode_called = False
        def enter_safe_mode():
            self.safe_mode_called = True

        def get_state() -> Dict[str, Any]:
            return {"temperature": 25.5, "status": "idle"}

        self.enter_safe_mode_func = enter_safe_mode
        self.get_state_func = get_state
        
        self.device_name = "Test Device"
        self.device_desc = "Unit Test Description"
        self.device_version = "1.0.0"
        self.service = None 

    def tearDown(self):
        if hasattr(self, 'service') and self.service:
            try:
                self.service.stop()
            except Exception:
                pass 

    def test_initialization(self):
        """Test metadata and startup."""
        self.service = AresDeviceService(
            self.enter_safe_mode_func, self.get_state_func,
            self.device_name, self.device_desc, self.device_version, port=0
        )
        
        self.assertEqual(self.service.device_name, self.device_name)
        self.assertEqual(self.service._service_wrapper.description, self.device_desc)

    def test_settings_management(self):
        """Test adding, retrieving schema, getting values, and setting values."""
        self.service = AresDeviceService(self.enter_safe_mode_func, self.get_state_func, self.device_name, self.device_desc, self.device_version, port=0)

        # Add Setting
        self.service.add_setting("TargetTemp", 100.0, optional=False)
        
        # Verify Schema
        schema_resp = self.service._service_wrapper.GetSettingsSchema(None, None)
        self.assertIn("TargetTemp", schema_resp.schema.fields)
        self.assertEqual(schema_resp.schema.fields["TargetTemp"].type, ares_data_type_pb2.AresDataType.NUMBER)

        # Verify Current Value
        curr_resp = self.service._service_wrapper.GetCurrentSettings(None, None)
        # Assuming AresValue is wrapped in a struct, we check the field
        # Note: Depending on your utils, you might need to decode the AresValue
        val_proto = curr_resp.settings.fields["TargetTemp"]
        self.assertEqual(val_proto.number_value, 100.0)

        # Set New Value (Simulate Client Request)
        set_req = device_service.SetSettingsRequest()
        ares_struct_utils.add_value_to_struct(set_req.settings, "TargetTemp", ares_value_utils.create_ares_value(150.0))
        
        self.service._service_wrapper.SetSettings(set_req, None)
        
        # Verify update
        self.assertEqual(self.service._service_wrapper._current_settings["TargetTemp"].number_value, 150.0)

    def test_command_execution(self):
        """Test registering and executing a command via Protobuf."""
        self.service = AresDeviceService(self.enter_safe_mode_func, self.get_state_func, self.device_name, self.device_desc, self.device_version, port=0)

        def move_axis(axis: str, speed: float) -> Dict[str, Any]:
            return {"moved": True, "axis": axis, "final_speed": speed}

        # Define and register the command
        axis_param_schema = DeviceSchemaEntry(AresDataType.STRING, "The choosen axis to move on", "N/A")
        speed_param_schema = DeviceSchemaEntry(AresDataType.NUMBER, "The speed at which the axis moves", "Speed")
        input_schema = { "axis": axis_param_schema, "speed": speed_param_schema }
        descriptor = DeviceCommandDescriptor("Move Axis", "Moves an axis", input_schema=input_schema, output_schema={})
        self.service.add_new_command(descriptor, move_axis)

        # --- TEST EXECUTION (Happy Path) ---
        req = device_service.ExecuteCommandRequest()
        req.command_name = "Move Axis"
        
        # Add Arguments
        ares_struct_utils.add_value_to_struct(req.arguments, "axis", ares_value_utils.create_ares_value("X"))
        ares_struct_utils.add_value_to_struct(req.arguments, "speed", ares_value_utils.create_ares_value(50.0))

        response = self.service._service_wrapper.ExecuteCommand(req, None)
        
        self.assertTrue(response.success, response.error)
        result_dict = ares_struct_utils.ares_struct_to_dict(response.result)
        self.assertEqual(result_dict["axis"], "X")
        self.assertEqual(result_dict["final_speed"], 50.0)

    def test_command_execution_errors(self):
        """Test failures: missing command, wrong arg counts."""
        self.service = AresDeviceService(self.enter_safe_mode_func, self.get_state_func, self.device_name, self.device_desc, self.device_version, port=0)

        # Register a simple command
        def simple_cmd(arg1): return {}
        desc = DeviceCommandDescriptor("Simple", "Simple Description", {"arg1": DeviceSchemaEntry(AresDataType.NULL)}, {})
        self.service.add_new_command(desc, simple_cmd)

        # 1. Unknown Command
        req_unknown = device_service.ExecuteCommandRequest(command_name="UnknownCmd")
        resp = self.service._service_wrapper.ExecuteCommand(req_unknown, None)
        self.assertFalse(resp.success)
        self.assertIn("Unable to find requested command", resp.error)

        # 2. Argument Count Mismatch
        req_mismatch = device_service.ExecuteCommandRequest(command_name="Simple")
        # Sending 0 args, expects 1
        resp_mis = self.service._service_wrapper.ExecuteCommand(req_mismatch, None)
        self.assertFalse(resp_mis.success)
        self.assertIn("parameter count did not match", resp_mis.error)

    def test_state_streaming(self):
        """Test the generator function for state streaming."""
        self.service = AresDeviceService(self.enter_safe_mode_func, self.get_state_func, self.device_name, self.device_desc, self.device_version, port=0)

        # Setup Request
        req = device_service.DeviceStateStreamRequest()
        req.polling_settings.polling_type = device_polling_settings_pb2.PollingType.INTERVAL
        req.polling_settings.interval_ms = 10 # Short interval for fast test

        # Setup Mock Context to kill loop after 3 iterations
        mock_context = MockGrpcContext()
        mock_context._active_count = 3

        # Call the generator
        response_generator = self.service._service_wrapper.GetStateStream(req, mock_context)

        # Collect results
        responses = list(response_generator)

        # Assertions
        self.assertEqual(len(responses), 3, "Should have yielded exactly 3 responses before context became inactive")
        
        first_resp = responses[0]
        state_dict = ares_struct_utils.ares_struct_to_dict(first_resp.state)
        self.assertEqual(state_dict["temperature"], 25.5)
        self.assertEqual(state_dict["status"], "idle")

    def test_safe_mode(self):
        """Test safe mode trigger."""
        self.service = AresDeviceService(self.enter_safe_mode_func, self.get_state_func, self.device_name, self.device_desc, self.device_version, port=0)

        self.service._service_wrapper.EnterSafeMode(None, None)
        self.assertTrue(self.safe_mode_called, "EnterSafeMode did not trigger the user callback")

if __name__ == '__main__':
    unittest.main(verbosity=2)