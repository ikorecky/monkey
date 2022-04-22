import shutil
from pathlib import Path
from typing import BinaryIO

from monkey_island.cc.server_utils.file_utils import create_secure_directory

from . import IFileStorageService


class DirectoryFileStorageService(IFileStorageService):
    """
    A implementation of IFileStorageService that reads and writes files from/to the local
    filesystem.
    """

    def __init__(self, storage_directory: Path):
        """
        :param storage_directory: A Path object representing the directory where files will be
                                  stored. If the directory does not exist, it will be created.
        """
        if storage_directory.exists() and not storage_directory.is_dir():
            raise ValueError(f"The provided path must point to a directory: {storage_directory}")

        if not storage_directory.exists():
            create_secure_directory(storage_directory)

        self._storage_directory = storage_directory

    def save_file(self, unsafe_file_name: str, file_contents: BinaryIO):
        safe_file_path = self._get_safe_file_path(unsafe_file_name)

        with open(safe_file_path, "wb") as dest:
            shutil.copyfileobj(file_contents, dest)

    def open_file(self, unsafe_file_name: str) -> BinaryIO:
        safe_file_path = self._get_safe_file_path(unsafe_file_name)
        return open(safe_file_path, "rb")

    def delete_file(self, unsafe_file_name: str):
        safe_file_path = self._get_safe_file_path(unsafe_file_name)

        safe_file_path.unlink()

    def _get_safe_file_path(self, unsafe_file_name: str):
        # Remove any path information from the file name.
        safe_file_name = Path(unsafe_file_name).resolve().name

        # TODO: Add super paranoid check

        return self._storage_directory / safe_file_name

    def delete_all_files(self):
        for file in self._storage_directory.iterdir():
            file.unlink()
