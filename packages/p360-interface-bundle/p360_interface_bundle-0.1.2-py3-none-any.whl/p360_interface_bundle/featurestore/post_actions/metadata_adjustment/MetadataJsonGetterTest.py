import unittest
from unittest.mock import patch, Mock
from pysparkbundle.test.PySparkTestCase import PySparkTestCase
from box import Box

from p360_interface_bundle.featurestore.post_actions.metadata_adjustment.MetadataJsonGetter import MetadataJsonGetter


class MetadataJsonGetterTest(PySparkTestCase):
    @patch("featurestorebundle.feature.FeatureStore.FeatureStore")
    @patch("featurestorebundle.entity.EntityGetter.EntityGetter")
    def test___get_metadata_with_subcategory(self, mock_entity_getter, mock_feature_store):
        mock_metadata_datetime_to_string_converter = Mock()
        mock_feature_store.get_metadata.return_value = self.spark.createDataFrame(
            [["client", "original_category_value"]], ["entity", "category"]
        )
        mock_entity_getter.get().name = "client"

        metadata_json_getter = MetadataJsonGetter(
            feature_store=mock_feature_store,
            entity_getter=mock_entity_getter,
            metadata_datetime_to_string_converter=mock_metadata_datetime_to_string_converter,
            category_mapping=Box.from_json('{"introduced_category_value": ["original_category_value"]}'),
            general_mapping=Box.from_json("{}"),
        )

        df_expected = self.spark.createDataFrame(
            [["client", "original_category_value", "introduced_category_value"]], ["entity", "subcategory", "category"]
        )

        self.compare_dataframes(
            df_expected,
            metadata_json_getter._MetadataJsonGetter__get_metadata_with_subcategory(),  # pylint: disable=W0212
            sort_keys=["entity"],
        )


if __name__ == "__main__":
    unittest.main()
