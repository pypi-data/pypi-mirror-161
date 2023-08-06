import datetime as dt


class MetadataDatetimeToStringConverter:
    def convert(self, metadata: dict) -> dict:
        for item in metadata["items"]:
            item = self.__convert_item(item)

        return metadata

    def __convert_item(self, item: dict) -> dict:
        for key, val in item.items():
            if isinstance(val, dt.datetime):
                item[key] = str(val)

        return item
