import unittest
from PyAres.Utils import ares_data_schema_utils
from PyAres.Models import AresDataType, AresSchemaEntry
from ares_datamodel import ares_data_type_pb2

class TestAresDataSchemaUtils(unittest.TestCase):
    def test_create_simple_entry(self):
        entry = ares_data_schema_utils.create_settings_schema_entry(
            AresDataType.STRING, 
            optional=True, 
            choices=[]
        )
        self.assertEqual(entry.type, ares_data_type_pb2.AresDataType.STRING)
        self.assertTrue(entry.optional)

    def test_create_entry_with_string_choices(self):
        choices = ["A", "B"]
        entry = ares_data_schema_utils.create_settings_schema_entry(
            AresDataType.STRING,
            optional=False,
            choices=choices
        )
        self.assertEqual(entry.string_choices.strings, choices)

    def test_create_entry_with_number_choices(self):
        choices = [1, 2.0]
        entry = ares_data_schema_utils.create_settings_schema_entry(
            AresDataType.NUMBER,
            optional=False,
            choices=choices
        )
        self.assertEqual(entry.number_choices.numbers, choices)

    def test_create_entry_with_mixed_choices(self):
        # Should result in no choices being set if types are mixed
        choices = ["A", 1]
        entry = ares_data_schema_utils.create_settings_schema_entry(
            AresDataType.STRING,
            optional=False,
            choices=choices
        )

        self.assertEqual(len(entry.string_choices.strings), 0)
        self.assertEqual(len(entry.number_choices.numbers), 0)

    def test_convert_ares_schema_entry_to_proto(self):
        py_entry = AresSchemaEntry(
            type=AresDataType.NUMBER,
            optional=True,
            description="Test Desc",
            unit="m/s",
            choices=[1.0, 2.0]
        )
        proto = ares_data_schema_utils.convert_ares_schema_entry_to_proto(py_entry)
        self.assertEqual(proto.type, ares_data_type_pb2.AresDataType.NUMBER)
        self.assertTrue(proto.optional)
        self.assertEqual(proto.description, "Test Desc")
        self.assertEqual(proto.unit, "m/s")
        self.assertEqual(proto.number_choices.numbers, [1.0, 2.0])

    def test_nested_struct_schema(self):
        nested_field = AresSchemaEntry(type=AresDataType.STRING, description="Inner")
        struct_entry = AresSchemaEntry(
            type=AresDataType.STRUCT,
            struct_schema={"inner_key": nested_field}
        )
        
        proto = ares_data_schema_utils.convert_ares_schema_entry_to_proto(struct_entry)
        self.assertEqual(proto.type, ares_data_type_pb2.AresDataType.STRUCT)
        self.assertIn("inner_key", proto.struct_schema.fields)
        
        inner_proto = proto.struct_schema.fields["inner_key"]
        self.assertEqual(inner_proto.type, ares_data_type_pb2.AresDataType.STRING)
        self.assertEqual(inner_proto.description, "Inner")

if __name__ == '__main__':
    unittest.main(verbosity=2)