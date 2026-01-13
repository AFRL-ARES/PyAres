import unittest
from PyAres.Utils import ares_data_type_utils
from PyAres.Models import AresDataType

class TestAresDataTypeUtils(unittest.TestCase):
    def test_determine_python_ares_data_type(self):
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type("string"), AresDataType.STRING)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(True), AresDataType.BOOLEAN)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(123), AresDataType.NUMBER)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(12.34), AresDataType.NUMBER)
        
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type(["a", "b"]), AresDataType.STRING_ARRAY)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type([1, 2.0]), AresDataType.NUMBER_ARRAY)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type([True, False]), AresDataType.LIST)
        self.assertEqual(ares_data_type_utils.determine_python_ares_data_type([1, "a"]), AresDataType.LIST)

if __name__ == '__main__':
    unittest.main(verbosity=2)