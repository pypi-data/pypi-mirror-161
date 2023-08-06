from featurestorebundle.orchestration.PostActionInterface import PostActionInterface

from p360_interface_bundle.featurestore.post_actions.metadata_adjustment.MetadataJsonGetter import MetadataJsonGetter
from p360_interface_bundle.featurestore.post_actions.metadata_adjustment.MetadataWriter import MetadataWriter
from p360_interface_bundle.featurestore.post_actions.metadata_adjustment.FolderContentRemover import FolderContentRemover


class CreateMetadataJsonFiles(PostActionInterface):
    def __init__(
        self,
        metadata_json_getter: MetadataJsonGetter,
        metadata_writer: MetadataWriter,
        folder_content_remover: FolderContentRemover,
        export_path: str,
    ) -> None:
        self.__metadata_json_getter = metadata_json_getter
        self.__metadata_writer = metadata_writer
        self.__folder_content_remover = folder_content_remover
        self.__export_path = export_path

    def run(self):
        metadata_jsons = self.__metadata_json_getter.get_jsons()
        self.__folder_content_remover.remove(folder_path=self.__export_path)
        self.__metadata_writer.write(metadata_jsons=metadata_jsons, export_path=self.__export_path)
