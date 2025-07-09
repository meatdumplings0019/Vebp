import json
import shutil
import zipfile
from pathlib import Path
from typing import Optional

from Vebp.Libs.File import FileStream, FolderStream
from Vebp.Libs.File.path import MPath_


class PluginBuilder:
    """插件构建器，专门用于将插件目录打包为 ZIP 格式"""

    def __init__(self, plugin_dir: str) -> None:
        """
        初始化插件构建器

        :param plugin_dir: 插件目录路径
        """
        self.plugin_path = Path(plugin_dir).resolve()
        if not self.plugin_path.exists():
            raise FileNotFoundError(f"🔴 插件目录不存在: {plugin_dir}")
        if not self.plugin_path.is_dir():
            raise ValueError(f"🔴 插件路径必须是目录: {plugin_dir}")

        # 获取插件元数据
        self.meta = self._load_plugin_meta()
        self.plugin_name = self.meta["namespace"]

        # 设置输出目录
        self.output_dir = MPath_.cwd / "vebp-build"
        FolderStream(self.output_dir).create()

        print(f"🔍 找到插件: {self.plugin_name}")
        print(f"📂 插件目录: {self.plugin_path}")
        print(f"📦 输出目录: {self.output_dir}")

    def _load_plugin_meta(self) -> dict:
        """加载插件元数据文件"""
        meta_file_path = self.plugin_path / "vebp-plugin.json"
        meta_file = FileStream(meta_file_path)

        if not meta_file.exists:
            raise FileNotFoundError(f"🔴 插件元数据文件 vebp-plugin.json 不存在")

        try:
            return meta_file.read_json()
        except json.JSONDecodeError:
            raise ValueError("🔴 vebp-plugin.json 格式错误")

    def validate(self) -> bool:
        """验证插件结构是否完整"""
        # 检查必要文件
        required_files = ["vebp-plugin.json", "main.py"]
        plugin_folder = FolderStream(self.plugin_path)
        dir_info = plugin_folder.walk()

        if dir_info is None:
            raise FileNotFoundError(f"🔴 无法访问插件目录: {self.plugin_path}")

        for file in required_files:
            if not any(f.name == file for f in dir_info.files):
                raise FileNotFoundError(f"🔴 插件缺少必要文件: {file}")

        # 验证元数据字段
        required_fields = ["namespace", "author"]
        for field in required_fields:
            if field not in self.meta:
                raise ValueError(f"🔴 vebp-plugin.json 缺少字段: {field}")

        return True

    def _copy_plugin_files(self, target_dir: Path):
        """复制插件文件到目标目录，排除不需要的文件"""
        print(f"📦 准备插件文件...")

        # 使用 FolderStream 遍历插件目录
        plugin_folder = FolderStream(self.plugin_path)
        self._copy_folder_contents(plugin_folder, target_dir)

    def _copy_folder_contents(self, source_folder: FolderStream, target_dir: Path):
        """递归复制文件夹内容"""
        dir_info = source_folder.walk()
        if dir_info is None:
            return

        # 处理当前目录的文件
        for file in dir_info.files:
            file_path = Path(file.path)
            if self._should_exclude(file_path):
                continue

            # 计算相对路径和目标路径
            rel_path = file_path.relative_to(self.plugin_path)
            dest_path = target_dir / rel_path

            # 确保目标目录存在
            FolderStream(dest_path.parent).create()

            # 复制文件
            FileStream.copy(str(file_path), str(dest_path))
            print(f"  ➕ 添加: {rel_path}")

        # 递归处理子目录
        for sub_folder in dir_info.folders:
            folder_path = Path(sub_folder.path)
            if self._should_exclude(folder_path):
                continue

            # 复制子目录内容
            self._copy_folder_contents(sub_folder, target_dir)

    def _create_zip_archive(self, source_dir: Path, zip_path: Path):
        """从源目录创建 ZIP 文件"""
        print(f"📦 创建 ZIP 包: {zip_path.name}")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 使用 FolderStream 遍历源目录
            source_folder = FolderStream(source_dir)
            self._add_folder_to_zip(source_folder, zipf, source_dir)

    def _add_folder_to_zip(self, folder: FolderStream, zipf: zipfile.ZipFile, base_dir: Path):
        """递归添加文件夹内容到 ZIP"""
        dir_info = folder.walk()
        if dir_info is None:
            return

        # 添加文件
        for file in dir_info.files:
            file_path = Path(file.path)
            rel_path = file_path.relative_to(base_dir)
            zipf.write(str(file_path), str(rel_path))

        # 递归添加子目录
        for sub_folder in dir_info.folders:
            self._add_folder_to_zip(sub_folder, zipf, base_dir)

    def _should_exclude(self, path: Path) -> bool:
        """判断是否应该排除文件/目录"""
        # 排除隐藏文件和目录
        if any(part.startswith('.') and part != '.' and part != '..'
               for part in path.parts):
            return True

        # 排除特定文件类型
        exclude_extensions = ['.pyc', '.pyo', '.pyd', '.log', '.tmp', '.bak']
        if path.suffix.lower() in exclude_extensions:
            return True

        # 排除特定目录
        exclude_dirs = ['__pycache__', '.git', '.idea', '.vscode', 'node_modules', 'dist', 'build']
        if any(dir_name in path.parts for dir_name in exclude_dirs):
            return True

        # 排除构建输出目录自身
        if self.output_dir in path.parents:
            return True

        # 排除 macOS 的 DS_Store 文件
        if path.name == '.DS_Store':
            return True

        return False

    def build(self) -> Optional[Path]:
        """构建插件 ZIP 包"""
        self.validate()

        # 创建临时构建目录
        temp_build_dir = self.output_dir / f"_{self.plugin_name}_temp"
        FolderStream(temp_build_dir).create()

        try:
            print(f"🔧 开始构建插件: {self.plugin_name}")

            # 复制文件到临时目录
            self._copy_plugin_files(temp_build_dir)

            # 创建 ZIP 文件
            zip_filename = f"{self.plugin_name}.zip"
            zip_path = self.output_dir / zip_filename
            self._create_zip_archive(temp_build_dir, zip_path)

            print(f"✅ 插件构建完成: {zip_path}")
            return zip_path
        finally:
            # 清理临时目录
            shutil.rmtree(temp_build_dir, ignore_errors=True)