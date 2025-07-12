import json
import os
import shutil

from pathlib import Path
from typing import Iterator, Any, Union, Optional


class FileStream:
    def __init__(self, file_path: str | Path) -> None:
        self._path = Path(os.path.normpath(str(file_path)))

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def suffix(self) -> str:
        return self._path.suffix

    @property
    def exists(self) -> bool:
        return self._path.exists()

    def create(self, value: str = "") -> "FileStream":
        if not self._path.exists():
            self.write(value)

        return self

    def write(self, value: str) -> "FileStream":
        if not self.exists:
            return self

        with open(self._path, 'w') as file:
            file.write(value)
        return self

    def read(self) -> Any:
        if not self.exists: return None

        try:
            with open(self._path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return None

    def is_name(self, name) -> bool:
        return self._path.name == name

    def read_json(self) -> dict:
        with open(self._path, 'r', encoding="utf-8") as file:
            return json.load(file)

    def write_json(self, data: dict) -> None:
        with open(self._path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    @staticmethod
    def abs(source) -> Optional[str]:
        if isinstance(source, FileStream):
            return os.path.abspath(source.path)
        elif isinstance(source, str):
            return os.path.abspath(source)
        elif isinstance(source, Path):
            return str(source)
        else:
            return None

    @staticmethod
    def copy(source, destination) -> Optional["FileStream"]:
        src_path = FileStream.abs(source)

        if not os.path.isfile(src_path):
            return None

        dest_abs = FileStream.abs(destination)

        if isinstance(destination, FolderStream) or os.path.isdir(dest_abs):
            dest_path = os.path.join(dest_abs, os.path.basename(src_path))
        else:
            dest_path = dest_abs

        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        shutil.copy2(src_path, dest_path)

        return FileStream(dest_path)

    def __repr__(self) -> str:
        return f"<FileStream: {self._path}>"


class DirectoryInfo:
    def __init__(self, path, folders, files) -> None:
        self._path = os.path.normpath(path)
        self._folders = folders
        self._files = files

    def __iter__(self) -> Iterator:
        yield self._path
        yield self._folders
        yield self._files

    def __repr__(self) -> str:
        return f"<DirectoryInfo: {self._path}>"

    @property
    def path(self) -> str:
        return self._path

    @property
    def folders(self) -> list["FolderStream"]:
        return self._folders

    @property
    def files(self) -> list[FileStream]:
        return self._files

class FolderStream:
    def __init__(self, folder_path: str | Path) -> None:
        self._path = os.path.normpath(str(folder_path))

    @property
    def path(self) -> str:
        return self._path

    @property
    def exists(self) -> bool:
        return os.path.exists(self._path) and os.path.isdir(self._path)

    def create(self) -> "FolderStream":
        os.makedirs(self._path, exist_ok=True)
        return self

    def delete(self) -> "FolderStream":
        shutil.rmtree(self._path, ignore_errors=True)
        return self

    def walk(self) -> Union[DirectoryInfo, None]:
        if not self.exists: return None

        folders = []
        files = []

        try:
            with os.scandir(self._path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        sub_folder = FolderStream(entry.path)
                        folders.append(sub_folder)
                    elif entry.is_file():
                        files.append(FileStream(entry.path))
        except PermissionError:
            pass

        return DirectoryInfo(self._path, folders, files)

    @staticmethod
    def abs(source) -> Optional[str]:
        if isinstance(source, FolderStream):
            return os.path.abspath(source.path)
        elif isinstance(source, str):
            return os.path.abspath(source)
        elif isinstance(source, Path):
            return str(source)
        else:
            return None

    def find_file(self, file_name):
        file = None
        for files in self.walk().files:
            if files.name == file_name:
                file = files

        return file

    def copy_tree(self, destination: Union[str, Path, "FolderStream"]) -> Optional["FolderStream"]:
        """
        递归复制当前文件夹及其所有内容到目标路径

        参数:
            destination: 目标路径(可以是字符串/Path对象/FolderStream对象)

        返回:
            FolderStream: 复制后的目标文件夹对象
            None: 如果复制失败
        """
        # 获取目标路径的绝对路径
        dest_abs = FolderStream.abs(destination)
        if dest_abs is None:
            return None

        # 确保源文件夹存在
        if not self.exists:
            return None

        try:
            # 创建目标文件夹（如果不存在）
            os.makedirs(dest_abs, exist_ok=True)

            # 遍历当前文件夹内容
            dir_info = self.walk()
            if dir_info is None:
                return None

            # 复制所有文件
            for file_stream in dir_info.files:
                # 构建目标文件路径
                target_file = os.path.join(dest_abs, file_stream.name)
                # 复制文件
                FileStream.copy(file_stream, target_file)

            # 递归复制子文件夹
            for sub_folder in dir_info.folders:
                # 构建目标子文件夹路径
                target_subfolder = os.path.join(dest_abs, os.path.basename(sub_folder.path))
                sub_folder.copy_tree(target_subfolder)

            return FolderStream(dest_abs)
        except Exception as e:
            print(f"复制失败: {str(e)}")
            return None

    def __repr__(self) -> str:
        return f"<FolderStream: {self._path}>"

    def __eq__(self, other) -> bool:
        if isinstance(other, FolderStream):
            return os.path.normpath(self._path) == os.path.normpath(other._path)
        return False

    def __hash__(self) -> int:
        return hash(os.path.normpath(self._path))