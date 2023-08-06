import unittest
import datetime as dt

from p360_interface_bundle.featurestore.post_actions.metadata_adjustment.MetadataDatetimeToStringConverter import (
    MetadataDatetimeToStringConverter,
)


class MetadataDatetimeToStringConverterTest(unittest.TestCase):
    def test_convert(self):
        metadata_datetime_to_string_converter = MetadataDatetimeToStringConverter()

        original_dict = {"items": [{"a": dt.datetime(2022, 2, 11)}], "not_items": True}

        converted_dict = metadata_datetime_to_string_converter.convert(original_dict.copy())

        self.assertIsInstance(converted_dict["items"][0]["a"], str)


if __name__ == "__main__":
    unittest.main()
