import unittest
from PyAres.Utils import ares_struct_utils
from ares_datamodel import ares_struct_pb2

class TestAresStructUtils(unittest.TestCase):
    def test_create_string_struct(self):
        s = ares_struct_utils.create_string_struct("key", "value")
        self.assertEqual(s.fields["key"].string_value, "value")

    def test_create_number_struct(self):
        s = ares_struct_utils.create_number_struct("key", 123)
        self.assertEqual(s.fields["key"].number_value, 123)

    def test_create_bool_struct(self):
        s = ares_struct_utils.create_bool_struct("key", True)
        self.assertEqual(s.fields["key"].bool_value, True)

    def test_create_null_struct(self):
        s = ares_struct_utils.create_null_struct("key")
        self.assertTrue(s.fields["key"].HasField("null_value"))

    def test_create_string_array_struct(self):
        s = ares_struct_utils.create_string_array_struct("key", ["a", "b"])
        self.assertEqual(s.fields["key"].string_array_value.strings, ["a", "b"])

    def test_create_number_array_struct(self):
        s = ares_struct_utils.create_number_array_struct("key", [1, 2.0])
        self.assertEqual(s.fields["key"].number_array_value.numbers, [1, 2.0])

    def test_create_bytes_array_struct(self):
        s = ares_struct_utils.create_bytes_array_struct("key", b"bytes")
        self.assertEqual(s.fields["key"].bytes_value, b"bytes")

    def test_create_ares_struct_inference(self):
        # Test type inference in create_ares_struct
        s_str = ares_struct_utils.create_ares_struct("k", "v")
        self.assertEqual(s_str.fields["k"].string_value, "v")

        s_num = ares_struct_utils.create_ares_struct("k", 10)
        self.assertEqual(s_num.fields["k"].number_value, 10)

        s_bool = ares_struct_utils.create_ares_struct("k", False)
        self.assertEqual(s_bool.fields["k"].bool_value, False)

        s_bytes = ares_struct_utils.create_ares_struct("k", b"123")
        self.assertEqual(s_bytes.fields["k"].bytes_value, b"123")

        s_list_str = ares_struct_utils.create_ares_struct("k", ["a", "b"])
        self.assertEqual(s_list_str.fields["k"].string_array_value.strings, ["a", "b"])

        s_list_num = ares_struct_utils.create_ares_struct("k", [1, 2])
        self.assertEqual(s_list_num.fields["k"].number_array_value.numbers, [1, 2])

        s_list_bool = ares_struct_utils.create_ares_struct("k", [True, False])
        self.assertEqual(s_list_bool.fields["k"].list_value.values[0].bool_value, True)

        s_empty = ares_struct_utils.create_ares_struct("k", [])
        self.assertTrue(s_empty.fields["k"].HasField("null_value"))

    def test_dict_conversions(self):
        py_dict = {
            "str": "val",
            "num": 1.0,
            "bool": True,
            "list": [1, 2]
        }
        struct_pb = ares_struct_pb2.AresStruct()
        ares_struct_utils.dict_to_ares_struct(py_dict, struct_pb)
        
        self.assertEqual(struct_pb.fields["str"].string_value, "val")
        self.assertEqual(struct_pb.fields["num"].number_value, 1.0)
        
        # Round trip
        new_dict = ares_struct_utils.ares_struct_to_dict(struct_pb)
        self.assertEqual(new_dict["str"], "val")
        self.assertEqual(new_dict["num"], 1.0)
        self.assertEqual(new_dict["bool"], True)
        self.assertEqual(new_dict["list"], [1, 2])

if __name__ == '__main__':
    unittest.main(verbosity=2)