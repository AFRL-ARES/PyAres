import unittest
from PyAres.Utils import ares_value_utils

class TestAresValueTypeConversions(unittest.TestCase):
  def test_float_ares_value(self):
    original_float = 0.0
    float_value = ares_value_utils.create_ares_value(original_float)
    self.assertEqual(float_value.number_value, original_float)    

  def test_int_ares_value(self):
    original_int = 0
    int_value = ares_value_utils.create_ares_value(original_int)
    self.assertEqual(int_value.number_value, original_int)

  def test_negative_ares_value(self):
    original_num = -1.0
    negative_value = ares_value_utils.create_ares_value(original_num)
    self.assertEqual(negative_value.number_value, original_num)

  def test_string_ares_value(self):
    original_str = "STRING"
    str_value = ares_value_utils.create_ares_value(original_str)
    self.assertEqual(str_value.string_value, original_str)

  def test_bool_ares_value(self):
    original_bool = True
    bool_value = ares_value_utils.create_ares_value(original_bool)
    self.assertEqual(bool_value.bool_value, original_bool)

  def test_bytes_ares_value(self):
    original_bytes = b"BYTES"
    bytes_value = ares_value_utils.create_ares_value(original_bytes)
    self.assertEqual(bytes_value.bytes_value, original_bytes)

  def test_number_array_ares_value(self):
    original_list = [1.0, 2.0, 3.0]
    list_value = ares_value_utils.create_ares_value(original_list)
    self.assertEqual(list_value.number_array_value.numbers, original_list)

  def test_string_array_ares_value(self):
    original_list = ["one", "two", "three"]
    list_value = ares_value_utils.create_ares_value(original_list)
    self.assertEqual(list_value.string_array_value.strings, original_list)

  def test_bool_array_ares_value(self):
    original_list = [True, False, True]
    list_value = ares_value_utils.create_ares_value(original_list)
    self.assertEqual(list_value.WhichOneof("kind"), "list_value")
    self.assertEqual(len(list_value.list_value.values), 3)
    self.assertEqual(list_value.list_value.values[0].bool_value, True)

  def test_mixed_list_ares_value(self):
    mixed_list = [1, "two"]
    list_value = ares_value_utils.create_ares_value(mixed_list)
    self.assertEqual(list_value.WhichOneof("kind"), "list_value")
    self.assertEqual(len(list_value.list_value.values), 2)
    self.assertEqual(list_value.list_value.values[0].number_value, 1)
    self.assertEqual(list_value.list_value.values[1].string_value, "two")

    # Unsupported type should return null value
    class Unsupported:
      pass
    unsupported = Unsupported()
    null_value = ares_value_utils.create_ares_value(unsupported)
    self.assertEqual(null_value.WhichOneof("kind"), "null_value")

  def test_struct_ares_value(self):
    original_dict = {"key": "value", "nested": {"inner": 123.0}}
    struct_value = ares_value_utils.create_ares_value(original_dict)
    self.assertEqual(struct_value.WhichOneof("kind"), "struct_value")
    self.assertEqual(struct_value.struct_value.fields["key"].string_value, "value")
    self.assertEqual(struct_value.struct_value.fields["nested"].struct_value.fields["inner"].number_value, 123.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)