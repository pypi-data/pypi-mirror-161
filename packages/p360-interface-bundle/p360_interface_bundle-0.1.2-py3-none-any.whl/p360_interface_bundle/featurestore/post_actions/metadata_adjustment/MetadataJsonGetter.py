from box import Box
import itertools
from typing import List
from pyspark.sql import types as t, functions as f
from pyspark.sql import DataFrame
from featurestorebundle.feature.FeatureStore import FeatureStore
from featurestorebundle.entity.EntityGetter import EntityGetter

from p360_interface_bundle.featurestore.post_actions.metadata_adjustment.MetadataDatetimeToStringConverter import (
    MetadataDatetimeToStringConverter,
)


class MetadataJsonGetter:
    def __init__(
        self,
        metadata_datetime_to_string_converter: MetadataDatetimeToStringConverter,
        feature_store: FeatureStore,
        entity_getter: EntityGetter,
        general_mapping: Box,
        category_mapping: Box,
    ) -> None:
        self.__metadata_datetime_to_string_converter = metadata_datetime_to_string_converter
        self.__feature_store = feature_store

        if category_mapping:
            self.__category_mapping = dict(
                itertools.chain(
                    *[list(itertools.product(value, [key])) for key, value in zip(category_mapping.keys(), category_mapping.values())]
                )
            )
        else:
            self.__category_mapping = {}
        self.__general_mapping = general_mapping.to_dict() if general_mapping else {}
        self.__entity = entity_getter.get()

    def __get_metadata_with_subcategory(self):
        metadata = self.__feature_store.get_metadata(entity_name=self.__entity.name)

        return (
            metadata.filter(f.col("entity") == self.__entity.name)
            .withColumn("subcategory", f.col("category"))
            .replace(to_replace=self.__category_mapping, subset=["category"])
        )

    def __rename_metadata(self, df: DataFrame, row: t.Row, general_mapping_dict: dict) -> dict:
        result = {
            (general_mapping_dict[col] if col in general_mapping_dict else col): (row[col] if row[col] is not None else "")
            for col in df.columns
        }
        result["description"] = ""

        return result

    def get_jsons(self) -> List[dict]:
        metadata_with_subcategory = self.__get_metadata_with_subcategory()

        collected_data = metadata_with_subcategory.collect()
        category_list = [row.category for row in (metadata_with_subcategory.select("category").distinct().collect())]
        all_categories = []
        for category in category_list:
            category_dict = {
                "title": category,
                "category": category,
                "subcategory": "",
                "author": "PX",
            }

            items = []
            for row in collected_data:
                if row["category"] == category:
                    items.append(self.__rename_metadata(metadata_with_subcategory, row, self.__general_mapping))
                    category_dict["items"] = items

            category_dict = self.__metadata_datetime_to_string_converter.convert(category_dict)
            all_categories.append(category_dict)

        return all_categories
