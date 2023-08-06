import os
import json
import pathlib
from typing import Union, List
from pyspark.dbutils import DBUtils


class MetadataWriter:
    def __init__(self, dbutils: DBUtils) -> None:
        self.__dbutils = dbutils

    def write(self, metadata_jsons: List[dict], export_path: Union[str, pathlib.Path]) -> None:
        for dict_category in metadata_jsons:
            self.__write_to_dbfs(content=dict_category)
            self.__copy_to_external_storage(export_path=export_path, filename=f"{dict_category['title']}.json")
            self.__remove_from_dbfs(filename=f"{dict_category['title']}.json")

    def __write_to_dbfs(self, content: dict) -> None:
        with open(os.path.join("/dbfs/tmp", f"{content['title']}.json"), "w", encoding="utf-8") as tmpfile:
            tmpfile.write(json.dumps(content))

    def __copy_to_external_storage(self, export_path: Union[str, pathlib.Path], filename: str) -> None:
        self.__dbutils.fs.cp(os.path.join("dbfs:/tmp", filename), os.path.join(export_path, filename))

    def __remove_from_dbfs(self, filename: str) -> None:
        self.__dbutils.fs.rm(os.path.join("dbfs:/tmp", filename))
