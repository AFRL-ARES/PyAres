import unittest
from PyAres.Utils import ares_data_type_utils
from PyAres.Models import AresDataType
from ares_datamodel import ares_data_type_pb2
from datetime import datetime, timezone

class TestAresDataTypeUtils(unittest.TestCase):
    def test_determine_python_ares_data_type(self):
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type("string"), AresDataType.STRING)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(True), AresDataType.BOOLEAN)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(123), AresDataType.NUMBER)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(12.34), AresDataType.NUMBER)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(datetime.now(timezone.utc)), AresDataType.TIMESTAMP)
        
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(["a", "b"]), AresDataType.STRING_ARRAY)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type([1, 2.0]), AresDataType.NUMBER_ARRAY)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type([True, False]), AresDataType.LIST)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type([1, "a"]), AresDataType.LIST)

    def test_new_scalar_type_round_trips(self):
        for py_type, proto_type in [
            (AresDataType.TIMESTAMP, ares_data_type_pb2.AresDataType.TIMESTAMP),
            (AresDataType.FLOAT, ares_data_type_pb2.AresDataType.FLOAT),
            (AresDataType.INT, ares_data_type_pb2.AresDataType.INT),
        ]:
            self.assertEqual(ares_data_type_utils.python_ares_type_to_proto_ares_type(py_type), proto_type)
            self.assertEqual(ares_data_type_utils.proto_ares_type_to_python_ares_type(proto_type), py_type)

if __name__ == '__main__':
    unittest.main(verbosity=2)
