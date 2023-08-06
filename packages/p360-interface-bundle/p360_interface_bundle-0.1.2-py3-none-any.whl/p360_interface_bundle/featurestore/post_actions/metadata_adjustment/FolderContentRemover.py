from pyspark.dbutils import DBUtils
import pathlib
from typing import Union


class FolderContentRemover:
    def __init__(self, dbutils: DBUtils) -> None:
        self.__dbutils = dbutils

    def remove(self, folder_path: Union[str, pathlib.Path]) -> None:
        for file_path in self.__dbutils.fs.ls(folder_path):
            self.__dbutils.fs.rm(file_path.path)
